// AI-assistent-server voor Kanalo en TableJoy, met Grok (xAI).
// Start: node server.mjs   (Node 20+, geen dependencies)
//
// Omgevingsvariabelen (zie .env.example). De xAI-sleutel blijft op de server;
// de apps en de werkvloer krijgen hem nooit te zien.

import http from "node:http";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { toolsFor } from "./lib/tools.mjs";

const DIR = path.dirname(fileURLToPath(import.meta.url));
const env = (k, d = "") => (process.env[k] || d).trim();

const PORT = +env("PORT", "8787");
const XAI_BASE_URL = env("XAI_BASE_URL", "https://api.x.ai/v1");
const XAI_MODEL = env("XAI_MODEL", "grok-4");
const DATA_DIR = env("DATA_DIR", path.join(DIR, "data"));
const ALLOWED_ORIGINS = env("ALLOWED_ORIGINS").split(",").map((s) => s.trim()).filter(Boolean);
const MAX_TOOL_ROUNDS = 5;

// ---------- Apps en hun regels ----------

const KANALO_RULES = `Belangrijke regels voor Kanalo (altijd, in elke taal):
- Kanalo is alleen een speler. Gebruikers voegen zelf hun eigen M3U- of Xtream-playlist toe van een aanbieder die ze zelf kiezen.
- Kanalo levert geen zenders, films, series of sport. Beloof dus nooit gratis zenders, films of sport, en wek die indruk ook niet.
- Noem geen bronnen, sites of aanbieders van playlists en geen echte zendernamen. Help niet bij het vinden van illegale streams.
- Vraagt iemand naar gratis content: leg vriendelijk uit dat Kanalo alleen een speler is en dat de inhoud van hun eigen playlist komt.`;

const APPS = {
  kanalo: {
    name: "Kanalo",
    about: "Kanalo is een IPTV-speler voor iPhone, iPad, Apple TV en Mac. Er is een Pro-abonnement met proefperiode via de App Store.",
    rules: KANALO_RULES,
  },
  tablejoy: {
    name: "TableJoy",
    about: "TableJoy is een app voor restaurants: reserveringen, tafels, wachtlijst, gastcommunicatie en reviews.",
    rules: "",
  },
};

function systemPrompt(app, scope, agent) {
  const a = APPS[app];
  const who = agent?.name ? `Je bent ${agent.name}, AI-assistent voor ${a.name}${agent.role ? ` met de rol "${agent.role}"` : ""}.` : `Je bent de AI-assistent van ${a.name}.`;
  const audience = scope === "owner"
    ? "Je werkt voor de eigenaar. Lever direct bruikbaar resultaat (concept, lijst, samenvatting), kort en zonder inleiding."
    : "Je helpt een gebruiker in de app. Wees kort, vriendelijk en concreet. Je kunt alleen gegevens van deze gebruiker zelf inzien.";
  return [
    who, a.about, audience,
    "Gebruik je tools om echte gegevens op te halen voordat je iets over cijfers, reserveringen, bugs, reviews of abonnementen zegt. Verzin nooit gegevens.",
    "Heeft een toolresultaat demo:true, zeg dan duidelijk dat het voorbeelddata is en geen echte gegevens.",
    "Je kunt niets versturen of wijzigen; je levert concepten die de eigenaar zelf verstuurt.",
    "Antwoord in de taal van de vraag (standaard Nederlands).",
    `Vandaag is ${new Date().toLocaleDateString("nl-NL", { timeZone: "Europe/Amsterdam", weekday: "long", year: "numeric", month: "long", day: "numeric" })} (Europe/Amsterdam).`,
    a.rules,
  ].filter(Boolean).join("\n\n");
}

// Laatste vangnet voor Kanalo: een antwoord dat gratis content belooft gaat niet de deur uit.
const FREE_PROMISE = /\b(gratis|free|kostenlos|kostenlose[nr]?|gratuit[es]?|gratuit[oa]s?|for nothing)\b[^.!?\n]{0,50}\b(zender|zenders|kanalen|kanaal|channels?|tv|films?|movies?|sport|voetbal|football|soccer|serie[s]?|series|sender|chaînes?|canales?|canali|filme)\b/i;
const NEGATION = /\b(geen|niet|nooit|no|not|never|without|kein\w*|nicht|pas|aucun\w*|ni|nunca|non|nessun\w*|zonder)\b/i;

