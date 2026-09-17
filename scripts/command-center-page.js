/* ============================================================
   Shared helpers
   ============================================================ */

const STATUS_PILL = {
  ACTIVE: "pill-good", PAUSED: "pill-warn", COMPLETED: "pill-neutral",
  STOPPED: "pill-critical", DRAFTED: "pill-accent",
};

function ownerDot(id){
  const color = id===ME ? "var(--accent-2)" : (String(id)==="25109251" ? "#8C6A70" : "#B7A3A7");
  return `<span class="owner-dot" style="background:${color}"></span>`;
}
function ownerChip(id){
  return `<span class="owner-chip">${ownerDot(id)}${esc(ownerName(id))}</span>`;
}

function sortRows(rows, key, dir, getter){
  const mult = dir === "asc" ? 1 : -1;
  return [...rows].sort((a,b)=>{
    const av = getter(a,key), bv = getter(b,key);
    if(typeof av === "string") return av.localeCompare(bv) * mult;
    return ((av||0) - (bv||0)) * mult;
  });
}
function mineFirst(rows, ownerKey="owner_id"){
  return [...rows].sort((a,b)=> (b[ownerKey]===ME?1:0) - (a[ownerKey]===ME?1:0));
}
function applyModeFilter(rows, mode, ownerKey="owner_id"){
  if(mode==="mine") return rows.filter(r=>r[ownerKey]===ME);
  if(mode==="team") return rows.filter(r=>r[ownerKey]!==ME);
  return rows;
}

function modeToggleHtml(scope, current){
  const modes=[["all","All"],["mine","Mine"],["team","Team"]];
  return `<div class="toggle-group" data-toggle="${scope}">` +
    modes.map(([v,l])=>`<button data-mode="${v}" class="${current===v?"active":""}">${l}</button>`).join("") +
    `</div>`;
}

function sortableTh(label, key, state){
  const active = state.sortKey===key;
  const arrow = active ? (state.sortDir==="asc" ? "&uarr;" : "&darr;") : "";
  return `<th data-sort="${key}" class="${active?"sort-active":""}">${esc(label)}<span class="arrow">${arrow}</span></th>`;
}

/* ============================================================
   MAIN PAGE  (/)
   ============================================================ */

const mainState = { overdueMode: "all" };

function myBookRow(){
  const acts = DATA.activities;
  const mine = acts.filter(a=>a.owner_id===ME);
  const overdue = mine.filter(a=>a.days>0);
  const dueToday = mine.filter(a=>a.days===0);
  const openDeals = DATA.deals.filter(d=>d.owner_id===ME && d.status==="open");
  const oldest = overdue.length ? Math.max(...overdue.map(a=>a.days)) : 0;
  return `
  <div class="section-head"><h2>My book</h2><span class="hint">Rachel &middot; owner_id 25102178</span></div>
  <div class="grid kpi-row">
    <div class="card mybook kpi"><span class="label">Overdue</span><span class="value critical num">${overdue.length}</span><span class="foot">past due date, not done</span></div>
    <div class="card mybook kpi"><span class="label">Due today</span><span class="value warn num">${dueToday.length}</span><span class="foot">${DATA.meta.today}</span></div>
    <div class="card mybook kpi"><span class="label">Open deals</span><span class="value num">${openDeals.length}</span><span class="foot">${openDeals.length===0 ? "both of Rachel's deals are won" : "in an open pipeline stage"}</span></div>
    <div class="card mybook kpi"><span class="label">Oldest overdue</span><span class="value critical num">${oldest}d</span><span class="foot">${oldest>0 ? "since it slipped" : "nothing overdue"}</span></div>
  </div>`;
}

function overdueByRepSection(){
  const counts = DATA.overdueByOwner;
  const entries = Object.entries(counts).sort((a,b)=>b[1]-a[1]);
  const max = Math.max(...entries.map(e=>e[1]), 1);
  const rachelIsMax = entries.length && entries[0][0]===ME;
  const rows = entries.map(([id,count])=>{
    const isMe = id===ME;
    const alert = isMe && rachelIsMax;
    const pct = Math.round(count/max*100);
    return `<div class="barrow ${alert?"alert":""}">
      <div class="who">${ownerChip(id)}${isMe?'<span class="pill pill-accent" style="margin-left:2px;">You</span>':""}</div>
      <div class="track"><div class="fill" style="width:${pct}%; ${isMe && !alert ? "background:var(--accent-2);" : ""}"></div></div>
      <div class="val num">${count}</div>
    </div>`;
  }).join("");
  return `
  <div class="section-head"><h2>Team overdue, by rep</h2><span class="hint">${entries.reduce((s,e)=>s+e[1],0)} total overdue activities open right now</span></div>
  <div class="card"><div class="barlist">${rows}</div></div>`;
}

