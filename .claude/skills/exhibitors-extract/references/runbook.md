# Runbook: commands, files and order

All paths are relative to the repo root. Scripts live in `pipeline/`, and work units go in `pipeline/work/`. Every data file is gitignored. Agent prompts are `pipeline/*_prompt.txt`, with `{NN}` replaced by the chunk number. Launch one background subagent per chunk with "Read <prompt file> and follow it exactly with {NN} = 03." For SmartScout and Surfe agents, use a smaller model for speed.

| Phase | Run | Agents (prompt) | Output |
|---|---|---|---|
| 1 | `python3 pipeline/phase1_scrape.py` (set `SHOWS` at the top), then `phase1_summaries.py export 40` with agents and `collect`, then `phase1_build.py`, then `phase1_social.py` | About summaries | `phase1_exhibitors.xlsx`, `pipeline/work/social_links.csv` |
| 2 | `phase2_fetch_sites.py`, then `phase2_work.py export 40` with agents and `collect`, then `phase2_build.py` | `p2_agent_prompt.txt` (one web search per exhibitor for the parent; `p2_agent_prompt_nosearch.txt` once the search limit is spent) | `phase2_domains.xlsx` |
| 3 | `phase3_brandpages.py`, then `phase3_work.py export 25` with agents and `collect`, then `phase3_build.py` | `p3_agent_prompt.txt` (SmartScout only) | `phase3_brands_amazon.xlsx`, `smartscout_cache.json` |
| 4 (SmartScout detail) | `phase4_work.py export 30` with agents and `collect`, then `phase4_build.py` | `p4_agent_prompt.txt` | `phase4_smartscout.xlsx` |
| 4 (store names) | `amazon_store.py export`, then `sh pipeline/amz_run.sh 3`, `amazon_store.py status` until done, then `amazon_store.py collect`. Rerun `amz_run.sh` to retry errors. | none (Playwright) | `amazon_stores.csv` |
| 5 | `smartscout_store.py plan 200` with agents, then `smartscout_store.py build` | `ssx_agent_prompt.txt` (put the live PROFILE handle from `run_state.json` in `{HANDLE}`) | `smartscout_store.csv` |
| 6 | `surfe_people.py export 40` with agents, one at a time. Top up with `sf_tr_in_NN.jsonl` and the trickle prompt, then `surfe_people.py select` | `sf_agent_prompt.txt`, `sf_trickle_prompt.txt` | `surfe_people.csv`, `surfe_companies.csv` |
| 7 | `surfe_emails.py export 200 <credit budget>` with agents, then `surfe_emails.py collect` | `se_agent_prompt.txt` | `surfe_emails.csv` |
| 8 | `cold_emails.py export 40` with agents, then `cold_emails.py check` until clean, then `cold_emails.py collect` | `ce_agent_prompt.txt` | `cold_emails.csv` |
| 9 | `master_build.py`, then write `master_sheet.csv` to the Google Sheet | Sheets writer agents for large tables | `master_sheet.csv`, Google Sheet |

## Order and dependencies

- Phase 4 store names can run as soon as phase 3 is built. It's the slowest step (about 2 to 3 brands a minute per worker), so start it early and do the other phases while it runs. `run` puts the highest-revenue exhibitors first.
- Phase 6 needs only phase 2 domains and phase 4 revenue for ordering. Phase 7 and later need the store check, because emails are spent only on exhibitors with a verified or possible store.
- `master_build.py` works at any stage. Missing inputs show up as Row Status reasons such as "Amazon check not run yet" or "Email pending", so you can publish a partial sheet and refresh it later.

## Known traps

- Killing workers: `pkill -f "amazon_store.py run"` also matches the shell running the command and kills it (exit 144). Use `sh pipeline/amz_run.sh N` to restart, or a bracketed pattern like `pkill -f "amazon_store[.]py run"`.
- User agent: use the shared `common.UA`, which matches the installed Chromium. An outdated or odd version string gets every request sent to Amazon's soft check.
- Surfe people search quota: see `rules.md`, phase 6. Only one search agent at a time.
- Surfe `departments` filter: it fails validation. Use `job_titles`.
- SmartScout handles expire: get a fresh one with `query_analytics` and save it in `run_state.json`.
- Google Sheets: about 6 writes a minute, and `create_file` needs the content inline. For a big table, add the tab with `update_spreadsheet`, write blocks of about 500 rows with `update_values`, then read back the row count.
- No dashes: run `sed`-style replacements for em and en dashes on every text column before writing (`master_build.py` already does this).