export function promisesFreeContent(text) {
  for (const sentence of String(text).split(/(?<=[.!?\n])/)) {
    if (FREE_PROMISE.test(sentence) && !NEGATION.test(sentence)) return true;
  }
  return false;
}

const KANALO_SAFE_REPLY = "Kanalo is alleen een speler: je voegt zelf je eigen M3U- of Xtream-playlist toe van een aanbieder die je zelf kiest. Kanalo levert zelf geen zenders, films of sport. Wil je hulp bij het toevoegen van je playlist?";

// ---------- Tokens ----------

function tokenTable() {
  const t = [];
  if (env("TABLEJOY_TOKEN")) t.push({ token: env("TABLEJOY_TOKEN"), app: "tablejoy", scope: "app" });
  if (env("KANALO_TOKEN")) t.push({ token: env("KANALO_TOKEN"), app: "kanalo", scope: "app" });
  if (env("OWNER_TOKEN")) t.push({ token: env("OWNER_TOKEN"), app: "*", scope: "owner" });
  return t;
}

function safeEqual(a, b) {
  const x = crypto.createHash("sha256").update(a).digest();
  const y = crypto.createHash("sha256").update(b).digest();
  return crypto.timingSafeEqual(x, y);
}

function authenticate(req) {
  const m = /^Bearer\s+(.+)$/i.exec(req.headers.authorization || "");
  if (!m) return null;
  const given = m[1].trim();
  return tokenTable().find((t) => safeEqual(t.token, given)) || null;
}

// ---------- Opslag: taken en logboek per app (JSON-bestand) ----------

const stores = {};
function store(app) {
  if (!stores[app]) {
    const file = path.join(DATA_DIR, `werkvloer-${app}.json`);
    let data = { tasks: [], log: [] };
    try { data = JSON.parse(fs.readFileSync(file, "utf8")); } catch {}
    stores[app] = { file, data, timer: null };
  }
  return stores[app];
}
function persist(app) {
  const s = store(app);
  clearTimeout(s.timer);
  s.timer = setTimeout(() => {
    fs.mkdirSync(DATA_DIR, { recursive: true });
    fs.writeFileSync(s.file + ".tmp", JSON.stringify(s.data));
    fs.renameSync(s.file + ".tmp", s.file);
  }, 200);
}
function addLog(app, agent, text) {
  const s = store(app);
  s.data.log.unshift({ at: new Date().toISOString(), agent: agent || null, text });
  s.data.log.length = Math.min(s.data.log.length, 200);
  persist(app);
}

// ---------- xAI ----------

async function xai(messages, tools) {
  const body = { model: XAI_MODEL, messages, temperature: 0.4 };
  if (tools.length) { body.tools = tools; body.tool_choice = "auto"; }
  const res = await fetch(`${XAI_BASE_URL}/chat/completions`, {
    method: "POST",
    headers: { "content-type": "application/json", authorization: `Bearer ${env("XAI_API_KEY", "proxy-injected")}` },
    body: JSON.stringify(body),
    signal: AbortSignal.timeout(90000),
  });
  const j = await res.json().catch(() => ({}));
  if (!res.ok) {
    const err = new Error(`xAI gaf HTTP ${res.status}${j.error ? `: ${typeof j.error === "string" ? j.error : j.error.message}` : ""}`);
    err.status = res.status === 429 ? 429 : 502;
    throw err;
  }
  return j;
}

const TOOL_LABELS = {
  bugrapporten: "las de bugrapporten", bugrapport: "opende een bugrapport", reviews: "las de App Store-reviews",
  abonnementen: "bekeek de abonnementen", app_store_meldingen: "bekeek de App Store-meldingen",
  mijn_abonnement: "bekeek het abonnement", mijn_bugrapporten: "bekeek de eigen bugrapporten", reserveringen: "las de reserveringen",
};

