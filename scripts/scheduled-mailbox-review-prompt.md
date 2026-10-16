# SmartLead Mailbox + Campaign Review, twice a month (scheduled task prompt)

You are running Albert Scott's twice-monthly SmartLead review (the 1st and the 15th), unattended.
This prompt is self-contained; you have no memory of any prior run. It is read-only: never pause,
resume, edit or reassign a mailbox or campaign from this routine. It reports; a human decides.

## What it checks
- **Every connected mailbox**: SMTP/IMAP connection, warmup status, warmup reputation, warmup
  emails pulled out of spam in the trailing week, open-tracking domain DNS and TLS, and whether
  the mailbox is attached to any active campaign (healthy but idle mailboxes are spare capacity).
- **Every ACTIVE campaign, trailing 14 days**: sends, replies, reply rate, bounce rate (fix at 5%,
  watch at 3%, judged from 100 sends), no mailboxes attached, nothing sent in 14 days, and
  sequences where 90% or more of leads have finished.

## Step 0 - Repo and key
In `/home/user/smartlead-api-client` run `git fetch origin main && git checkout -B main origin/main`
(clone `https://github.com/salesmanager-crypto/smartlead-api-client.git` there first if it isn't
present). Check `test -n "$SMARTLEAD_API_KEY"` without printing it. If it isn't set, skip to
Step 2's failure email.

## Step 1 - Run the review
```
node scripts/mailbox-campaign-review.mjs --out <scratchpad>/mailbox-review
```
It prints one JSON line (`mailboxes`, `activeCampaigns`, `sent`, `replies`, `replyRate`,
`bounceRate`, `mailboxProblems`, `mailboxWarnings`, `idleMailboxes`, `campaignProblems`,
`campaignWarnings`, `trackingIssues`, `checksFailed`, `subject`) and writes `mailbox-review.html`
and `mailbox-review.txt`. A SmartLead timeout is worth one retry after 60 seconds. Never edit the
output by hand and never invent a number.

## Step 2 - Email it
Send with the Gmail connector's `send_message` to `["yoni@albertscott.com"]`:
- **Success**: `subject` from the script, `htmlBody` = the full `mailbox-review.html`, `body` = the
  full `mailbox-review.txt`.
- **Failure** (no key, or the script still fails after the retry): subject
  `SmartLead mailbox and campaign review - could not run`, and a plain `body` with the error message
  and which step failed. Yoni expects this email twice a month, so silence would read as "all
  clear".

## Step 3 - Report
Three lines at most: mailboxes and campaigns checked, how many items are "fix" vs "watch", the
14-day bounce and reply rates, and whether the email went out (with its Gmail message id). No em
dashes.
