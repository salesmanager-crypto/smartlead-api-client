#!/usr/bin/env node
/**
 * Prints the dashboard's content key, for the DASHBOARD_CONTENT_KEY Actions secret.
 *
 *   node scripts/recover-content-key.mjs            # reads the live Pages sign-in page
 *   node scripts/recover-content-key.mjs index.html # or a saved copy of it
 *
 * Run it on your own machine. It asks for your dashboard username and password,
 * unwraps your copy of the content key exactly the way the sign-in page does, checks
 * the key by decrypting the dashboard, and prints the key once. Nothing is sent
 * anywhere except the one GET of the public sign-in page. Paste the output straight
 * into GitHub: Settings > Secrets and variables > Actions > New repository secret,
 * name DASHBOARD_CONTENT_KEY. Do not paste it into a chat or commit it.
 *
 * Every account wraps the same content key, so any one account recovers it, and
 * pages encrypted with it keep working for every existing username and password.
 */
import fs from "node:fs";
import readline from "node:readline";
import { webcrypto as crypto } from "node:crypto";

const LIVE = "https://salesmanager-crypto.github.io/smartlead-api-client/";

const rl = readline.createInterface({ input: process.stdin, output: process.stdout, terminal: process.stdin.isTTY });
let muted = false;
const write = rl._writeToOutput.bind(rl);
rl._writeToOutput = (s) => { if (!muted) write(s); }; // echo nothing while the password is typed
const lines = rl[Symbol.asyncIterator]();
async function ask(question, { hidden = false } = {}) {
  process.stdout.write(question);
  muted = hidden;
  const { value } = await lines.next();
  muted = false;
  if (hidden) process.stdout.write("\n");
  return value ?? "";
}

const b64 = (s) => Uint8Array.from(Buffer.from(s, "base64"));

const src = process.argv[2];
const html = src ? fs.readFileSync(src, "utf8") : await (await fetch(LIVE)).text();

const U = JSON.parse(/var U=(\{.*?\});\s*\n/.exec(html)?.[1] ?? "null");
const dm = /var D=\{iv:"([^"]+)",ct:"([^"]+)",iter:(\d+)\}/.exec(html);
if (!U || !dm) {
  console.error("That page does not look like the encrypted sign-in page (no U / D records found).");
  process.exit(1);
}
const D = { iv: dm[1], ct: dm[2], iter: Number(dm[3]) };

const name = (await ask("Dashboard username: ")).trim().toLowerCase();
const rec = U[name];
if (!rec) {
  console.error(`No account named "${name}" on that page. Accounts: ${Object.keys(U).join(", ")}`);
  rl.close();
  process.exit(1);
}
const pass = await ask("Password (not shown): ", { hidden: true });
rl.close();

try {
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(name + "\0" + pass), "PBKDF2", false, ["deriveKey"]);
  const kek = await crypto.subtle.deriveKey(
    { name: "PBKDF2", salt: b64(rec.s), iterations: D.iter, hash: "SHA-256" },
    base, { name: "AES-GCM", length: 256 }, false, ["decrypt"]
  );
  const raw = new Uint8Array(await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(rec.i) }, kek, b64(rec.w)));
  // prove it is the right key before printing it
  const key = await crypto.subtle.importKey("raw", raw, "AES-GCM", false, ["decrypt"]);
  const page = new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: b64(D.iv) }, key, b64(D.ct)));
  if (!/<html|<!doctype/i.test(page.slice(0, 500))) throw new Error("decrypted content is not HTML");

  console.log("\nKey verified: it decrypts the current dashboard.");
  console.log("Save this as the Actions secret DASHBOARD_CONTENT_KEY:\n");
  console.log(Buffer.from(raw).toString("base64"));
  console.log("");
} catch {
  console.error("Incorrect username or password.");
  process.exit(1);
}
