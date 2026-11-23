'use strict';

const main = document.getElementById('main');
const caseIds = ['headphones', 'monitor', 'speaker'];
const caseLabels = { headphones: 'Headphones', monitor: 'Monitor', speaker: 'Speaker' };
const previewNames = { headphones: 'Arc One headphones', monitor: 'Forma 27 monitor', speaker: 'Tide Mini speaker' };
const states = {
  pilot: { name: 'Advance to pilot', filter: 'Pilot', icon: 'check' },
  collect: { name: 'Collect more evidence', filter: 'Collect', icon: 'time' },
  hold: { name: 'Hold for investigation', filter: 'Hold', icon: 'pause' }
};
const icons = {
  headphones: '<path d="M4 14v-2a8 8 0 0 1 16 0v2M4 12h2a2 2 0 0 1 2 2v3a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-3a2 2 0 0 1 1-2Zm16 0h-2a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-1-2Z"/>',
  monitor: '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8m-4-4v4"/>',
  speaker: '<rect x="6" y="2.7" width="12" height="18.6" rx="3"/><circle cx="12" cy="15" r="3"/><path d="M10 7h4"/>',
  check: '<path d="m4 12 5 5L20 6"/>',
  time: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7v6l3 2"/>',
  pause: '<path d="M8 5v14m8-14v14" stroke-width="2.6"/>',
  file: '<path d="M6 3h8l4 4v14H6zM14 3v5h4M9 12h6m-6 4h5"/>',
  download: '<path d="M12 3v12m-5-5 5 5 5-5M4 17v4h16v-4"/>',
  inspect: '<path d="M3 3h7v7H3zm11 0h7v7h-7zM3 14h7v7H3zm11 0h7v7h-7z"/>'
};
const fmt = new Intl.NumberFormat('en-GB');
const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'})[char]);
const icon = name => '<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">' + (icons[name] || '') + '</svg>';
const tag = label => '<span class="tag">' + esc(label) + '</span>';
const signed = (n, digits = 2) => (n > 0 ? '+' : n < 0 ? '−' : '') + Math.abs(n).toFixed(digits);
const pp = n => signed(n) + ' pp';
const pct = p => (100 * p).toFixed(1) + '%';
const pval = value => value < 0.001 ? '< 0.001' : value.toFixed(3);
const lensLabels = { content: 'Content & answers', experiment: 'Shopper experiment', referrals: 'Traffic & citations', observed: 'Controlled AI run' };
let experiments, geo, observed, referrals;
let selection = 'headphones';
let worklistFilter = 'all';
let questionId = '';
let answerRepeat = 1;
let observedPair = '';
let currentPath = '';

