export const meta = {
  name: 'lead-recap-overview',
  description: 'Build a Gmail+SmartLead recap/overview for every lead across 3 Pipedrive re-engagement sheet tabs',
  phases: [
    { title: 'Recap', detail: 'one agent per ~15-lead batch: Gmail search + SmartLead cross-reference + synopsis' },
  ],
}

// Run via the Workflow tool (Claude Code), not `node` directly -- agent()/parallel()/phase()
// only exist inside that runtime. See docs/Lead-Recap-Overview-Workflow.md for the full
// pipeline (extracting the sheet, building the SmartLead lookup, running this, assembling
// the output workbook) and for how to pass `args`.
//
// args shape:
//   {
//     manifest: [{ tab, batchIndex, file, count }, ...],  // file = absolute path to a JSON
//                                                          // array of lead rows, each with
//                                                          // a "_key" field (lowercased email)
//     smartleadLookupFile: "<absolute path>",              // JSON object keyed by lowercased
//                                                          // email -> SmartLead campaign history,
//                                                          // built by lead-recap-smartlead-lookup.mjs
//   }

const RECAP_SCHEMA = {
  type: 'object',
  properties: {
    recaps: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          key: { type: 'string', description: "the lead's _key value from the input file, echoed back verbatim" },
          overview: { type: 'string', description: '2-4 sentence recap: what happened, where things stand now, a short synopsis useful for Pipedrive re-engagement' },
          current_status: { type: 'string', description: 'short 2-6 word status tag' },
          last_touchpoint: { type: 'string', description: 'YYYY-MM-DD of the most recent real signal found, or "none"' },
        },
        required: ['key', 'overview', 'current_status', 'last_touchpoint'],
      },
    },
  },
  required: ['recaps'],
}

function buildPrompt(batch, smartleadLookupFile) {
  return `You are building a lead re-engagement recap for Albert Scott's SmartLead <-> Pipedrive re-engagement project. Background doc (optional): /home/user/smartlead-api-client/docs/Smartlead-Pipedrive-Automation-Workflow.md

Read the JSON array of lead rows at ${batch.file} (Read tool, or "cat ${batch.file} | jq" via Bash). It has ${batch.count} rows from the "${batch.tab}" tab of a Pipedrive re-engagement spreadsheet. Each row is a plain object with whatever that tab already recorded (Pipedrive activity counts/dates, Owner, SmartLead category, Salesforce Lead Status, etc.) plus a "_key" field: the lead's primary email address, lowercased.

Also read ${smartleadLookupFile} (jq is strongly recommended given its size -- do NOT dump it whole into context; look up individual keys with e.g. \`jq '.["someone@example.com"]' ${smartleadLookupFile}\`). It's a JSON object keyed by lowercased email, giving each matched lead's SmartLead campaign history: campaign name, category, and the last SENT/REPLY message (subject/snippet/from) per campaign. Not every lead in your batch will have an entry there -- that just means SmartLead never touched them directly, or the email doesn't match a SmartLead record. That's expected and fine.

For EACH of the ${batch.count} lead rows in your batch:
1. Search Gmail for correspondence with that person: mcp__Gmail__search_threads with query \`(from:<email> OR to:<email>)\`, pageSize 10. The search preview snippets (subject/sender/date/snippet) are usually enough by themselves -- only call mcp__Gmail__get_thread on a specific thread when the snippet doesn't make the outcome clear and understanding it actually matters (e.g. did they book a call? did they say no? is this a real reply or an autoresponder?).
2. Cross-reference with that email's SmartLead lookup entry, if any. Real message content there is a strong primary source -- but watch for messages that are actually bounces/mailer-daemon notices/out-of-office autoresponders rather than a real human reply, and say so rather than treating them as genuine interest.
3. Use the row's own existing sheet fields (Pipedrive activity dates/types, SmartLead category, Salesforce Lead Status, Owner, etc.) as further signal on relationship history.

Then write, per lead:
- overview: 2-4 plain-English sentences covering (a) what happened with this lead -- how they were first engaged and any real conversation/reply/meeting, (b) where things stand now (never replied / went cold after interest / said not now / booked a call / asked to be removed / bounced / etc.), (c) anything concretely useful for a Pipedrive re-engagement outreach -- a specific objection, timing, or interest they mentioned, if any. If you genuinely found nothing (no Gmail thread, no SmartLead record, sheet shows zero activity), say that plainly rather than inventing detail -- e.g. "No email or SmartLead history found; sheet shows no Pipedrive activity either -- likely an unworked contact." is a valid, useful answer.
- current_status: a short (2-6 word) tag, e.g. "Never contacted", "Sent, no reply", "Replied - interested", "Replied - not now", "Out of office / bounced", "Booked a call", "Asked to stop contact", "Ongoing conversation".
- last_touchpoint: the YYYY-MM-DD date of the most recent real signal you found across Gmail/SmartLead/sheet data, or "none" if nothing found.

Return recaps for ALL ${batch.count} leads in the batch -- one entry per lead, each keyed by its exact "_key" value from the input file (echo it back verbatim, unmodified, so results can be matched back to rows). Do not skip any lead, even ones with nothing found.`
}

phase('Recap')
log(`Processing ${args.manifest.length} batches (${args.manifest.reduce((s, b) => s + b.count, 0)} leads total) across ${new Set(args.manifest.map(b => b.tab)).size} tabs`)

const results = await parallel(
  args.manifest.map((batch) => () =>
    agent(buildPrompt(batch, args.smartleadLookupFile), {
      label: `${batch.tab}-${String(batch.batchIndex).padStart(3, '0')}`,
      phase: 'Recap',
      schema: RECAP_SCHEMA,
    })
      .then((r) => ({ tab: batch.tab, batchIndex: batch.batchIndex, recaps: r?.recaps || [] }))
      .catch((err) => ({ tab: batch.tab, batchIndex: batch.batchIndex, recaps: [], error: String(err) }))
  )
)

const settled = results.filter(Boolean)
const failed = settled.filter((r) => r.error || r.recaps.length === 0)
const totalRecaps = settled.reduce((s, r) => s + r.recaps.length, 0)
log(`Done: ${settled.length}/${args.manifest.length} batches returned, ${totalRecaps} recaps total, ${failed.length} batches empty/errored`)

return { results: settled }
