// Execute the public renderer against the four committed snapshots without a browser dependency.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const root = path.resolve(__dirname, '..');
const snapshots = {};
for (const name of ['experiment', 'geo', 'observed', 'referrals']) {
  snapshots[name] = JSON.parse(fs.readFileSync(path.join(root, 'data', name + '.json'), 'utf8'));
}

const fields = new Map();
const savedNotes = new Map();
const downloads = [];
let exportedBlob;

class Element {
  constructor() {
    this.innerHTML = '';
    this.attributes = {};
    this.handlers = {};
  }
  addEventListener(name, handler) { this.handlers[name] = handler; }
  setAttribute(name, value) { this.attributes[name] = value; }
  removeAttribute(name) { delete this.attributes[name]; }
  focus() {}
  append() {}
  remove() {}
  click() { downloads.push(this.download); }
}

const document = {
  body: new Element(),
  createElement() { return new Element(); },
  getElementById(id) {
    if (!fields.has(id)) fields.set(id, new Element());
    return fields.get(id);
  }
};
const location = { hash: '#overview' };
const context = vm.createContext({
  document, location, Intl, Blob,
  window: { SHELF_DATA: snapshots, addEventListener() {}, scrollTo() {} },
  localStorage: {
    getItem: key => savedNotes.get(key),
    setItem: (key, value) => savedNotes.set(key, value)
  },
  URL: {
    createObjectURL(blob) { exportedBlob = blob; return 'blob:test'; },
    revokeObjectURL() {}
  },
  setTimeout() {}
});
const evaluate = code => vm.runInContext(code, context);
const main = document.getElementById('main');

function verifyRoute(hash, landmark) {
  location.hash = hash;
  evaluate('render()');
  assert.match(main.innerHTML, landmark);
  assert.doesNotMatch(main.innerHTML, /undefined|NaN|\[object Object\]/);
}

async function verifyWorkbench() {
  evaluate(fs.readFileSync(path.join(root, 'app.js'), 'utf8'));
  assert.match(main.innerHTML, /Content decision desk/);
  assert.match(main.innerHTML, /Review first case/);
  assert.match(main.innerHTML, /Tide Mini speaker/);
  assert.match(main.innerHTML, /0\.87 to \+2\.85 pp/);

  for (const id of ['headphones', 'monitor', 'speaker']) {
    verifyRoute('#evidence/' + id, /Buyer question review/);
    for (const question of snapshots.geo.cases[id].questions) {
      for (const repeat of [1, 2]) {
        context.pick = question.id;
        context.repeat = repeat;
        const html = evaluate('questionId = pick; answerRepeat = repeat; answerInspector(geo.cases[selection])');
        assert.doesNotMatch(html, /No matching answer/);
        assert.match(html, /Answer · version A/);
        assert.match(html, /Answer · version B/);
      }
    }
    verifyRoute('#evidence/' + id + '/experiment', /Robustness checks/);
    verifyRoute('#evidence/' + id + '/referrals', /Citation trend/);
    verifyRoute('#brief/' + id, /Reviewer handoff/);
    document.getElementById('review-status').value = 'Agree with trial decision';
    document.getElementById('review-note').value = 'Review <' + id + '>.';
    main.handlers.submit({ target: { id: 'review-form' }, preventDefault() {} });
    evaluate('render()');
    assert.ok(main.innerHTML.includes('Review &lt;' + id + '&gt;.'));
    evaluate('exportBrief()');
    assert.equal(downloads.at(-1), 'shelf-evidence-' + id + '-brief.md');
    const markdown = await exportedBlob.text();
    assert.ok(markdown.includes(snapshots.experiment.cases[id].decision));
    assert.ok(markdown.includes('Review <' + id + '>.'));
  }
  verifyRoute('#observed', /Captured answer comparison/);
  for (const question of snapshots.observed.items) {
    context.pick = question.id;
    const html = evaluate('observedPair = pick; observedView()');
    assert.ok(html.includes(question.B.grade));
    assert.match(html, /Evaluation reference/);
  }
  console.log('Passed: overview, 13 routes, 24 fixture pairs, 4 observed questions, 3 saved reviews and Markdown exports.');
}

verifyWorkbench().catch(error => { console.error(error); process.exitCode = 1; });
