// Function calling: welke tools elke assistent krijgt.
//
// Twee niveaus:
//  - "app":   aanroepen uit de iOS-app (TABLEJOY_TOKEN / KANALO_TOKEN). Alleen data
//             van de gebruiker zelf; device_id / restaurant_id komen uit de request,
//             nooit van het model, zodat een gebruiker geen data van anderen kan opvragen.
//  - "owner": de werkvloer van de eigenaar (OWNER_TOKEN). Alle bedrijfsdata.

import { kanalo, appStoreReviews, tablejoyReservations } from "./sources.mjs";

const fn = (name, description, properties = {}, required = []) => ({
  type: "function",
  function: { name, description, parameters: { type: "object", properties, required, additionalProperties: false } },
});

const PERIOD = {
  type: "string",
  enum: ["today", "yesterday", "this_week", "last_week", "this_month", "last_month", "last_7_days", "last_30_days", "last_90_days", "this_year"],
  description: "Periode in Amsterdamse tijd",
};
const DATE = { type: "string", pattern: "^\\d{4}-\\d{2}-\\d{2}$", description: "YYYY-MM-DD" };

// Geef de assistent alleen wat hij nodig heeft (geen e-mailadressen of device-ID's).
function stripPersonal(obj) {
  if (Array.isArray(obj)) return obj.map(stripPersonal);
  if (obj && typeof obj === "object") {
    const out = {};
    for (const [k, v] of Object.entries(obj)) {
      if (/^(email|e_mail|device_id|ip|device_name|original_transaction_id)$/i.test(k)) continue;
      out[k] = stripPersonal(v);
    }
    return out;
  }
  return obj;
}

const TOOLS = {
  kanalo: {
    owner: [
      [fn("bugrapporten", "Bugrapporten en supportvragen uit de Kanalo-app, nieuwste eerst, met tellingen per categorie.", {
        status: { type: "string", enum: ["open", "resolved", "all"] }, period: PERIOD, category: { type: "string" },
        search: { type: "string", description: "Zoek in de tekst" }, limit: { type: "integer", minimum: 1, maximum: 50 },
      }), (a) => kanalo("list_bug_reports", a).then(stripPersonal)],
      [fn("bugrapport", "Eén bugrapport volledig, met diagnostics.", { id: { type: "string" } }, ["id"]),
        (a) => kanalo("get_bug_report", { id: a.id }).then(stripPersonal)],
      [fn("reviews", "Nieuwste App Store-reviews van Kanalo.", {
        limit: { type: "integer", minimum: 1, maximum: 50 }, territory: { type: "string", description: "Landcode, bv. NLD, DEU" },
      }), (a) => appStoreReviews(a)],
      [fn("abonnementen", "Stand van de abonnementen: MRR, ARR en betalende abonnees per plan, plus proefperiodes in de periode.", { period: PERIOD }),
        async (a) => ({ mrr: await kanalo("get_mrr", {}), proefperiodes: await kanalo("get_trial_stats", a.period ? { period: a.period } : {}) })],
      [fn("app_store_meldingen", "App Store-meldingen (aankopen, verlengingen, opzeggingen, refunds) in een periode.", {
        period: PERIOD, from: DATE, to: DATE, type: { type: "string", description: "bv. SUBSCRIBED, DID_RENEW, EXPIRED, REFUND" },
        limit: { type: "integer", minimum: 1, maximum: 100 },
      }), (a) => kanalo("list_app_store_notifications", a).then(stripPersonal)],
    ],
    app: [
      [fn("mijn_abonnement", "Abonnementsstatus (Pro, proefperiode, verloopdatum) van het toestel van deze gebruiker."),
        async (_a, ctx) => {
          if (!ctx.device_id) return { error: "Geen device_id meegestuurd door de app." };
          const d = await kanalo("get_device", { device_id: ctx.device_id });
          return stripPersonal({ demo: d.demo, is_pro: d.is_pro ?? d.device?.is_pro, pro_changes: d.pro_changes, app_store_notifications: d.app_store_notifications });
        }],
      [fn("mijn_bugrapporten", "Bugrapporten die deze gebruiker zelf heeft gestuurd, met status."),
        async (_a, ctx) => {
          if (!ctx.device_id) return { error: "Geen device_id meegestuurd door de app." };
          const d = await kanalo("get_device", { device_id: ctx.device_id });
          return stripPersonal({ demo: d.demo, bug_reports: d.bug_reports || [] });
        }],
    ],
  },
  tablejoy: {
    owner: [
      [fn("reserveringen", "Reserveringen van TableJoy op een datum, optioneel voor één restaurant of gefilterd op naam.", {
        date: DATE, restaurant_id: { type: "string" }, q: { type: "string", description: "Zoek op gastnaam" },
      }), (a) => tablejoyReservations(a)],
    ],
    app: [
      [fn("reserveringen", "Reserveringen van dit restaurant op een datum, optioneel gefilterd op gastnaam.", {
        date: DATE, q: { type: "string", description: "Zoek op gastnaam" },
      }), (a, ctx) => {
        if (!ctx.restaurant_id) return { error: "Geen restaurant_id meegestuurd door de app." };
        return tablejoyReservations({ date: a.date, q: a.q, restaurant_id: ctx.restaurant_id });
      }],
    ],
  },
};

export function toolsFor(app, scope) {
  const list = TOOLS[app]?.[scope] || [];
  return {
    definitions: list.map(([d]) => d),
    async run(name, args, ctx) {
      const hit = list.find(([d]) => d.function.name === name);
      if (!hit) return { error: `Onbekende tool: ${name}` };
      try {
        return await hit[1](args || {}, ctx || {});
      } catch (e) {
        return { error: String(e.message || e) };
      }
    },
  };
}
