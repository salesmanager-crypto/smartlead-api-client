# Dashboard code

One page, two builds. See the root README, "Daily refresh", for the whole pipeline.

| File | What it is |
|---|---|
| `command-center.html` | The dashboard: layout, styles and render code for every route. Its DATA BLOCK is empty in git and is filled by a builder. Opening this file directly shows an empty dashboard. |
| `data-map.js` | The single mapping from `docs/data/*.json` to the constants the page reads. Both builders use it, so the two dashboards cannot drift. |
| `signin.html` | The GitHub Pages sign-in page (per-account envelope encryption, AES-256-GCM under PBKDF2). `scripts/build-pages.mjs` puts the encrypted dashboard into it. |

- `scripts/build-pages.mjs` -> `docs/index.html`: sign-in page + encrypted dashboard code
  that fetches `docs/data/` after sign-in. No data inside.
- `scripts/build-artifact.mjs` -> `docs/artifact/alberscott-dashboard.html.enc`: the same page
  with all data inlined, for the Claude artifact.

Edit `command-center.html` for any change to what the dashboards show; both pick it up on the
next build. Screenshots of every route, taken with synthetic person data, are in
`docs/screenshots/`.