function stateOf(record) {
  return Object.keys(states).find(key => states[key].name === record.decision) || 'hold';
}
function badge(record) {
  const key = stateOf(record);
  return '<span class="status state-' + key + '">' + icon(states[key].icon) + esc(record.decision) + '</span>';
}
function nameOf(id) {
  return geo.cases[id].name || previewNames[id];
}
function say(text) { document.getElementById('notice').textContent = text; }
function hero(eyebrow, title, intro, action = '') {
  return '<div class="hero"><div><div class="eyebrow">' + esc(eyebrow) + '</div><h1>' + esc(title) +
    '</h1><p class="intro">' + esc(intro) + '</p></div>' + action + '</div>';
}
function numberRange(record) {
  return signed(record.ci_low_pp) + ' to ' + pp(record.ci_high_pp);
}
function sectionLead(heading, subtitle) {
  return '<div class="section-lead"><h2>' + esc(heading) + '</h2><p class="section-desc">' + esc(subtitle) + '</p></div>';
}
function productSelect(section, lens = '') {
  const options = caseIds.map(id => '<option value="' + id + '"' + (id === selection ? ' selected' : '') + '>' + esc(nameOf(id)) + '</option>').join('');
  return '<label class="field-inline">Product <select id="case-select" data-section="' + section + '" data-lens="' +
    lens + '">' + options + '</select></label>';
}
function chart() {
  const records = Object.values(experiments.cases);
  const ticks = [];
  const low = Math.min(-1, Math.floor(Math.min(...records.map(r => r.ci_low_pp))));
  const high = Math.max(1, Math.ceil(Math.max(...records.map(r => r.ci_high_pp))));
  const position = n => (n - low) * 100 / (high - low);
  const step = high - low > 7 ? 2 : 1;
  for (let i = Math.ceil(low / step) * step; i <= high; i += step) ticks.push(i);
  const lines = ticks.map(n => '<i class="gridline ' + (n === 0 ? 'zero' : '') + '" style="left:' + position(n) + '%"></i>').join('');
  const rows = caseIds.map(id => {
    const r = experiments.cases[id];
    const flagged = stateOf(r) === 'hold' ? ' flagged' : '';
    return '<div class="forest-label">' + caseLabels[id] + '</div><div class="lane" role="img" aria-label="' +
      esc(caseLabels[id] + ': ' + pp(r.effect_pp) + ', 95% interval ' + numberRange(r) + '. ' + r.decision + '.') + '">' + lines +
      '<i class="interval' + flagged + '" style="left:' + position(r.ci_low_pp) + '%;width:' +
      (position(r.ci_high_pp) - position(r.ci_low_pp)) + '%"></i><i class="estimate' + flagged +
      '" style="left:' + position(r.effect_pp) + '%"></i></div>';
  }).join('');
  const axis = ticks.map(n => '<span style="left:' + position(n) + '%">' + signed(n, 0) + '</span>').join('');
  return '<section class="chart-card"><div class="chart-heading"><div><h2>Add-to-cart effect</h2>' +
    '<p class="chart-desc">Treatment minus control in percentage points · 95% intervals</p></div>' + tag('Simulated') +
    '</div><div class="forest">' + rows + '<div></div><div class="axis" aria-hidden="true">' + axis +
    '</div></div><p class="chart-foot"><i></i> Amber indicates a failed allocation check.</p></section>';
}
function queue() {
  const records = Object.values(experiments.cases);
  const rows = Object.entries(states).map(([key, value]) => '<div class="queue-row"><span class="status-icon state-' +
    key + '">' + icon(value.icon) + '</span><span class="queue-label">' + value.name + '</span><strong>' +
    records.filter(record => stateOf(record) === key).length + '</strong></div>').join('');
  return '<section class="queue-card"><h2>Review queue</h2><div class="queue-rows">' + rows +
    '</div><p class="queue-foot">One fixed-horizon experiment per product.</p></section>';
}
function caseRows() {
  return caseIds.filter(id => worklistFilter === 'all' || stateOf(experiments.cases[id]) === worklistFilter).map(id => {
    const r = experiments.cases[id];
    return '<tr><td class="product"><div class="product-wrap"><span class="product-icon ' + id + '">' + icon(id) +
      '</span><div><a class="product-link" href="#evidence/' + id + '">' + esc(nameOf(id)) +
      '</a><span class="subline">' + esc(r.retailer) + '</span></div></div></td><td class="eff num">' + pp(r.effect_pp) +
      '</td><td class="outcome">' + badge(r) + '</td><td class="open-case"><a class="review-link" href="#evidence/' + id +
      '" aria-label="Review ' + esc(nameOf(id)) + '">Review case</a></td></tr>';
  }).join('');
}
function evidenceLink(id, text) { return '<a class="button" href="#evidence/' + id + '">' + icon('file') + esc(text) + '</a>'; }
function overview() {
  const filters = [['all','All cases'], ...Object.entries(states).map(([key, v]) => [key, v.filter])].map(([key,label]) =>
    '<button class="filter" type="button" data-filter="' + key + '" aria-pressed="' + (worklistFilter === key) + '">' + label + '</button>').join('');
  return hero('Retail content research', 'Content decision desk', 'Which product-page changes deserve a wider pilot? Follow each recommendation from a buyer’s question to the shopper experiment.', evidenceLink('headphones','Review first case')) +
    '<div class="overview-grid">' + chart() + queue() + '</div><section class="worklist"><div class="section-heading"><div><h2>Case worklist</h2><p class="section-desc">Three fictional UK retail cases with reproducible results.</p></div>' +
    '<div class="filters" role="group" aria-label="Filter case worklist">' + filters + '</div></div><div class="table-shell"><table class="case-table"><thead><tr><th>Product / retailer</th><th>Cart effect</th><th>Trial decision</th><th><span class="sr">Action</span></th></tr></thead><tbody id="case-rows">' +
    caseRows() + '</tbody></table></div></section><aside class="info-strip"><div><strong>Controlled AI reading test</strong><p>Inspect the captured answers from a separate, source-restricted model exercise.</p></div><a href="#observed">Open the run</a></aside>';
}
function contextBar(lens) {
  const nav = [['content','Content & answers'],['referrals','Traffic & citations'],['experiment','Shopper experiment']].map(([key,label]) =>
    '<a href="#evidence/' + selection + '/' + key + '"' + (lens === key ? ' aria-current="page"' : '') + '>' + label + '</a>').join('');
  return '<div class="contextbar">' + productSelect('evidence', lens) + '<nav class="subnav" aria-label="Case evidence">' + nav + '</nav></div>';
}
function passagesCard(version, letter) {
  const rows = version.passages.map(p => '<div class="excerpt"><span class="mono">' + esc(p.id) + '</span><p>' + esc(p.text) + '</p></div>').join('');
  return '<article class="paper version-card ' + letter.toLowerCase() + '"><div class="smallcap">Version ' + letter + '</div><h3>' +
    esc(version.label) + '</h3>' + rows + '</article>';
}
function recordFor(c, letter) {
  return c.records.find(r => r.question_id === questionId && r.version === letter && Number(r.repeat) === Number(answerRepeat));
}
function answerCard(c, letter) {
  const r = recordFor(c, letter);
  if (!r) return '<article class="paper"><p>No matching answer in this fixture.</p></article>';
  const verdict = r.verdict === 'abstain' ? 'Abstained' : r.verdict === 'correct' ? 'Correct' : 'Incorrect';
  let citation = '<p class="microcopy spaced">No citation supplied.</p>';
  if (r.citation_id) citation = '<div class="citation"><span class="mono">' + esc(r.citation_id) +
    '</span> · ' + (r.citation_valid ? 'Valid citation' : 'Invalid citation') + '<p>“' + esc(r.citation_quote) + '”</p></div>';
  return '<article class="paper version-card ' + letter.toLowerCase() + '"><div class="card-heading"><div class="smallcap">Answer · version ' +
    letter + '</div>' + tag(verdict) + '</div><p class="answer">' + esc(r.answer) + '</p>' + citation +
    '<p class="helper">Supported by the supplied text: <strong>' + (r.supported ? 'Yes' : 'No') + '</strong></p></article>';
}
function answerInspector(c) {
  if (!c.questions.some(q => q.id === questionId)) questionId = c.questions[0].id;
  const q = c.questions.find(item => item.id === questionId);
  const repeats = [...new Set(c.records.filter(r => r.question_id === questionId).map(r => Number(r.repeat)))].sort((a,b) => a-b);
  if (!repeats.includes(Number(answerRepeat))) answerRepeat = repeats[0];
  const options = c.questions.map(item => '<option value="' + esc(item.id) + '"' + (item.id === questionId ? ' selected' : '') + '>' + esc(item.text) + '</option>').join('');
  const repeatOptions = repeats.map(n => '<option value="' + n + '"' + (n === Number(answerRepeat) ? ' selected' : '') + '>Example ' + n + '</option>').join('');
  return '<div class="formrow"><label><span class="label">Buyer question</span><select id="question-select">' + options +
    '</select></label><label><span class="label">Paired answer</span><select id="repeat-select">' + repeatOptions +
    '</select></label></div><div class="double">' + answerCard(c,'A') + answerCard(c,'B') +
    '</div><div class="callout"><strong>Reference answer</strong><p>' + esc(q.truth) + ' <span class="mono">' + esc(q.fact_id) + '</span></p></div>';
}
function metricsTable(c) {
  const metrics = [['Total answers','total'],['Correct','correct'],['Incorrect','incorrect'],['Abstained','abstain'],['Cited a passage','cited'],['Supported by the text','supported']];
  const rows = metrics.map(([label,key]) => '<tr><td>' + label + '</td><td>' + c.metrics.A[key] + '</td><td>' + c.metrics.B[key] + '</td></tr>').join('');
  return '<div class="table-scroll"><table class="mini-table"><thead><tr><th>Fixture outcome</th><th>Version A</th><th>Version B</th></tr></thead><tbody>' + rows + '</tbody></table></div>';
}
function contentEvidence(c) {
  return '<section class="panel"><div class="card-heading"><h2>Content revision</h2>' + tag('Synthetic fixture') +
    '</div><p>' + esc(c.revision) + '</p><details class="details"><summary>Compare the product-page passages</summary><div class="double">' +
    passagesCard(c.versions.A,'A') + passagesCard(c.versions.B,'B') + '</div></details></section>' +
    sectionLead('Buyer question review','Paired answers are authored examples. Check each answer against the exact passage available to that version.') +
    '<section id="inspector">' + answerInspector(c) + '</section><section class="panel"><h2>Answer audit</h2><p>' +
    esc(c.interpretation) + '</p>' + metricsTable(c) +
    '<p class="helper">Denominator: all authored responses for that content version. These counts describe this fixture only.</p></section>' +
    '<div class="action-row"><a class="button" href="#evidence/' + selection + '/experiment">Inspect shopper experiment</a><a class="subbutton" href="#observed">View controlled AI run</a></div>';
}
function stat(label, value) {
  return '<div class="stat"><span>' + esc(label) + '</span><strong>' + esc(value) + '</strong></div>';
}
function rateCount(arm, field) { return pct(arm[field] / arm.n) + ' (' + fmt.format(arm[field]) + ')'; }
function experimentEvidence(r) {
  const counts = [['Assigned sessions','n'],['Engaged','engaged'],['Added to cart','carts'],['Purchased','purchases']].map(([label,key]) =>
    '<tr><td>' + label + '</td><td>' + (key === 'n' ? fmt.format(r.control.n) : rateCount(r.control,key)) +
    '</td><td>' + (key === 'n' ? fmt.format(r.treatment.n) : rateCount(r.treatment,key)) + '</td></tr>').join('');
  const strats = r.devices.map(row => '<tr><td>' + esc(row.device) + '</td><td>' + fmt.format(row.control.n) + ' / ' +
    fmt.format(row.treatment.n) + '</td><td>' + pp(row.effect_pp) + '</td><td>' + numberRange(row) + '</td></tr>').join('');
  return '<section class="panel"><div class="card-heading"><h2>Shopper experiment</h2>' + tag('Seeded simulation') +
    '</div><p>Each shopper session was assigned to A or B once. The primary outcome is a session with at least one add-to-cart.</p>' +
    '<div class="stat-grid">' + stat('Cart effect',pp(r.effect_pp)) + stat('Control cart rate',pct(r.control.carts / r.control.n)) +
    stat('Revised cart rate',pct(r.treatment.carts / r.treatment.n)) + '</div><p><strong>95% confidence interval:</strong> ' + numberRange(r) +
    '. <strong>Allocation check:</strong> p ' + (r.balance_p < 0.001 ? '&lt; 0.001' : '= ' + pval(r.balance_p)) + '.</p><div class="callout">' +
    badge(r) + '<p>' + esc(r.reason) + '</p></div><p class="helper">Pre-specified rule: hold if allocation p &lt; 0.01. Otherwise advance only if the lower confidence bound exceeds +0.50 pp.</p></section>' +
    '<section class="panel"><h2>Assignment and outcomes</h2><p class="section-desc">' + esc(r.retailer) + ' · ' + esc(r.locale) + ' · ' +
    esc(r.start_date) + ' to ' + esc(r.end_date) + '</p><div class="table-scroll"><table class="mini-table"><thead><tr><th>Shopper outcome</th><th>A · Current</th><th>B · Revised</th></tr></thead><tbody>' +
    counts + '</tbody></table></div><p class="helper">Rates use all sessions assigned to the respective version. Engagement and purchase are secondary outcomes.</p></section>' +
    '<section class="panel"><h2>Robustness checks</h2><p class="section-desc">Device estimates and leave-one-day-out checks are descriptive. They do not repair broken allocation.</p>' +
    '<div class="table-scroll"><table class="mini-table"><thead><tr><th>Device</th><th>Sessions A / B</th><th>Cart effect</th><th>95% interval</th></tr></thead><tbody>' + strats +
    '</tbody></table></div><p class="helper">Device-standardised effect ' + pp(r.sensitivity.standardised_effect_pp) + '. Dropping one day at a time gives ' +
    signed(r.sensitivity.leave_one_day_out_min_pp) + ' to ' + pp(r.sensitivity.leave_one_day_out_max_pp) + '.</p></section>' +
    '<div class="action-row"><a class="button" href="#brief/' + selection + '">' + icon('file') + 'Prepare decision brief</a></div>';
}
function evidence(lens) {
  const c = geo.cases[selection];
  return hero('Case evidence',nameOf(selection),c.business_question) + contextBar(lens) +
    (lens === 'experiment' ? experimentEvidence(experiments.cases[selection]) :
      lens === 'referrals' ? referralEvidence(referrals.cases[selection]) : contentEvidence(c));
}

