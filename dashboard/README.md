# Command Center dashboard

**This repository is public. The dashboard in git is deliberately data-free.**

`command-center.html` is committed with an empty `DATA BLOCK`. That block is the
only part of the file that holds real business data — lead names, email
addresses, deal values and reply text — and it is regenerated from the live APIs
at build time, never committed.

To get a working dashboard locally:

```sh
node dashboard/pull/apply-constants.mjs   # fills the DATA BLOCK from live APIs
open dashboard/index.html
```

Do not commit the result. `git checkout -- dashboard/command-center.html` puts
it back to the data-free state. The scheduled workflow builds it the same way
and keeps it as a private workflow artifact instead of committing it.

The Pages deploy is manual-only for the same reason: a Pages site is publicly
readable even from a private repository.

---

Static dashboard published with GitHub Pages. The generated data block in
`command-center.html` is refreshed by GitHub Actions every six hours from
Pipedrive, Smartlead, and HeyReach.

## GitHub setup

Keep this repository private because the generated dashboard contains business
data and contact information. Add these repository Actions secrets:

- `PIPEDRIVE_API_TOKEN`
- `PIPEDRIVE_COMPANY_DOMAIN`
- `SMARTLEAD_API_KEY`
- `SMARTLEAD_BASE_URL` (optional)
- `HEYREACH_API_KEY`
- `HEYREACH_ORG_API_KEY` (optional)

Then enable GitHub Pages with **GitHub Actions** as the source. The first data
refresh can also be started manually from the Actions tab.

To refresh locally, export the same variables or keep the existing `.env` files
in `~/pipedrive-api-client` and `~/smartlead-api-client`, then run:

```sh
node pull/apply-constants.mjs
```
## Google Workspace access (SEO tracker, Drive, Gmail)

The SEO & GEO page reads the shared issue tracker straight from Drive on the
same six-hourly schedule. Access uses a **service account**, not an OAuth
`client_secret` desktop client: the desktop flow needs a human to click through
a browser consent screen, which a scheduled job cannot do.

**Never commit a key file.** The Pages workflow publishes what is committed, so
a credential in the repo becomes a public URL. `.gitignore` blocks the usual
filenames; the key belongs in a repo secret and, locally, in `.env`.

### One-time setup

1. In the `albertscott-seo-automation` project, create a service account and
   download a JSON key. Note its `client_email`
   (`something@albertscott-seo-automation.iam.gserviceaccount.com`).
2. Add repository Actions secrets:
   - `GOOGLE_SERVICE_ACCOUNT_JSON` — the whole key file, pasted as one value
   - `SEO_TRACKER_FILE_ID` — the id in the tracker URL, between `/d/` and `/edit`
   - `SEO_TRACKER_TAB` — optional, only if the issues are not on the first tab
3. Convert the tracker from `.xlsx` to a native Google Sheet
   (**File > Save as Google Sheets**). The Sheets API cannot read an uploaded
   `.xlsx`, and a live Sheet also means the team stops re-uploading copies.
4. Share that Sheet with the service account's `client_email`, Viewer access.
   A service account is not a member of the Workspace; it only sees what is
   shared with it explicitly.

Then run it locally to confirm:

```sh
GOOGLE_SERVICE_ACCOUNT_JSON="$(cat ~/keys/albertscott-seo-automation.json)" \
SEO_TRACKER_FILE_ID=... node pull/pull-seo-tracker.mjs
```

It prints the issue counts it wrote and refuses to overwrite a populated
dashboard with a suspiciously empty read.

### Gmail needs one extra step

Drive and Sheets work with plain file sharing. **Gmail does not**: a service
account has no mailbox, so reading `yoni@albertscott.com` requires
domain-wide delegation, which only a Workspace super-admin can grant:

> admin.google.com > Security > Access and data control > API controls >
> Domain-wide delegation > add the service account's **client ID** and
> authorise `https://www.googleapis.com/auth/gmail.readonly`

Grant `gmail.readonly` and nothing wider. Delegation lets the service account
impersonate any user in the domain for the scopes granted, so the scope list is
the only thing limiting it.
