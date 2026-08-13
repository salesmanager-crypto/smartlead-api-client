# Email Deliverability Roles & Responsibilities

Reference doc for the job titles and responsibilities that map to the deliverability
work this repo automates (inbox health checks, warmup monitoring, domain blocklist
management). Useful when scoping who owns what on the team, or when writing a job
posting for deliverability help.

---

## Job Titles

| Title | Focus |
|---|---|
| **Email Deliverability Specialist** | Hands-on, day-to-day role: ongoing monitoring, spam troubleshooting, and inbox placement. |
| **Email Deliverability Engineer** | More technical: building, maintaining, and debugging mail servers and sending infrastructure. |
| **Email Authentication Specialist** | Sets up and manages DNS-level security protocols (SPF, DKIM, DMARC). |
| **Deliverability Operations Manager** | Oversees monitoring alerts, blocklist remediations, and incident responses across a whole program. |

Source: [suped.com — appropriate job titles for email deliverability](https://www.suped.com/learn/email-deliverability/what-are-some-appropriate-job-titles-for-someone-who-specializes-in-email-deliverability)

---

## Core Responsibilities

- **Authentication Configuration** — setting up and verifying DNS records like SPF, DKIM, and DMARC.
  ([suped.com](https://www.suped.com/learn/email-deliverability/what-are-some-appropriate-job-titles-for-someone-who-specializes-in-email-deliverability), [belkins.io](https://belkins.io/deliverability-approach))
- **Reputation Management** — fixing blocklist/blacklist issues and managing domain health.
  ([suped.com](https://www.suped.com/learn/email-deliverability/what-are-some-appropriate-job-titles-for-someone-who-specializes-in-email-deliverability))
- **Inbox Diagnostics** — analyzing bounce rates, spam complaints, and placement rates across major
  mailbox providers like Gmail and Outlook.
  ([powerdmarc.com](https://powerdmarc.com/email-deliverability-consultant/), [upwork.com](https://www.upwork.com/hire/email-deliverability-consulting-freelancers/))

---

## How this maps to this repo's tooling

| Responsibility | Where it's handled here |
|---|---|
| Reputation management / domain health | `scripts/daily-deliverability-check.mjs` (warmup status, spam-save drift), `scripts/flagged-domain-campaigns.mjs`, `client.getAllInboxHealth()` |
| Inbox diagnostics | `node src/cli.js inboxes:health`, `node src/cli.js inboxes:warmup-stats <id>`, `client.getEmailAccountWarmupStats()` |
| Authentication configuration (SPF/DKIM/DMARC) | Not covered by the Smartlead API — this is DNS-side and configured with the domain registrar/host, outside this client |

This repo's automation covers the *monitoring* half of the Email Deliverability
Specialist role (warmup health, spam-complaint drift, blocklist hygiene) rather than
the DNS-authentication or mail-server engineering half — those stay manual/registrar-side.
