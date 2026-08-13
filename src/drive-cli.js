#!/usr/bin/env node
/**
 * Tiny CLI wrapper around GoogleDriveClient. No dependencies.
 *
 * Usage:
 *   node src/drive-cli.js drive:list "name contains 'fancy-food'"
 *   node src/drive-cli.js drive:get <fileId>
 *   node src/drive-cli.js drive:create-folder "Fancy Foods Exports" <parentFolderId>
 *   node src/drive-cli.js drive:upload <localFilePath> [folderId] [driveFileName]
 *   node src/drive-cli.js drive:move <fileId> <addParentId> [removeParentId]
 *
 * Reads GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN from the environment.
 * Loads a local .env file automatically if present (no dotenv dependency needed).
 * Run `node scripts/google-drive-auth.mjs` once first to obtain a refresh token.
 */

import fs from "node:fs";
import path from "node:path";
import { GoogleDriveClient } from "./google-drive-client.js";

loadDotEnv();

const [, , cmd, ...args] = process.argv;

let client;

const commands = {
  "drive:list": (query) => client.listFiles({ query }),
  "drive:get": (fileId) => client.getFile(fileId, { fields: "*" }),
  "drive:create-folder": (name, parentId) => client.createFolder(name, parentId),
  "drive:move": (fileId, addParents, removeParents) => client.moveFile(fileId, { addParents, removeParents }),
  "drive:upload": (filePath, folderId, fileName) => {
    const resolved = path.resolve(process.cwd(), filePath);
    const content = fs.readFileSync(resolved);
    return client.uploadFile({ content, name: fileName || path.basename(resolved), folderId });
  },
};

async function main() {
  const fn = commands[cmd];
  if (!fn) {
    console.error(`Unknown or missing command: ${cmd ?? "(none)"}\n`);
    console.error("Available commands:\n  " + Object.keys(commands).join("\n  "));
    process.exit(1);
  }
  try {
    client = new GoogleDriveClient({});
    const result = await fn(...args);
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error(err.message);
    if (err.body) console.error(JSON.stringify(err.body, null, 2));
    process.exit(1);
  }
}

function loadDotEnv() {
  const envPath = path.resolve(process.cwd(), ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = value;
  }
}

main();
