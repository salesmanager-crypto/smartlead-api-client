#!/usr/bin/env node
// Build a single-file copy of the calendar for publishing as a claude.ai Artifact.
// Inlines data/shows.js and drops the document wrapper tags (the Artifact host adds its own).
//
//   node trade-show-calendar/tools/build-artifact.mjs   # -> trade-show-calendar/dist/trade-show-calendar.html

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const data = fs.readFileSync(path.join(root, "data", "shows.js"), "utf8").replace(/<\/script/gi, "<\\/script");

const tag = '<script src="data/shows.js"></script>';
if (!html.includes(tag)) throw new Error(`index.html no longer contains ${tag}`);

const out = html
  .replace(tag, () => `<script>\n${data}\n</script>`)
  .replace(/<!doctype html>\s*/i, "")
  .replace(/<html[^>]*>\s*/i, "")
  .replace(/<head>\s*/i, "")
  .replace(/<meta charset="utf-8">\s*/i, "")
  .replace(/<meta name="viewport"[^>]*>\s*/i, "")
  .replace(/<\/head>\s*<body>\s*/i, "")
  .replace(/<\/body>\s*<\/html>\s*$/i, "");

fs.mkdirSync(path.join(root, "dist"), { recursive: true });
const file = path.join(root, "dist", "trade-show-calendar.html");
fs.writeFileSync(file, out);
console.log(`Wrote ${file} (${Math.round(out.length / 1024)} KB)`);