export async function runAssistant({ app, scope, agent, messages, ctx }) {
  const tools = toolsFor(app, scope);
  const convo = [{ role: "system", content: systemPrompt(app, scope, agent) }, ...messages];
  const used = [];
  let demo = false;
  for (let round = 0; round <= MAX_TOOL_ROUNDS; round++) {
    const j = await xai(convo, round < MAX_TOOL_ROUNDS ? tools.definitions : []);
    const msg = j.choices?.[0]?.message || {};
    const calls = msg.tool_calls || [];
    if (!calls.length) {
      let reply = (msg.content || "").trim();
      if (app === "kanalo" && promisesFreeContent(reply)) {
        // Eén keer laten herschrijven; lukt dat niet, dan het vaste veilige antwoord.
        const fix = await xai([...convo, { role: "assistant", content: reply },
          { role: "user", content: "Je antwoord wekt de indruk dat Kanalo gratis zenders, films of sport levert. Dat mag niet. Herschrijf het antwoord volgens de Kanalo-regels." }], []);
        reply = (fix.choices?.[0]?.message?.content || "").trim();
        if (promisesFreeContent(reply)) reply = KANALO_SAFE_REPLY;
        used.push("veiligheidscheck");
      }
      return { reply, tools_used: used, demo_data: demo, model: j.model || XAI_MODEL };
    }
    convo.push({ role: "assistant", content: msg.content || null, tool_calls: calls });
    for (const call of calls) {
      let args = {};
      try { args = JSON.parse(call.function?.arguments || "{}"); } catch {}
      const name = call.function?.name;
      const result = await tools.run(name, args, ctx);
      if (result?.demo) demo = true;
      used.push(name);
      if (scope === "owner") addLog(app, agent?.name, `${TOOL_LABELS[name] || name}${result?.demo ? " (voorbeelddata)" : ""}${result?.error ? " — mislukt" : ""}`);
      let content = JSON.stringify(result);
      if (content.length > 24000) content = content.slice(0, 24000) + "…(ingekort)";
      convo.push({ role: "tool", tool_call_id: call.id, content });
    }
  }
  throw Object.assign(new Error("Te veel toolrondes"), { status: 502 });
}

// ---------- HTTP ----------

const rate = new Map(); // simpele limiet per token: 30 verzoeken per minuut
function rateLimited(key) {
  const now = Date.now();
  const r = rate.get(key) || { n: 0, t: now };
  if (now - r.t > 60000) { r.n = 0; r.t = now; }
  r.n++;
  rate.set(key, r);
  return r.n > +env("RATE_PER_MINUTE", "30");
}

function cors(req, res) {
  const origin = req.headers.origin;
  if (origin && (ALLOWED_ORIGINS.includes("*") || ALLOWED_ORIGINS.includes(origin))) {
    res.setHeader("access-control-allow-origin", origin);
    res.setHeader("vary", "origin");
    res.setHeader("access-control-allow-headers", "authorization, content-type");
    res.setHeader("access-control-allow-methods", "GET, POST, OPTIONS");
  }
}