const reviewOptions = ['Pending review', 'Agree with trial decision', 'Request another test', 'Escalate to data owner'];
const storageKey = id => 'shelf-evidence.v1.review.' + id;
function loadReview(id) {
  try {
    const item = JSON.parse(localStorage.getItem(storageKey(id)) || '{}');
    return {status: reviewOptions.includes(item?.status) ? item.status : reviewOptions[0], note: String(item?.note || ''), saved: item?.saved || ''};
  } catch { return {status: reviewOptions[0], note: '', saved: ''}; }
}
function brief() {
  const r = experiments.cases[selection], c = geo.cases[selection], saved = loadReview(selection);
  const options = reviewOptions.map(o => '<option' + (o === saved.status ? ' selected' : '') + '>' + esc(o) + '</option>').join('');
  const entries = [
    ['Retailer and market',r.retailer + ' · ' + r.locale],['Proposed change',c.revision],
    ['Supported answers',c.metrics.A.supported + ' / ' + c.metrics.A.total + ' in A, ' + c.metrics.B.supported + ' / ' + c.metrics.B.total + ' in B (authored examples)'],
    ['Cart effect',pp(r.effect_pp) + ' · 95% interval ' + numberRange(r)],['Allocation p-value',pval(r.balance_p)],
    ['Trial decision',r.decision],['Next step',r.reason]
  ];
  return hero('Knowledge transfer','Decision brief','Capture the analyst’s evidence and your review in a shareable Markdown brief.') +
    '<div class="contextbar">' + productSelect('brief') + '<a class="back" href="#evidence/' + selection + '/experiment">Reopen experiment</a></div>' +
    '<div class="brief-grid"><section class="paper"><div class="card-heading"><h2>' + esc(nameOf(selection)) + '</h2>' +
    tag('Synthetic case') + '</div><dl>' + entries.map(([k,v]) => '<div class="key-value"><dt>' + esc(k) + '</dt><dd>' + esc(v) + '</dd></div>').join('') +
    '</dl></section><section class="paper"><h2>Reviewer handoff</h2><p class="section-desc">Save a review on this device or download the current brief.</p>' +
    '<form id="review-form"><label class="form-field"><span class="label">Review outcome</span><select id="review-status">' + options + '</select></label>' +
    '<label class="form-field"><span class="label">Reviewer note</span><textarea id="review-note" rows="5" maxlength="4000" placeholder="What should the retailer or research lead do next?">' +
    esc(saved.note) + '</textarea></label><div class="action-row"><button class="button" type="submit">Save review</button>' +
    '<button class="subbutton" type="button" id="export-brief">' + icon('download') + 'Export .md</button></div><p id="save-status" class="helper" role="status">' +
    (saved.saved ? 'Saved on this device: ' + esc(new Date(saved.saved).toLocaleString('en-GB')) : 'Review notes stay in this browser until you export them.') +
    '</p></form></section></div>';
}
function currentReview() {
  return {status: document.getElementById('review-status').value, note: document.getElementById('review-note').value, saved: new Date().toISOString()};
}
function exportBrief() {
  const r = experiments.cases[selection], c = geo.cases[selection], form = currentReview();
  const content = [
    '# ' + nameOf(selection) + ' — retail content decision',
    'Shelf Evidence v1.0 · ' + r.retailer + ' · ' + r.locale,
    '## Business question', c.business_question, '## Proposed change', c.revision,
    '## Shopping-answer evidence', 'Authored, synthetic paired responses. A: ' + c.metrics.A.supported + '/' + c.metrics.A.total +
    ' supported answers. B: ' + c.metrics.B.supported + '/' + c.metrics.B.total + ' supported answers. ' + c.interpretation,
    '## Shopper experiment', 'Seeded synthetic sessions, ' + r.start_date + ' to ' + r.end_date + '.',
    '| Version | Assigned | Engaged | Added to cart | Purchased |\n|---|---:|---:|---:|---:|\n' +
    [r.control,r.treatment].map((arm,i) => '| ' + (i ? 'B' : 'A') + ' | ' + [arm.n,arm.engaged,arm.carts,arm.purchases].join(' | ') + ' |').join('\n'),
    'Absolute cart effect: ' + pp(r.effect_pp) + '. 95% interval: ' + numberRange(r) + '. Allocation p-value: ' + pval(r.balance_p) + '.',
    '## Decision', r.decision + '. ' + r.reason,
    '## Reviewer handoff', form.status, form.note || 'No additional note.', 'Exported ' + form.saved + '.',
    'The answer fixture and shopper experiment are separate measurements. These results do not establish any effect of AI exposure on purchases.',
    'Source and methods: https://github.com/rongsenzhang/shelf-evidence-lab'
  ].join('\n\n') + '\n';
  const url = URL.createObjectURL(new Blob([content],{type:'text/markdown;charset=utf-8'}));
  const link = document.createElement('a');
  link.href = url; link.download = 'shelf-evidence-' + selection + '-brief.md';
  document.body.append(link); link.click(); link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1500);
  say('Decision brief exported.');
}

