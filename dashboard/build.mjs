#!/usr/bin/env node
/**
 * Builds the shareable dashboard into dashboard/_site/.
 *
 *   node dashboard/build.mjs
 *
 * Fills the DATA BLOCK from the live APIs, writes _site/index.html, then puts
 * the tracked file back to its data-free state so the fill is never committed.
 * _site/ is gitignored. Point any static host at it.
 */
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";

const HERE = path.resolve(path.dirname(new URL(import.meta.url).pathname));
const DASH = path.join(HERE, "command-center.html");
const SITE = path.join(HERE, "_site");

const pristine = fs.readFileSync(DASH, "utf8");
const emptyBlock = pristine.includes('const OVERDUE = [];');

try {
  console.error("filling the data block from live APIs...");
  execFileSync("node", [path.join(HERE, "pull", "apply-constants.mjs")], { stdio: "inherit" });

  const built = fs.readFileSync(DASH, "utf8");
  if (emptyBlock && built.includes("const OVERDUE = [];")) {
    throw new Error("apply-constants.mjs ran but the data block is still empty — check your API credentials.");
  }

  fs.mkdirSync(SITE, { recursive: true });
  fs.writeFileSync(path.join(SITE, "index.html"), built);

  const emails = new Set(built.match(/[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,}/g) || []);
  console.error(`\nwrote ${path.relative(process.cwd(), path.join(SITE, "index.html"))}`);
  console.error(`  ${(built.length / 1024).toFixed(0)} KB, ${emails.size} email addresses inside`);
  console.error("\nThis build contains real lead data. Put it behind access control,");
  console.error("not on a plain public URL. See dashboard/README.md.");
} finally {
  // never leave the filled version in the working tree
  fs.writeFileSync(DASH, pristine);
  console.error("\ntracked command-center.html restored to its data-free state");
}
