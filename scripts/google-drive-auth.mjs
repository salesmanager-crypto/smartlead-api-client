import fs from "node:fs";
import path from "node:path";
import readline from "node:readline";
import { fileURLToPath } from "node:url";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

// minimal .env loader (mirrors src/cli.js)
const envPath = path.join(projectRoot, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq === -1) continue;
    const k = t.slice(0, eq).trim();
    const v = t.slice(eq + 1).trim();
    if (!(k in process.env)) process.env[k] = v;
  }
}

const clientId = process.env.GOOGLE_CLIENT_ID;
const clientSecret = process.env.GOOGLE_CLIENT_SECRET;
const redirectUri = process.env.GOOGLE_REDIRECT_URI || "http://localhost:8080/callback";

if (!clientId || !clientSecret) {
  console.error(
    "Missing GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET.\n" +
      "Copy them from your downloaded Google OAuth client JSON into .env (see .env.example)."
  );
  process.exit(1);
}

// drive.file: this app can only see/manage files it creates or that the user opens with it —
// broader than that requires the "drive" scope instead, which is not needed here.
const SCOPE = "https://www.googleapis.com/auth/drive.file";

const authUrl = new URL("https://accounts.google.com/o/oauth2/v2/auth");
authUrl.searchParams.set("client_id", clientId);
authUrl.searchParams.set("redirect_uri", redirectUri);
authUrl.searchParams.set("response_type", "code");
authUrl.searchParams.set("scope", SCOPE);
authUrl.searchParams.set("access_type", "offline");
authUrl.searchParams.set("prompt", "consent");

console.log("1. Open this URL and sign in with the Google account you want to connect:\n");
console.log(`   ${authUrl.toString()}\n`);
console.log(`2. After you approve, the browser will try to redirect to ${redirectUri} and fail to load —`);
console.log("   that's expected, nothing needs to be listening there. Copy the full URL from the address");
console.log("   bar anyway (or just the `code=...` value) and paste it below.\n");

const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
rl.question("Paste the redirect URL (or just the code): ", async (answer) => {
  rl.close();
  const code = extractCode(answer.trim());
  if (!code) {
    console.error("Couldn't find a `code` value in that input.");
    process.exit(1);
  }

  let res, data;
  try {
    res = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "authorization_code",
        code,
        client_id: clientId,
        client_secret: clientSecret,
        redirect_uri: redirectUri,
      }),
    });
    data = await res.json();
  } catch (err) {
    console.error(`Token exchange request failed: ${err.message}`);
    process.exit(1);
  }

  if (!res.ok) {
    console.error(`Token exchange failed: ${res.status}`);
    console.error(JSON.stringify(data, null, 2));
    process.exit(1);
  }
  if (!data.refresh_token) {
    console.error(
      "Google didn't return a refresh_token (it only issues one the first time an app is authorized " +
        "for an account, or when access is re-consented).\n" +
        "Revoke prior access at https://myaccount.google.com/permissions and run this script again."
    );
    process.exit(1);
  }

  const tokenPath = path.join(projectRoot, ".google-token.json");
  fs.writeFileSync(
    tokenPath,
    JSON.stringify(
      { refresh_token: data.refresh_token, scope: data.scope, obtained_at: new Date().toISOString() },
      null,
      2
    ) + "\n",
    "utf8"
  );

  console.log(`\nSaved refresh token to ${tokenPath} (gitignored).`);
  console.log("Add this line to your .env so the Drive client can use it:\n");
  console.log(`GOOGLE_REFRESH_TOKEN=${data.refresh_token}\n`);
});

function extractCode(input) {
  // Accept either a bare code or a full redirect URL containing ?code=...
  if (input.includes("code=")) {
    try {
      const url = new URL(input);
      return url.searchParams.get("code");
    } catch {
      const match = input.match(/[?&]code=([^&]+)/);
      return match ? decodeURIComponent(match[1]) : null;
    }
  }
  return input || null;
}
