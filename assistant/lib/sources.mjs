// Databronnen voor de assistenten. Elke bron leest alleen; niets schrijft terug.
// Is een bron niet ingesteld, dan geeft hij voorbeelddata terug met demo:true,
// zodat de assistent eerlijk kan zeggen dat het geen echte cijfers zijn.

import crypto from "node:crypto";
import fs from "node:fs";

const env = (k) => (process.env[k] || "").trim();

// ---------- Kanalo: de Kanalo MCP-server (streamable HTTP, JSON-RPC) ----------

let mcpSession = null; // { id, url }

async function mcpPost(url, body, sessionId) {
  const headers = {
    "content-type": "application/json",
    accept: "application/json, text/event-stream",
  };
  if (env("KANALO_MCP_TOKEN")) headers.authorization = `Bearer ${env("KANALO_MCP_TOKEN")}`;
  if (sessionId) headers["mcp-session-id"] = sessionId;
  const res = await fetch(url, { method: "POST", headers, body: JSON.stringify(body), signal: AbortSignal.timeout(20000) });
  if (!res.ok && res.status !== 202) throw new Error(`Kanalo-server gaf HTTP ${res.status}`);
  const sid = res.headers.get("mcp-session-id");
  const type = res.headers.get("content-type") || "";
  const text = await res.text();
  let msg = null;
  if (type.includes("text/event-stream")) {
    // Pak het laatste data:-bericht met ons id.
    for (const block of text.split(/\n\n/)) {
      const data = block.split("\n").filter((l) => l.startsWith("data:")).map((l) => l.slice(5).trim()).join("");
      if (!data) continue;
      try { const m = JSON.parse(data); if (m.id === body.id) msg = m; } catch {}
    }
  } else if (text) {
    msg = JSON.parse(text);
  }
  return { msg, sid };
}

async function kanaloCall(tool, args = {}) {
  const url = env("KANALO_MCP_URL");
  if (!mcpSession || mcpSession.url !== url) {
    const init = await mcpPost(url, {
      jsonrpc: "2.0", id: 1, method: "initialize",
      params: { protocolVersion: "2025-06-18", capabilities: {}, clientInfo: { name: "assistent-server", version: "1.0" } },
    });
    mcpSession = { id: init.sid, url };
    await mcpPost(url, { jsonrpc: "2.0", method: "notifications/initialized" }, mcpSession.id).catch(() => {});
  }
  const id = Math.floor(Math.random() * 1e9);
  let { msg } = await mcpPost(url, { jsonrpc: "2.0", id, method: "tools/call", params: { name: tool, arguments: args } }, mcpSession.id);
  if (!msg) throw new Error("Geen antwoord van de Kanalo-server");
  if (msg.error) {
    mcpSession = null; // sessie mogelijk verlopen; volgende keer opnieuw
    throw new Error(msg.error.message || "Fout van de Kanalo-server");
  }
  const r = msg.result || {};
  if (r.structuredContent) return r.structuredContent;
  const txt = (r.content || []).filter((c) => c.type === "text").map((c) => c.text).join("\n");
  try { return JSON.parse(txt); } catch { return { text: txt }; }
}

const KANALO_DEMO = {
  list_bug_reports: {
    demo: true, total: 2, by_category: { playback: 1, epg: 1 },
    reports: [
      { id: "demo-1", at: "2026-11-20T19:02:00Z", category: "playback", message: "Stream blijft hangen na 10 minuten op Apple TV", app_version: "1.6.13", model: "AppleTV14,1", is_pro: true, resolved: false },
      { id: "demo-2", at: "2026-11-18T08:41:00Z", category: "epg", message: "Gids laat geen programma's zien", app_version: "1.6.12", model: "iPhone16,2", is_pro: false, resolved: false },
    ],
  },
  get_bug_report: { demo: true, id: "demo-1", message: "Stream blijft hangen na 10 minuten op Apple TV", category: "playback", resolved: false },
  get_mrr: { demo: true, mrr_eur: 0, arr_eur: 0, plans: [] },
  get_trial_stats: { demo: true, started: 0, converted: 0, expired: 0, conversion: null },
  list_app_store_notifications: { demo: true, total: 0, notifications: [] },
  get_device: { demo: true, is_pro: false, app_store_notifications: [], bug_reports: [] },
};

