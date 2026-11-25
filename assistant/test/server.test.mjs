// node --test test/   — draait tegen een nep-xAI, kost niets.
import test from "node:test";
import assert from "node:assert/strict";
import http from "node:http";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

// ---- nep-xAI: speelt een script af per laatste gebruikersvraag ----
const seen = [];
const fake = http.createServer(async (req, res) => {
  let b = ""; for await (const c of req) b += c;
  const body = JSON.parse(b);
  seen.push(body);
  const last = [...body.messages].reverse().find((m) => m.role === "user").content;
  const hadTool = body.messages.some((m) => m.role === "tool");
  const say = (content) => res.end(JSON.stringify({ model: "fake-grok", choices: [{ message: { role: "assistant", content } }] }));
  const call = (name, args) => res.end(JSON.stringify({ model: "fake-grok", choices: [{ message: { role: "assistant", content: null, tool_calls: [{ id: "c1", type: "function", function: { name, arguments: JSON.stringify(args) } }] } }] }));
  res.setHeader("content-type", "application/json");
  if (last.includes("reserveringen") && !hadTool) return call("reserveringen", { date: "2026-11-25" });
  if (last.includes("bugs") && !hadTool) return call("bugrapporten", { limit: 5 });
  if (last.includes("gratis")) return say("Met Kanalo krijg je gratis zenders en sport!");
  if (last.includes("Herschrijf")) return say("Natuurlijk, gratis films en sport kijken kan direct.");
  if (hadTool) {
    const tool = body.messages.find((m) => m.role === "tool");
    return say("Samenvatting: " + tool.content.slice(0, 200));
  }
  say("Hallo!");
});
await new Promise((r) => fake.listen(0, r));

process.env.XAI_BASE_URL = `http://127.0.0.1:${fake.address().port}`;
process.env.XAI_API_KEY = "test";
process.env.TABLEJOY_TOKEN = "tj-token";
process.env.KANALO_TOKEN = "kn-token";
process.env.OWNER_TOKEN = "owner-token";
process.env.DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), "assist-"));
delete process.env.KANALO_MCP_URL; delete process.env.TABLEJOY_API_URL;

const { createServer, promisesFreeContent } = await import("../server.mjs");
const srv = createServer();
await new Promise((r) => srv.listen(0, r));
const base = `http://127.0.0.1:${srv.address().port}`;
const post = (token, body, headers = {}) => fetch(`${base}/assistant`, {
  method: "POST", headers: { "content-type": "application/json", ...(token ? { authorization: `Bearer ${token}` } : {}), ...headers }, body: JSON.stringify(body),
});

test.after(() => { srv.close(); fake.close(); });

test("zonder of met fout token: 401", async () => {
  assert.equal((await post(null, { message: "hoi" })).status, 401);
  assert.equal((await post("fout", { message: "hoi" })).status, 401);
});

test("app-token mag niet bij de andere app", async () => {
  assert.equal((await post("tj-token", { app: "kanalo", message: "hoi" })).status, 403);
});

test("TableJoy-app: function calling met restaurant uit de header", async () => {
  const r = await post("tj-token", { message: "welke reserveringen hebben we vandaag?" }, { "x-restaurant-id": "r42" });
  const j = await r.json();
  assert.equal(r.status, 200);
  assert.deepEqual(j.tools_used, ["reserveringen"]);
  assert.equal(j.demo_data, true);
  assert.match(j.reply, /Familie Jansen/);
  // App-niveau krijgt geen restaurant_id-parameter: het model kan geen ander restaurant kiezen.
  const def = seen.at(-2).tools.find((t) => t.function.name === "reserveringen");
  assert.equal(def.function.parameters.properties.restaurant_id, undefined);
});

test("Kanalo-app krijgt alleen eigen tools; eigenaar krijgt bedrijfsdata", async () => {
  await post("kn-token", { message: "hoi" });
  const appTools = seen.at(-1).tools.map((t) => t.function.name).sort();
  assert.deepEqual(appTools, ["mijn_abonnement", "mijn_bugrapporten"]);
  await post("owner-token", { app: "kanalo", message: "hoi" });
  const ownerTools = seen.at(-1).tools.map((t) => t.function.name).sort();
  assert.deepEqual(ownerTools, ["abonnementen", "app_store_meldingen", "bugrapport", "bugrapporten", "reviews"]);
});

test("Kanalo-systeemprompt bevat de speler-regel", async () => {
  await post("kn-token", { message: "hoi" });
  const sys = seen.at(-1).messages[0].content;
  assert.match(sys, /alleen een speler/);
  assert.match(sys, /Beloof dus nooit gratis zenders, films of sport/);
});

test("Kanalo belooft nooit gratis content, ook als het model dat wel doet", async () => {
  const j = await (await post("kn-token", { message: "krijg ik gratis zenders?" })).json();
  assert.ok(!promisesFreeContent(j.reply), j.reply);
  assert.match(j.reply, /alleen een speler/);
  assert.ok(j.tools_used.includes("veiligheidscheck"));
});

test("vangnet herkent beloftes maar niet ontkenningen", () => {
  assert.ok(promisesFreeContent("Je kijkt gratis films en sport."));
  assert.ok(promisesFreeContent("Watch free channels today!"));
  assert.ok(!promisesFreeContent("Kanalo levert geen gratis zenders."));
  assert.ok(!promisesFreeContent("De app is gratis te downloaden."));
});

test("werkvloer: taak + logboek komen terug via /werkvloer/state", async () => {
  const r = await post("owner-token", { app: "kanalo", agent: "Sara", role: "Bugrapporten", task: "vat de open bugs samen" });
  const j = await r.json();
  assert.equal(r.status, 200);
  assert.deepEqual(j.tools_used, ["bugrapporten"]);
  const s = await (await fetch(`${base}/werkvloer/state?app=kanalo`, { headers: { authorization: "Bearer owner-token" } })).json();
  assert.equal(s.tasks[0].agent, "Sara");
  assert.equal(s.tasks[0].status, "klaar");
  assert.ok(s.log.some((l) => l.agent === "Sara" && /bugrapporten/.test(l.text)));
  assert.ok(s.stats.done_today >= 1);
  // Een app-token mag het logboek niet lezen.
  assert.equal((await fetch(`${base}/werkvloer/state?app=kanalo`, { headers: { authorization: "Bearer kn-token" } })).status, 403);
});

test("werkvloer-pagina bevat geen sleutel en geen claude.use", async () => {
  const html = await (await fetch(`${base}/werkvloer/tablejoy`)).text();
  assert.match(html, /<meta name="werkvloer-app" content="tablejoy">/);
  assert.doesNotMatch(html, /claude\.use|owner-token|xai-|XAI_API_KEY/);
  assert.match(html, /fetch\(server/);
});
