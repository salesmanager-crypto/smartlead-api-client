/**
 * Combines the 1st and 2nd tabs of a spreadsheet (by position, regardless of their
 * titles/column layouts) into a normalized contact schema, de-duplicates by email,
 * and overwrites the 3rd tab with the result.
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

  const [tab1Values, tab2Values] = await Promise.all([
    sheets.getValues(spreadsheetId, tab1.properties.title),
    sheets.getValues(spreadsheetId, tab2.properties.title),
  ]);
  const [tab1Header, ...tab1Rows] = tab1Values;
  const [tab2Header, ...tab2Rows] = tab2Values;

  const combined = [
    ...normalizeRows(tab1Header, tab1Rows, tab1.properties.title),
    ...normalizeRows(tab2Header, tab2Rows, tab2.properties.title),
  ];

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

  await sheets.clearValues(spreadsheetId, tab3.properties.title);
  await sheets.updateValues(spreadsheetId, tab3.properties.title, [MASTER_COLUMNS, ...deduped]);

  return {
    tab1: { title: tab1.properties.title, rows: tab1Rows.length },
    tab2: { title: tab2.properties.title, rows: tab2Rows.length },
    tab3: { title: tab3.properties.title, rows: deduped.length },
    duplicatesRemoved: duplicates,
  };
}
