/**
 * Normalizes rows from one or more source tabs into a common contact schema,
 * de-duplicates by email across all of them, and writes the result into a
 * target tab.
 */

// Normalized master schema — every source row gets mapped into this shape.
export const MASTER_COLUMNS = ["First Name", "Last Name", "Email", "Phone", "Company", "Website", "Title", "Source", "Status"];

const ALIASES = {
  "First Name": ["first_name", "first name", "firstname"],
  "Last Name": ["last_name", "last name", "lastname"],
  Email: ["email", "email address"],
  Phone: ["phone_number", "phone", "phone number"],
  Company: ["company_name", "company", "company / account", "company/account"],
  Website: ["website", "site", "url"],
  Title: ["title", "job_title", "job title"],
  Source: ["source", "campaign_name", "campaign"],
  Status: ["status", "lead_status", "lead status", "category"],
};

function normalizeKey(h) {
  return (h || "").trim().toLowerCase();
}

function buildColumnMap(header) {
  const normalized = header.map(normalizeKey);
  const map = {};
  for (const [masterCol, aliases] of Object.entries(ALIASES)) {
    const idx = normalized.findIndex((h) => aliases.includes(h));
    if (idx >= 0) map[masterCol] = idx;
  }
  return map;
}

function normalizeRows(header, rows, sourceLabel) {
  const map = buildColumnMap(header);
  return rows.map((row) =>
    MASTER_COLUMNS.map((col) => (col === "Source" && map[col] === undefined ? sourceLabel : row[map[col]] || ""))
  );
}

/**
 * Normalize + de-duplicate (by email) any number of {header, rows, label} sources.
 * @param {Array<{header: string[], rows: string[][], label: string}>} sources
 * @returns {{rows: string[][], duplicatesRemoved: number}}
 */
export function dedupeSources(sources) {
  const combined = sources.flatMap((s) => normalizeRows(s.header, s.rows, s.label));
  const emailCol = MASTER_COLUMNS.indexOf("Email");
  const seen = new Set();
  const deduped = [];
  let duplicates = 0;
  for (const row of combined) {
    const key = (row[emailCol] || "").trim().toLowerCase();
    if (key && seen.has(key)) {
      duplicates++;
      continue;
    }
    if (key) seen.add(key);
    deduped.push(row);
  }
  return { rows: deduped, duplicatesRemoved: duplicates };
}

/**
 * Reads one or more source tabs (by title) from a spreadsheet, normalizes + de-dupes
 * them by email, and overwrites a target tab (by title) with the result.
 * @param {import("./google-sheets-client.js").GoogleSheetsClient} sheets
 * @param {string} spreadsheetId
 * @param {object} opts
 * @param {string[]} opts.sourceTitles
 * @param {string} opts.targetTitle
 */
export async function buildDedupedTab(sheets, spreadsheetId, { sourceTitles, targetTitle }) {
  const values = await Promise.all(sourceTitles.map((title) => sheets.getValues(spreadsheetId, title)));
  const sources = values.map((v, i) => {
    const [header, ...rows] = v;
    return { header, rows, label: sourceTitles[i] };
  });

  const { rows: deduped, duplicatesRemoved } = dedupeSources(sources);

  await sheets.clearValues(spreadsheetId, targetTitle);
  await sheets.updateValues(spreadsheetId, targetTitle, [MASTER_COLUMNS, ...deduped]);

  return {
    sources: sources.map((s, i) => ({ title: sourceTitles[i], rows: s.rows.length })),
    target: { title: targetTitle, rows: deduped.length },
    duplicatesRemoved,
  };
}

/**
 * Combines the 1st and 2nd tabs of a spreadsheet (by position, regardless of their
 * titles/column layouts) and overwrites the 3rd tab with the de-duplicated result.
 * @param {import("./google-sheets-client.js").GoogleSheetsClient} sheets
 * @param {string} spreadsheetId
 * @returns {Promise<{tab1: object, tab2: object, tab3: object, duplicatesRemoved: number}>}
 */
export async function buildMasterList(sheets, spreadsheetId) {
  const meta = await sheets.getSpreadsheet(spreadsheetId, { fields: "sheets.properties" });
  const byIndex = meta.sheets.sort((a, b) => a.properties.index - b.properties.index);
  if (byIndex.length < 3) {
    throw new Error(`Expected at least 3 tabs, found ${byIndex.length}: ${byIndex.map((s) => s.properties.title).join(", ")}`);
  }
  const [tab1, tab2, tab3] = byIndex;

  const result = await buildDedupedTab(sheets, spreadsheetId, {
    sourceTitles: [tab1.properties.title, tab2.properties.title],
    targetTitle: tab3.properties.title,
  });

  return {
    tab1: { title: tab1.properties.title, rows: result.sources[0].rows },
    tab2: { title: tab2.properties.title, rows: result.sources[1].rows },
    tab3: result.target,
    duplicatesRemoved: result.duplicatesRemoved,
  };
}