function send(res, status, obj) {
  res.writeHead(status, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  res.end(JSON.stringify(obj));
}

async function readJson(req) {
  let size = 0;
  const chunks = [];
  for await (const c of req) {
    size += c.length;
    if (size > 64 * 1024) throw Object.assign(new Error("Bericht te groot"), { status: 413 });
    chunks.push(c);
  }
  try { return JSON.parse(Buffer.concat(chunks).toString("utf8") || "{}"); }
  catch { throw Object.assign(new Error("Ongeldige JSON"), { status: 400 }); }
}

const clean = (s, n) => (typeof s === "string" ? s.slice(0, n) : undefined);

function normalizeMessages(body) {
  if (Array.isArray(body.messages)) {
    return body.messages.slice(-20)
      .filter((m) => (m.role === "user" || m.role === "assistant") && typeof m.content === "string")
      .map((m) => ({ role: m.role, content: m.content.slice(0, 8000) }));
  }
  const text = clean(body.task || body.message || body.prompt, 8000);
  return text ? [{ role: "user", content: text }] : [];
}

async function handleAssistant(req, res, auth) {
  const body = await readJson(req);
  const app = auth.scope === "owner" ? body.app : auth.app;
  if (!APPS[app]) return send(res, 400, { error: "Onbekende app" });
  if (auth.scope === "app" && body.app && body.app !== auth.app) return send(res, 403, { error: "Dit token hoort bij een andere app" });
  const messages = normalizeMessages(body);
  if (!messages.length || messages.at(-1).role !== "user") return send(res, 400, { error: "Geen vraag of taak meegestuurd" });

  const agent = auth.scope === "owner" ? { name: clean(body.agent, 40), role: clean(body.role, 80) } : null;
  const ctx = {
    device_id: clean(req.headers["x-device-id"], 100),
    restaurant_id: clean(req.headers["x-restaurant-id"], 100),
  };

  const t0 = Date.now();
  const s = store(app);
  const task = auth.scope === "owner"
    ? { id: crypto.randomUUID(), agent: agent.name || null, role: agent.role || null, text: messages.at(-1).content, status: "bezig", at: new Date().toISOString() }
    : null;
  if (task) { s.data.tasks.unshift(task); s.data.tasks.length = Math.min(s.data.tasks.length, 100); addLog(app, agent.name, `kreeg een taak: ${task.text.slice(0, 120)}`); }

  try {
    const out = await runAssistant({ app, scope: auth.scope, agent, messages, ctx });
    const ms = Date.now() - t0;
    if (task) { Object.assign(task, { status: "klaar", result: out.reply, tools_used: out.tools_used, ms, demo_data: out.demo_data }); addLog(app, agent.name, `✓ taak klaar: ${task.text.slice(0, 120)}`); persist(app); }
    send(res, 200, { ...out, ms, task_id: task?.id });
  } catch (e) {
    if (task) { Object.assign(task, { status: "fout", result: String(e.message), ms: Date.now() - t0 }); addLog(app, agent.name, "kon de taak niet afronden"); persist(app); }
    throw e;
  }
}

function handleState(req, res, auth, url) {
  if (auth.scope !== "owner") return send(res, 403, { error: "Alleen voor de werkvloer (OWNER_TOKEN)" });
  const app = url.searchParams.get("app");
  if (!APPS[app]) return send(res, 400, { error: "Onbekende app" });
  const { tasks, log } = store(app).data;
  const today = new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Amsterdam" });
  const doneToday = tasks.filter((t) => t.status === "klaar" && new Date(t.at).toLocaleDateString("sv-SE", { timeZone: "Europe/Amsterdam" }) === today);
  const times = tasks.filter((t) => t.ms).slice(0, 40).map((t) => t.ms);
  send(res, 200, {
    app,
    tasks: tasks.slice(0, 50),
    log: log.slice(0, 100),
    stats: {
      done_today: doneToday.length,
      busy: tasks.filter((t) => t.status === "bezig").length,
      avg_seconds: times.length ? +(times.reduce((a, b) => a + b, 0) / times.length / 1000).toFixed(1) : null,
    },
  });
}

function serveWerkvloer(res, app) {
  let html = fs.readFileSync(path.join(DIR, "public", "werkvloer.html"), "utf8");
  html = html.replace("<head>", `<head>\n<meta name="werkvloer-app" content="${app}">`);
  res.writeHead(200, {
    "content-type": "text/html; charset=utf-8",
    "cache-control": "no-store",
    "content-security-policy": "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; connect-src 'self'; img-src 'self' data:",
  });
  res.end(html);
}

export function createServer() {
  return http.createServer(async (req, res) => {
    cors(req, res);
    const url = new URL(req.url, "http://localhost");
    try {
      if (req.method === "OPTIONS") { res.writeHead(204); return res.end(); }
      if (req.method === "GET" && url.pathname === "/health") return send(res, 200, { ok: true, model: XAI_MODEL });
      const wv = /^\/werkvloer\/(kanalo|tablejoy)\/?$/.exec(url.pathname);
      if (req.method === "GET" && wv) return serveWerkvloer(res, wv[1]);

      const auth = authenticate(req);
      if (url.pathname === "/assistant" || url.pathname === "/werkvloer/state") {
        if (!auth) return send(res, 401, { error: "Ongeldig of ontbrekend token" });
        if (rateLimited(auth.token)) return send(res, 429, { error: "Even te veel verzoeken. Probeer het over een minuut opnieuw." });
      }
      if (req.method === "POST" && url.pathname === "/assistant") return await handleAssistant(req, res, auth);
      if (req.method === "GET" && url.pathname === "/werkvloer/state") return handleState(req, res, auth, url);
      send(res, 404, { error: "Niet gevonden" });
    } catch (e) {
      console.error(new Date().toISOString(), req.method, url.pathname, e.message);
      if (!res.headersSent) send(res, e.status || 500, { error: e.status ? e.message : "Er ging iets mis op de server" });
    }
  });
}

if (process.argv[1] === fileURLToPath(import.meta.url)) {
  if (!tokenTable().length) console.warn("Let op: geen TABLEJOY_TOKEN, KANALO_TOKEN of OWNER_TOKEN ingesteld; alle verzoeken worden geweigerd.");
  createServer().listen(PORT, () => console.log(`Assistent-server op http://localhost:${PORT} (model ${XAI_MODEL})`));
}