function mostOverdueSection(){
  const acts = applyModeFilter(DATA.activities.filter(a=>a.days>0), mainState.overdueMode);
  const sorted = mineFirst(sortRows(acts, "days", "desc", (a,k)=>a[k])).slice(0,10);
  const rows = sorted.map(a=>`
    <tr class="${a.owner_id===ME?"mine-row":""}">
      <td class="num" style="font-weight:800;color:var(--critical);">${a.days}d</td>
      <td>${a.due_date}</td>
      <td class="wrap">${esc(a.subject)}</td>
      <td>${esc(a.type)}</td>
      <td class="wrap">${a.contact_name?esc(a.contact_name):'<span style="color:var(--ink-faint)">Unlinked</span>'}</td>
      <td class="wrap">${a.org_name?esc(a.org_name):"—"}</td>
      <td>${ownerChip(a.owner_id)}</td>
    </tr>`).join("") || `<tr><td colspan="7" class="empty-state">Nothing in this view.</td></tr>`;
  return `
  <div class="section-head"><h2>Most overdue right now</h2>${modeToggleHtml("main-overdue", mainState.overdueMode)}</div>
  <div class="table-wrap"><table>
    <thead><tr><th>Overdue</th><th>Due date</th><th class="wrap">Subject</th><th>Type</th><th class="wrap">Contact</th><th class="wrap">Org</th><th>Owner</th></tr></thead>
    <tbody>${rows}</tbody>
  </table></div>`;
}

function yesterdaySection(){
  const y = DATA.yesterday;
  return `
  <div class="section-head"><h2>Yesterday, across channels</h2><span class="hint">${DATA.meta.yesterday}</span></div>
  <div class="grid" style="grid-template-columns:repeat(auto-fit,minmax(240px,1fr));">
    <div class="card">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <strong style="font-size:13px;">Smartlead</strong><span class="pill pill-good">Connected</span>
      </div>
      <div class="stat-inline">
        <div><b class="num">${fmtNum(y.sent)}</b> sent</div>
        <div><b class="num">${y.campaigns_sent}</b> campaigns sent</div>
        <div><b class="num">${y.replies}</b> replies</div>
        <div><b class="num">${DATA.yesterdayInterested}</b> interested</div>
      </div>
    </div>
    <div class="card" style="opacity:0.75;">
      <div style="display:flex;align-items:center;justify-content:space-between;">
        <strong style="font-size:13px;">LinkedIn</strong><span class="pill pill-neutral">Not connected</span>
      </div>
      <p style="font-size:12px;color:var(--ink-faint);margin:8px 0 0;">No outreach tool connected this session &mdash; see the LinkedIn page for what would turn this on.</p>
    </div>
  </div>`;
}