function render(options = {}) {
  const path = location.hash.slice(1).split('/');
  const section = ['evidence','brief','observed'].includes(path[0]) ? path[0] : 'overview';
  if (caseIds.includes(path[1])) selection = path[1];
  const lens = ['experiment','referrals'].includes(path[2]) ? path[2] : 'content';
  const top = section === 'observed' ? 'evidence' : section;
  for (const id of ['overview','evidence','brief']) {
    const link = document.getElementById('nav-' + id);
    if (id === top) link.setAttribute('aria-current','page'); else link.removeAttribute('aria-current');
    if (id !== 'overview') link.href = '#' + id + '/' + selection;
  }
  if (section === 'evidence') main.innerHTML = evidence(lens);
  else if (section === 'brief') main.innerHTML = brief();
  else if (section === 'observed') main.innerHTML = observedView();
  else main.innerHTML = overview();
  const viewTitle = {overview:'Content decision desk',evidence:nameOf(selection) + ' · ' + lensLabels[lens],brief:'Decision brief',observed:'Controlled AI run'}[section];
  document.title = viewTitle + ' · Shelf Evidence';
  if (currentPath && currentPath !== location.hash && options.focus !== false) {
    main.focus({preventScroll:true});
    window.scrollTo(0,0);
  }
  currentPath = location.hash || '#overview';
}
main.addEventListener('click', event => {
  const filter = event.target.closest('[data-filter]');
  if (filter) {
    worklistFilter = filter.dataset.filter;
    document.querySelectorAll('[data-filter]').forEach(el => el.setAttribute('aria-pressed',String(el === filter)));
    document.getElementById('case-rows').innerHTML = caseRows();
    say(document.getElementById('case-rows').children.length + ' cases shown.');
  }
  if (event.target.closest('#export-brief')) exportBrief();
});
main.addEventListener('change', event => {
  const field = event.target;
  if (field.id === 'case-select') {
    questionId = ''; answerRepeat = 1;
    location.hash = field.dataset.section + '/' + field.value + (field.dataset.lens ? '/' + field.dataset.lens : '');
  }
  if (field.id === 'question-select' || field.id === 'repeat-select') {
    if (field.id === 'question-select') { questionId = field.value; answerRepeat = 1; }
    else answerRepeat = Number(field.value);
    document.getElementById('inspector').innerHTML = answerInspector(geo.cases[selection]);
    document.getElementById(field.id).focus();
    say('Updated the paired answers.');
  }
  if (field.id === 'observed-select') {
    observedPair = field.value;
    main.innerHTML = observedView();
    document.getElementById('observed-select')?.focus();
    say('Updated the controlled run evidence.');
  }
});
main.addEventListener('submit', event => {
  if (event.target.id !== 'review-form') return;
  event.preventDefault();
  const status = document.getElementById('save-status');
  try {
    localStorage.setItem(storageKey(selection),JSON.stringify(currentReview()));
    status.textContent = 'Review saved on this device.';
  } catch { status.textContent = 'Browser storage is unavailable. Export the brief to keep this review.'; }
});
async function readData(name) {
  const response = await fetch('data/' + name + '.json');
  if (!response.ok) throw new Error(name + ' (' + response.status + ')');
  return response.json();
}
async function initialise() {
  try {
    const data = window.SHELF_DATA || Object.fromEntries(await Promise.all(['experiment','geo','observed','referrals'].map(async name => [name,await readData(name)])));
    experiments = data.experiment; geo = data.geo; observed = data.observed; referrals = data.referrals;
    render();
    window.addEventListener('hashchange',render);
  } catch (error) {
    main.innerHTML = '<section class="paper error" role="alert"><h1>Evidence could not be opened</h1><p class="spaced">Reload the published page or serve a local checkout with <code>python3 -m http.server</code>. The workspace reads its evidence from the accompanying data files.</p><p class="helper">' + esc(error.message) + '</p></section>';
  }
}

