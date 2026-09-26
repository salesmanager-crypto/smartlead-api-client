# Token-saving checklist — do's and don'ts

Notes for keeping Claude Code token usage (and cost) down when starting a new task or chat in this project.

## ✅ Do

1. **Start a new chat per distinct task/goal.** Don't keep bolting new work onto an old conversation — cost per turn scales with how much history already exists, and it compounds fast (one session here grew from 34K to 930K tokens of re-read context over 1,625 turns).
2. **Use `/clear` or `/compact` when a sub-task wraps up** but you're staying in the same chat to keep working.
3. **Delegate heavy multi-step work to a sub-agent** (research, browsing, scraping, big searches). It runs in its own disposable context and hands back a short result instead of leaving every screenshot/page-read in the main thread forever.
4. **Read only what you need** — targeted greps/line ranges instead of whole files, filtered command output instead of raw dumps.
5. **Persist progress to a file/checkpoint** for anything you'll "resume" later, so the next session reads a small state file instead of replaying a giant transcript.
6. **Keep scheduled/automated tasks scoped and short** (the ones in this repo already run 6–16 turns — that's the right pattern, keep it that way).
7. **Check in on usage occasionally** to catch a runaway session early instead of after 1,600 turns.

## ❌ Don't

1. **Don't let one chat run across unrelated tasks indefinitely.** Long-running sessions are the single biggest lever — split them up.
2. **Don't repeatedly reload/edit the same large working file dozens of times in one session.** Each read/edit re-pulls the whole file into context.
3. **Don't dump full raw tool output** (entire files, full API/browser responses, unfiltered logs) into the conversation when a summary or slice would do.
4. **Don't drive lots of browser automation (screenshots, page reads) in the main thread** — push it to a sub-agent instead.
5. **Don't "resume" old giant sessions** — start fresh from a saved checkpoint/file instead.
6. **Don't worry about this repo's own files** — reading README/`.env`/docs/scripts is cheap (a rounding error across this project's entire history); that's not where tokens go.