export async function kanalo(tool, args) {
  if (!env("KANALO_MCP_URL")) return { ...KANALO_DEMO[tool], demo: true, note: "KANALO_MCP_URL is niet ingesteld: dit is voorbeelddata." };
  return kanaloCall(tool, args);
}

// ---------- Kanalo: App Store-reviews via de App Store Connect API ----------

function ascToken() {
  const keyPem = env("ASC_PRIVATE_KEY") || (env("ASC_PRIVATE_KEY_PATH") ? fs.readFileSync(env("ASC_PRIVATE_KEY_PATH"), "utf8") : "");
  const b64 = (o) => Buffer.from(JSON.stringify(o)).toString("base64url");
  const now = Math.floor(Date.now() / 1000);
  const head = b64({ alg: "ES256", kid: env("ASC_KEY_ID"), typ: "JWT" });
  const body = b64({ iss: env("ASC_ISSUER_ID"), iat: now, exp: now + 15 * 60, aud: "appstoreconnect-v1" });
  const sig = crypto.sign("sha256", Buffer.from(`${head}.${body}`), { key: keyPem, dsaEncoding: "ieee-p1363" });
  return `${head}.${body}.${sig.toString("base64url")}`;
}

export async function appStoreReviews({ limit = 20, territory } = {}) {
  const ready = env("ASC_KEY_ID") && env("ASC_ISSUER_ID") && env("ASC_APP_ID") && (env("ASC_PRIVATE_KEY") || env("ASC_PRIVATE_KEY_PATH"));
  if (!ready) {
    return {
      demo: true, note: "App Store Connect-sleutel is niet ingesteld: dit is voorbeelddata.",
      reviews: [
        { rating: 2, title: "EPG werkt niet", body: "Gids blijft leeg bij mijn playlist.", territory: "NLD", date: "2026-11-21" },
        { rating: 5, title: "Super speler", body: "Snel en overzichtelijk.", territory: "DEU", date: "2026-11-19" },
      ],
    };
  }
  const q = new URLSearchParams({ sort: "-createdDate", limit: String(Math.min(Math.max(+limit || 20, 1), 100)) });
  if (territory) q.set("filter[territory]", String(territory).toUpperCase());
  const res = await fetch(`https://api.appstoreconnect.apple.com/v1/apps/${env("ASC_APP_ID")}/customerReviews?${q}`, {
    headers: { authorization: `Bearer ${ascToken()}` }, signal: AbortSignal.timeout(20000),
  });
  if (!res.ok) throw new Error(`App Store Connect gaf HTTP ${res.status}`);
  const j = await res.json();
  return {
    reviews: (j.data || []).map((r) => ({
      rating: r.attributes.rating, title: r.attributes.title, body: r.attributes.body,
      territory: r.attributes.territory, date: (r.attributes.createdDate || "").slice(0, 10),
    })),
  };
}

// ---------- TableJoy: reserveringen ----------
// Verwacht een REST-API: GET {TABLEJOY_API_URL}/reservations?date=YYYY-MM-DD[&restaurant_id=..][&q=..]
// met Authorization: Bearer {TABLEJOY_API_KEY}. Pas het pad aan in TABLEJOY_RESERVATIONS_PATH.

export async function tablejoyReservations({ date, restaurant_id, q } = {}) {
  const base = env("TABLEJOY_API_URL");
  if (!base) {
    return {
      demo: true, note: "TABLEJOY_API_URL is niet ingesteld: dit is voorbeelddata.", date: date || "vandaag",
      reservations: [
        { time: "18:00", name: "Familie Jansen", party_size: 4, status: "bevestigd", notes: "kinderstoel" },
        { time: "19:30", name: "De Vries", party_size: 2, status: "bevestigd", notes: "glutenvrij" },
        { time: "20:00", name: "Bakker", party_size: 6, status: "wacht op bevestiging", notes: "" },
      ],
    };
  }
  const params = new URLSearchParams();
  if (date) params.set("date", date);
  if (restaurant_id) params.set("restaurant_id", restaurant_id);
  if (q) params.set("q", q);
  const path = env("TABLEJOY_RESERVATIONS_PATH") || "/reservations";
  const res = await fetch(`${base.replace(/\/$/, "")}${path}?${params}`, {
    headers: env("TABLEJOY_API_KEY") ? { authorization: `Bearer ${env("TABLEJOY_API_KEY")}` } : {},
    signal: AbortSignal.timeout(20000),
  });
  if (!res.ok) throw new Error(`TableJoy-API gaf HTTP ${res.status}`);
  return res.json();
}