PAGE_RENDERERS["/"] = function(){
  const gap = DATA.syncGap.persistentGapCount ?? DATA.syncGap.gap;
  return `
  ${myBookRow()}
  ${gap>0 ? `<div class="finding-flag" style="margin-top:28px;"><span style="font-size:18px;">&#9888;&#65039;</span><div><strong>${gap} Smartlead ${gap===1?"reply":"replies"} never made it into Pipedrive</strong> &mdash; qualifying category, still no matching contact record, tracked until resolved (not just the last 7 days). <a href="#/smartlead">See the sync-gap detail &rarr;</a></div></div>` : ""}
  ${overdueByRepSection()}
  ${mostOverdueSection()}
  ${yesterdaySection()}
  `;
};

/* ============================================================
   SMARTLEAD PAGE  (/smartlead)
   ============================================================ */

const slState = { statusFilter: "ALL", rachelOnly: false, sortKey: "sent", sortDir: "desc" };

function campaignStatusChips(){
  const order = ["ALL","ACTIVE","PAUSED","COMPLETED","STOPPED","DRAFTED"];
  return order.map(s=>{
    const count = s==="ALL" ? DATA.campaigns.length : (DATA.campaignStatusCounts[s]||0);
    return `<button class="chip-filter ${slState.statusFilter===s?"active":""}" data-status="${s}">${s==="ALL"?"All":s} <span class="num">${count}</span></button>`;
  }).join("");
}

function rachelTagChip(){
  const count = DATA.campaigns.filter(c=>c.isRachel).length;
  return `<button class="chip-filter ${slState.rachelOnly?"active":""}" id="sl-rachel-chip" style="${slState.rachelOnly?"background:var(--accent-2);border-color:var(--accent-2);":""}">
    <span class="owner-dot" style="background:${slState.rachelOnly?"#fff":"var(--accent-2)"};display:inline-block;margin-right:5px;"></span>Tagged &ldquo;Rachel&rdquo; <span class="num">${count}</span>
  </button>`;
}

function campaignRowsHtml(){
  let rows = slState.statusFilter==="ALL" ? DATA.campaigns : DATA.campaigns.filter(c=>c.status===slState.statusFilter);
  if(slState.rachelOnly) rows = rows.filter(c=>c.isRachel);
  rows = sortRows(rows, slState.sortKey, slState.sortDir, (c,k)=>c[k]);
  if(rows.length===0) return `<tr><td colspan="9" class="empty-state">No campaigns in this status.</td></tr>`;
  return rows.map(c=>`
    <tr>
      <td class="wrap" style="min-width:220px;">${esc(c.name)}</td>
      <td><span class="pill ${STATUS_PILL[c.status]||"pill-neutral"}">${esc(c.status)}</span></td>
      <td>${fmtDate(c.created_at)}</td>
      <td class="num">${fmtNum(c.sent)}</td>
      <td class="num">${fmtNum(c.replies)}</td>
      <td class="num">${fmtNum(c.bounces)}</td>
      <td class="num">${fmtNum(c.leads)}</td>
      <td class="num">${fmtNum(c.interested)}</td>
      <td class="num">${fmtPct(c.reply_rate)}</td>
      <td class="num">${fmtPct(c.bounce_rate)}</td>
    </tr>`).join("");
}

function campaignTableSection(){
  const cols = [["name","Campaign"],["status","Status"],["created_at","Created"],["sent","Sent"],["replies","Replies"],["bounces","Bounces"],["leads","Leads"],["interested","Interested"],["reply_rate","Reply %"],["bounce_rate","Bounce %"]];
  return `
  <div class="section-head"><h2>Campaigns</h2><span class="hint">${DATA.campaigns.length} total</span></div>
  <div class="filterbar" id="sl-status-chips">${campaignStatusChips()}<span style="width:1px;align-self:stretch;background:var(--border);margin:0 2px;"></span>${rachelTagChip()}</div>
  <div class="table-wrap"><table id="sl-campaign-table">
    <thead><tr>${cols.map(([k,l])=>sortableTh(l,k,slState)).join("")}</tr></thead>
    <tbody>${campaignRowsHtml()}</tbody>
  </table></div>`;
}

function syncGapBanner(){
  const g = DATA.syncGap;
  const persistent = g.persistentGaps ?? [];
  const gapCount = g.persistentGapCount ?? g.gap;
  const good = gapCount===0;
  const watchlist = persistent.length ? `
    <div class="card" style="margin-top:14px;border-color:var(--critical);">
      <div style="font-size:12.5px;font-weight:700;color:var(--critical);margin-bottom:8px;">Open sync-gap watchlist &mdash; tracked until resolved, independent of the 7-day window below</div>
      <div class="table-wrap" style="border-color:var(--critical);"><table>
        <thead><tr><th>Lead</th><th class="wrap">Email</th><th class="wrap">Campaign</th><th>Category</th><th>First seen</th><th>Days open</th></tr></thead>
        <tbody>${persistent.map(p=>`<tr>
          <td>${esc(p.lead_name||"—")}</td>
          <td class="wrap">${esc(p.email)}</td>
          <td class="wrap">${esc(p.campaign_name||"—")}</td>
          <td><span class="pill pill-neutral">${esc(p.category)}</span></td>
          <td>${fmtDate(p.first_seen)}</td>
          <td class="num" style="font-weight:800;color:var(--critical);">${p.days_open}d</td>
        </tr>`).join("")}</tbody>
      </table></div>
    </div>` : "";
  return `
  <div class="grid kpi-row">
    <div class="card kpi" style="${good?"":"border-color:var(--critical);"}">
      <span class="label">Sync gaps (open)</span><span class="value ${good?"good":"critical"} num">${gapCount}</span>
      <span class="foot">${good ? "every qualifying reply made it to Pipedrive" : "qualifying reply, still no Pipedrive record"}</span>
    </div>
    <div class="card kpi"><span class="label">Synced (7d)</span><span class="value good num">${g.synced}</span><span class="foot">qualifying + matched</span></div>
    <div class="card kpi"><span class="label">Uncategorized (7d)</span><span class="value num">${g.uncategorized}</span><span class="foot">no category applied yet</span></div>
    <div class="card kpi"><span class="label">Mailboxes / domains</span><span class="value num">${DATA.mailboxCount} <span style="font-size:16px;color:var(--ink-faint);">/ ${DATA.sendingDomainCount}</span></span><span class="foot">sending inboxes / domains</span></div>
  </div>
  ${watchlist}`;
}

function dailyInboxLog(){
  const byDay = {};
  DATA.masterInboxReplies7d.forEach(r=>{
    const day = (r.time||"").slice(0,10) || "unknown";
    (byDay[day] = byDay[day] || []).push(r);
  });
  const days = Object.keys(byDay).sort().reverse();
  const SYNC_PILL = { synced:"pill-good", gap:"pill-critical", uncategorized:"pill-neutral", none:"pill-neutral" };
  const sections = days.map(day=>{
    const rows = byDay[day].sort((a,b)=>(b.time||"").localeCompare(a.time||""));
    const gapCount = rows.filter(r=>r.sync_status==="gap").length;
    const body = rows.map(r=>`
      <tr class="${r.sync_status==="gap"?"mine-row":""}" style="${r.sync_status==="gap"?"background:var(--critical-soft);":""}">
        <td>${fmtDateTime(r.time)}</td>
        <td class="wrap">${esc(r.lead_name||"—")}</td>
        <td class="wrap">${esc(r.email||"—")}</td>
        <td class="wrap">${esc(r.campaign_name||"—")}</td>
        <td>${r.category ? `<span class="pill pill-neutral">${esc(r.category)}</span>` : '<span class="pill pill-neutral">Uncategorized</span>'}</td>
        <td><span class="pill ${SYNC_PILL[r.sync_status]}">${r.sync_status}</span></td>
      </tr>`).join("");
    return `
    <details class="day-log" ${day===days[0]?"open":""}>
      <summary><span>${fmtDate(day+"T00:00:00Z")} <span style="color:var(--ink-faint);font-weight:600;">&middot; ${rows.length} ${rows.length===1?"reply":"replies"}</span></span>
        <span class="day-log-stats">${gapCount>0?`<span class="pill pill-critical">${gapCount} gap</span>`:'<span class="pill pill-good">0 gaps</span>'}</span>
      </summary>
      <div class="day-log-body"><div class="table-wrap"><table>
        <thead><tr><th>Time</th><th class="wrap">Lead</th><th class="wrap">Email</th><th class="wrap">Campaign</th><th>Category</th><th>Sync</th></tr></thead>
        <tbody>${body}</tbody>
      </table></div></div>
    </details>`;
  }).join("");
  return `
  <div class="section-head"><h2>Daily inbox log</h2><span class="hint">Trailing 7 days &middot; ${DATA.masterInboxReplies7d.length} replies</span></div>
  ${sections || '<div class="empty-state">No replies in the last 7 days.</div>'}`;
}

PAGE_RENDERERS["/smartlead"] = function(){
  return `
  ${syncGapBanner()}
  ${campaignTableSection()}
  <div style="margin-top:36px;"></div>
  ${dailyInboxLog()}
  `;
};

/* ============================================================
   PIPEDRIVE PAGE  (/pipedrive)
   ============================================================ */

const pdState = { tab: "overdue", mode: "all", rep: "all", query: "" };

function pdBucketRows(tab){
  if(tab==="overdue") return DATA.activities.filter(a=>a.days>0);
  if(tab==="today") return DATA.activities.filter(a=>a.days===0);
  return DATA.activities.filter(a=>a.days<0 && a.days>=-14);
}

function pdFilteredRows(){
  let rows = pdBucketRows(pdState.tab);
  rows = applyModeFilter(rows, pdState.mode);
  if(pdState.rep!=="all") rows = rows.filter(a=>String(a.owner_id)===pdState.rep);
  if(pdState.query){
    const q = pdState.query.toLowerCase();
    rows = rows.filter(a=>
      (a.subject||"").toLowerCase().includes(q) ||
      (a.contact_name||"").toLowerCase().includes(q) ||
      (a.org_name||"").toLowerCase().includes(q)
    );
  }
  const sortKey = pdState.tab==="upcoming" ? "days" : "days";
  const sortDir = pdState.tab==="upcoming" ? "asc" : "desc";
  return mineFirst(sortRows(rows, sortKey, sortDir, (a,k)=>a[k]));
}

function pdActivityTableHtml(){
  const rows = pdFilteredRows();
  const body = rows.map(a=>{
    const daysLabel = a.days>0 ? `<span style="color:var(--critical);font-weight:800;">${a.days}d over</span>`
      : a.days===0 ? `<span style="color:var(--warn);font-weight:800;">Today</span>`
      : `<span style="color:var(--ink-soft);font-weight:700;">in ${-a.days}d</span>`;
    return `<tr class="${a.owner_id===ME?"mine-row":""}">
      <td>${daysLabel}</td>
      <td>${a.due_date}</td>
      <td class="wrap">${esc(a.subject)}</td>
      <td>${esc(a.type)}</td>
      <td class="wrap">${a.contact_name?esc(a.contact_name):'<span style="color:var(--ink-faint)">Unlinked</span>'}</td>
      <td class="wrap">${a.org_name?esc(a.org_name):"—"}</td>
      <td>${ownerChip(a.owner_id)}</td>
    </tr>`;
  }).join("");
  return body || `<tr><td colspan="7" class="empty-state">No activities match this view.</td></tr>`;
}

function pdActivitiesSection(){
  const tabs = [["overdue","Overdue"],["today","Due today"],["upcoming","Upcoming (14d)"]];
  const tabBar = tabs.map(([k,l])=>{
    const count = pdBucketRows(k).length;
    return `<button class="tab ${pdState.tab===k?"active":""}" data-tab="${k}">${l} <span class="count">${count}</span></button>`;
  }).join("");
  const repOptions = ["all",...Object.keys(OWNERS)].map(id=>
    `<option value="${id}" ${pdState.rep===id?"selected":""}>${id==="all"?"All reps":ownerName(id)}</option>`).join("");
  return `
  <div class="section-head"><h2>Activities</h2>${modeToggleHtml("pd-activities", pdState.mode)}</div>
  <div class="tabbar" id="pd-tabbar">${tabBar}</div>
  <div class="filterbar">
    <select id="pd-rep-filter" class="chip-filter" style="cursor:pointer;">${repOptions}</select>
    <div class="searchbox"><svg viewBox="0 0 24 24"><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>
      <input id="pd-search" type="text" placeholder="Search subject, contact, org&hellip;" value="${esc(pdState.query)}">
    </div>
  </div>
  <div class="table-wrap"><table id="pd-activity-table">
    <thead><tr><th>Status</th><th>Due date</th><th class="wrap">Subject</th><th>Type</th><th class="wrap">Contact</th><th class="wrap">Org</th><th>Owner</th></tr></thead>
    <tbody id="pd-activity-tbody">${pdActivityTableHtml()}</tbody>
  </table></div>`;
}

const dealsState = { sortKey: "add_time", sortDir: "desc" };
const STATUS_PILL_DEAL = { won:"pill-good", lost:"pill-critical", open:"pill-accent" };

function dealsRowsHtml(){
  const rows = mineFirst(sortRows(DATA.deals, dealsState.sortKey, dealsState.sortDir, (d,k)=>d[k]));
  return rows.map(d=>`
    <tr class="${d.owner_id===ME?"mine-row":""}">
      <td class="wrap">${esc(d.title)}</td>
      <td>${esc(d.stage)}</td>
      <td><span class="pill ${STATUS_PILL_DEAL[d.status]||"pill-neutral"}">${esc(d.status)}</span></td>
      <td class="num">$${fmtNum(d.value)}</td>
      <td>${fmtDate(d.add_time)}</td>
      <td>${d.close_time?fmtDate(d.close_time):"—"}</td>
      <td>${ownerChip(d.owner_id)}</td>
    </tr>`).join("");
}

function pdDealsSection(){
  const cols=[["title","Deal"],["stage","Stage"],["status","Status"],["value","Value"],["add_time","Added"],["close_time","Closed"]];
  return `
  <div class="section-head"><h2>Deals</h2><span class="hint">${DATA.deals.length} total</span></div>
  <div class="table-wrap"><table id="pd-deals-table">
    <thead><tr>${cols.map(([k,l])=>sortableTh(l,k,dealsState)).join("")}<th>Owner</th></tr></thead>
    <tbody>${dealsRowsHtml()}</tbody>
  </table></div>`;
}

PAGE_RENDERERS["/pipedrive"] = function(){
  return `
  <div class="grid kpi-row">
    <div class="card kpi"><span class="label">Open activities</span><span class="value num">${DATA.activities.length}</span><span class="foot">${DATA.activityTypeCounts.call||0} calls &middot; ${DATA.activityTypeCounts.task||0} tasks &middot; ${DATA.activityTypeCounts.meeting||0} meetings</span></div>
    <div class="card kpi"><span class="label">Total leads</span><span class="value num">${fmtNum(DATA.totalLeads)}</span><span class="foot">Rachel ${DATA.leadsByOwner["25102178"]||0} &middot; Yoni ${DATA.leadsByOwner["25109251"]||0} &middot; Rep 3 ${DATA.leadsByOwner["26939288"]||0}</span></div>
    <div class="card kpi"><span class="label">Total persons</span><span class="value num">${fmtNum(DATA.totalPersons)}</span><span class="foot">contacts in Pipedrive</span></div>
    <div class="card kpi"><span class="label">Total organizations</span><span class="value num">${fmtNum(DATA.totalOrgs)}</span><span class="foot">companies in Pipedrive</span></div>
  </div>
  ${pdActivitiesSection()}
  <div style="margin-top:36px;"></div>
  ${pdDealsSection()}
  `;
};

/* ============================================================
   LINKEDIN PAGE  (/linkedin)
   ============================================================ */

PAGE_RENDERERS["/linkedin"] = function(){
  return `
  <div class="placeholder-page">
    <div class="card placeholder-card">
      <div class="icon">${ICONS.link}</div>
      <h3>LinkedIn isn't connected</h3>
      <p>No LinkedIn outreach tool or connector was available to this session, so there's no campaign, connection, or reply data to show.</p>
      <div class="needlist">To turn this page on, connect whatever tool runs your LinkedIn outreach (e.g. an MCP connector for it) and re-run the refresh. Once connected, this page will show campaign name, status, start date, list name, sender count, total leads, processed / pending, connections sent / accepted, messages sent, replies, and failed &mdash; per the funnel spec.</div>
    </div>
  </div>`;
};

/* ============================================================
   SEO / GEO PAGE  (/seo)
   ============================================================ */

PAGE_RENDERERS["/seo"] = function(){
  const s = DATA.seoGeo;
  const listRows = s.listicleVisibility.queries.map(q=>`
    <tr><td class="wrap">${esc(q.query)}</td><td>${q.present ? '<span class="pill pill-good">Present</span>' : '<span class="pill pill-critical">Not found</span>'}</td></tr>`).join("");
  const notFoundAny = s.listicleVisibility.queries.every(q=>!q.present);
  return `
  ${notFoundAny ? `<div class="finding-flag"><span style="font-size:18px;">&#9888;&#65039;</span><div><strong>albertscott.com did not appear</strong> in any of the 3 "best Amazon agency" searches checked today &mdash; visibility on these head terms currently belongs to competitors.</div></div>` : ""}

  <div class="two-col">
    <div class="card">
      <div class="section-head" style="margin-top:0;"><h2>Listicle &amp; AI visibility</h2><span class="hint">Checked ${fmtDateTime(s.listicleVisibility.checked_at)}</span></div>
      <div class="table-wrap"><table>
        <thead><tr><th class="wrap">Query</th><th>albertscott.com</th></tr></thead>
        <tbody>${listRows}</tbody>
      </table></div>
      <p style="font-size:12px;color:var(--ink-faint);margin:12px 0 6px;">Top-ranking competitors seen across these searches:</p>
      <div style="display:flex;flex-wrap:wrap;gap:6px;">${s.listicleVisibility.topCompetitors.map(c=>`<span class="pill pill-neutral">${esc(c)}</span>`).join("")}</div>
    </div>

    <div class="card placeholder-card" style="text-align:left;">
      <h3 style="font-size:14px;">Site health</h3>
      <p>${esc(s.siteHealth.note)}</p>
      <div class="needlist">To turn this on: run this refresh from an environment whose network egress isn't blocked for albertscott.com, or grant direct fetch access in this session.</div>
    </div>
  </div>

  <div class="card placeholder-card" style="margin-top:16px; text-align:left; max-width:none;">
    <h3 style="font-size:14px;">Keyword position tracking</h3>
    <p>${esc(s.keywordPositions.note)}</p>
    <div class="needlist">To turn this on: enable the Semrush connector for this chat (it's installed for the org, just not switched on here), then re-run the refresh &mdash; this will show target keyword positions and the current top-ranking competitor for each.</div>
  </div>
  `;
};

/* ============================================================
   RESOURCES PAGE  (/resources)
   ============================================================ */

PAGE_RENDERERS["/resources"] = function(){
  return `
  <div class="placeholder-page">
    <div class="card placeholder-card">
      <div class="icon">${ICONS.box}</div>
      <h3>No resources data yet</h3>
      <p>${esc(DATA.resources.note)}</p>
      <div class="needlist">To turn this page on, share: a vendor cost sheet (tool/subscription, monthly cost, owner) and the sending-domain wave schedule (which domains warm up on which dates). Re-run the refresh once you have it.</div>
    </div>
  </div>`;
};

/* ============================================================
   INTERACTION WIRING
   ============================================================ */

function wirePageInteractions(path){
  if(path==="/"){
    document.querySelectorAll('[data-toggle="main-overdue"] button').forEach(btn=>{
      btn.addEventListener("click", ()=>{ mainState.overdueMode = btn.dataset.mode; rerenderSection("/", "main-overdue-section", mostOverdueSection); });
    });
  }
  if(path==="/smartlead"){
    document.querySelectorAll('#sl-status-chips [data-status]').forEach(btn=>{
      btn.addEventListener("click", ()=>{
        slState.statusFilter = btn.dataset.status;
        document.getElementById("view").innerHTML = PAGE_RENDERERS["/smartlead"]();
        wirePageInteractions("/smartlead");
      });
    });
    const rachelChip = document.getElementById("sl-rachel-chip");
    if(rachelChip) rachelChip.addEventListener("click", ()=>{
      slState.rachelOnly = !slState.rachelOnly;
      document.getElementById("view").innerHTML = PAGE_RENDERERS["/smartlead"]();
      wirePageInteractions("/smartlead");
    });
    document.querySelectorAll('#sl-campaign-table thead th[data-sort]').forEach(th=>{
      th.addEventListener("click", ()=>{
        const key = th.dataset.sort;
        slState.sortDir = (slState.sortKey===key && slState.sortDir==="desc") ? "asc" : "desc";
        slState.sortKey = key;
        document.getElementById("view").innerHTML = PAGE_RENDERERS["/smartlead"]();
        wirePageInteractions("/smartlead");
      });
    });
  }
  if(path==="/pipedrive"){
    document.querySelectorAll('[data-toggle="pd-activities"] button').forEach(btn=>{
      btn.addEventListener("click", ()=>{ pdState.mode = btn.dataset.mode; fullRerender("/pipedrive"); });
    });
    document.querySelectorAll('#pd-tabbar [data-tab]').forEach(btn=>{
      btn.addEventListener("click", ()=>{ pdState.tab = btn.dataset.tab; fullRerender("/pipedrive"); });
    });
    const repSel = document.getElementById("pd-rep-filter");
    if(repSel) repSel.addEventListener("change", ()=>{ pdState.rep = repSel.value; fullRerender("/pipedrive"); });
    const searchBox = document.getElementById("pd-search");
    if(searchBox){
      searchBox.addEventListener("input", ()=>{
        pdState.query = searchBox.value;
        document.getElementById("pd-activity-tbody").innerHTML = pdActivityTableHtml();
      });
      searchBox.focus();
      searchBox.setSelectionRange(searchBox.value.length, searchBox.value.length);
    }
    document.querySelectorAll('#pd-deals-table thead th[data-sort]').forEach(th=>{
      th.addEventListener("click", ()=>{
        const key = th.dataset.sort;
        dealsState.sortDir = (dealsState.sortKey===key && dealsState.sortDir==="desc") ? "asc" : "desc";
        dealsState.sortKey = key;
        fullRerender("/pipedrive");
      });
    });
  }
}

function fullRerender(path){
  document.getElementById("view").innerHTML = PAGE_RENDERERS[path]();
  wirePageInteractions(path);
}
function rerenderSection(path, id, fn){
  fullRerender(path);
}