function observedView() {
  const items = observed.items;
  const item = items.find(row => row.id === observedPair) || items[0];
  observedPair = item.id;
  const options = items.map(row => '<option value="' + esc(row.id) + '"' + (row.id === observedPair ? ' selected' : '') + '>' + esc(row.question) + '</option>').join('');
  function observedAnswer(key) {
    const result = item[key];
    return '<article class="paper version-card ' + key.toLowerCase() + '"><div class="card-heading"><div class="smallcap">Capture ' + key +
      '</div>' + tag(result.grade) + '</div><p class="answer captured">' + esc(result.answer) + '</p></article>';
  }
  const passage = key => '<article class="paper version-card ' + key.toLowerCase() + '"><div class="smallcap">Source packet ' + key +
    '</div><p class="spaced captured">' + esc(observed.variants[key]) + '</p></article>';
  const textList = value => Array.isArray(value) ? '<ul class="bullet-list">' + value.map(v => '<li>' + esc(v) + '</li>').join('') + '</ul>' : '<p>' + esc(value) + '</p>';
  return hero('Controlled AI run',observed.title,observed.product) +
    '<div class="contextbar"><a class="back" href="#overview">Back to overview</a><span class="tag">Recorded ' + esc(observed.date) + '</span></div>' +
    '<section class="panel"><div class="card-heading"><h2>How the run was captured</h2>' + tag('Observed responses') + '</div>' +
    textList(observed.protocol) + '<p class="helper">Product reference: <a class="source-link" href="' + esc(observed.source_url) + '" target="_blank" rel="noopener noreferrer">' +
    esc(observed.source_label) + '</a></p><details class="details"><summary>Read the two source packets</summary><div class="double">' + passage('A') + passage('B') +
    '</div></details><details class="details"><summary>Read the exact reader instruction</summary><p class="captured">' +
    esc(observed.instruction) + '</p></details></section>' + sectionLead('Captured answer comparison','Select a question to compare the recorded model answers under each source condition.') +
    '<div class="formrow"><label><span class="label">Buyer question</span><select id="observed-select">' + options +
    '</select></label></div><div class="double">' + observedAnswer('A') + observedAnswer('B') + '</div><div class="callout"><strong>Evaluation reference</strong><p>' +
    esc(item.expected) + '</p></div><section class="panel"><h2>Interpretation limits</h2>' + textList(observed.limitations) + '</section>';
}

function referralEvidence(r) {
  const channelRows = r.channels.map(row => '<tr><td>' + esc(row.channel) + '</td><td>' + fmt.format(row.n) + '</td><td>' +
    fmt.format(row.carts) + '</td><td>' + Number(row.cart_rate_pct).toFixed(1) + '%</td><td>' + fmt.format(row.purchases) + '</td></tr>').join('');
  const weekRows = r.weekly.map(row => '<tr><td>' + esc(row.week) + '</td><td>' + row.cited + ' / ' + row.probes +
    '</td><td><span class="rate-bar"><i style="width:' + Math.max(0, Math.min(100, row.citation_rate_pct)) + '%"></i></span>' +
    Number(row.citation_rate_pct).toFixed(1) + '%</td></tr>').join('');
  const sourceRows = r.sources.map(row => '<tr><td>' + esc(row.publisher) + '</td><td>' + esc(row.format) + '</td><td>' + row.cited +
    ' / ' + row.probes + '</td><td>' + Number(row.citation_rate_pct).toFixed(1) + '%</td></tr>').join('');
  return '<section class="panel"><div class="card-heading"><h2>Referral attribution</h2>' + tag('Synthetic observations') +
    '</div><p>Compare sessions with explicit AI referral tags against organic search. A missing tag makes the origin uncertain.</p><div class="stat-grid">' +
    stat('Tagged AI sessions',fmt.format(r.tagged_ai_sessions)) + stat('Share of all sessions',Number(r.tagged_ai_share_pct).toFixed(1) + '%') +
    stat('Unknown origin',Number(r.unknown_share_pct).toFixed(1) + '%') + '</div><div class="table-scroll"><table class="mini-table"><thead><tr>' +
    '<th>Observed source</th><th>Sessions</th><th>Cart adds</th><th>Cart rate</th><th>Purchases</th></tr></thead><tbody>' + channelRows +
    '</tbody></table></div><p class="helper">Tagged AI minus organic cart rate: ' + pp(r.observed_gap_pp) +
    '. Different shoppers select into these channels, so this gap cannot identify an AI referral effect.</p></section>' +
    '<section class="panel"><div class="card-heading"><h2>Citation trend</h2>' + tag('Synthetic probe panel') +
    '</div><p>Each row counts the probes that cited a source during that week. This panel is independent of the shopper sessions.</p>' +
    '<div class="table-scroll"><table class="mini-table"><thead><tr><th>Week</th><th>Cited / probes</th><th>Citation rate</th></tr></thead><tbody>' +
    weekRows + '</tbody></table></div></section><section class="panel"><h2>Publisher and format</h2><p>Compare citation frequency by publisher and content format.</p>' +
    '<div class="table-scroll"><table class="mini-table"><thead><tr><th>Publisher</th><th>Format</th><th>Cited / probes</th><th>Citation rate</th></tr></thead><tbody>' +
    sourceRows + '</tbody></table></div><p class="helper">Unadjusted correlation between fact-table format and citation: r = ' +
    Number(r.format_correlation_r).toFixed(2) + '. Publisher mix, wording and question selection can influence this association.</p></section>' +
    '<div class="action-row"><a class="button" href="#evidence/' + selection + '/experiment">Inspect shopper experiment</a></div>';
}

document.getElementById('skip-link').addEventListener('click', event => {
  event.preventDefault();
  main.focus();
});

initialise();
