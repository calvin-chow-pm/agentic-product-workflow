// Render the exported page in a DOM stub; no browser or live inference.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('site/workflow.html','utf8');
assert.ok(!source.includes('href="walkthrough.html"'));
assert.ok(!source.includes('Inspect execution details'));
assert.ok(!source.includes('The product story'));
assert.ok(source.includes('Repository &amp; supporting records'));
assert.equal((source.match(/class="disclosure"/g)||[]).length,1);
const nodes={};let removed=[];
const context={document:{querySelector:s=>nodes[s]??={style:{},setAttribute(k,v){this[k]=v}},querySelectorAll:()=>['Try the local release checks','Try the learning & context refresh','Design alternatives'].map(text=>({querySelector:()=>({textContent:text}),remove(){removed.push(text)}}))},location:{hash:''},history:{replaceState(){}},setTimeout(){}};
vm.createContext(context);vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],context);
assert.ok(nodes['#content'].innerHTML.includes('Adoption was healthy'));
for(let selected=0;selected<7;selected++){vm.runInContext(`show(${selected})`,context);assert.ok(nodes['#content'].innerHTML.includes('section'));}
assert.ok(removed.includes('Try the local release checks'));
assert.ok(removed.includes('Try the learning & context refresh'));
assert.ok(!removed.includes('Design alternatives'));
assert.ok(nodes['#content'].innerHTML.includes('Defined successful exports'));
vm.runInContext("selected=4;render();selectPreview('baseline')",context);
assert.equal(nodes['#preview'].src,'baseline.html?qa=1');assert.equal(nodes['#full-workspace'].href,'baseline.html?qa=1');
vm.runInContext("selectPreview('candidate')",context);assert.equal(nodes['#preview'].src,'app.html?qa=1');
vm.runInContext("action('release')",context);assert.ok(nodes['#message'].textContent.includes('Saved run'));
vm.runInContext('show(5)',context);assert.ok(nodes['#content'].innerHTML.includes('10% → 35%'));assert.ok(nodes['#content'].innerHTML.includes('all certification users with dashboard access'));assert.ok(nodes['#content'].innerHTML.includes('Month over month'));assert.ok(nodes['#content'].innerHTML.includes('Reconstruction release status'));
for(const file of ['app.html','baseline.html','walkthrough.html']){
 const html=fs.readFileSync('site/'+file,'utf8');
 for(const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
}
assert.ok(fs.readFileSync('site/app.html','utf8').includes('View certification analytics'));
assert.ok(!fs.readFileSync('site/baseline.html','utf8').includes('data-event="analytics_cta_clicked"'));
console.log('PASS: seven static tabs, relative preview paths, hidden local controls, captured reasoning, safe action fallback and script syntax.');

// The cover leads with strategy and outcomes; the full prototype stays one click away.
const cover=fs.readFileSync('site/index.html','utf8');
assert.ok(!cover.includes('<iframe'));
assert.ok(cover.includes('id="prototype" href="https://calvin-chow-pm.github.io/agentic-product-workflow/prototype.html?view=overview"'));
assert.ok(cover.includes('Try the certification prototype'));
assert.ok(cover.includes('The Second Brain behind this system'));
assert.ok(cover.indexOf('id="strategy"')<cover.indexOf('id="outcomes"'));
assert.ok(cover.indexOf('id="outcomes"')<cover.indexOf('<div class="actions bottom">'));
assert.ok(!cover.includes('Saved execution evidence'));
assert.ok(!cover.includes('Why analytics belonged on the overview'));
vm.runInContext('show(3)',context);assert.ok(nodes['#content'].innerHTML.includes('Program-specific analytics was planned for a later slice'));assert.ok(nodes['#content'].innerHTML.indexOf('I chose the certification overview')<nodes['#content'].innerHTML.indexOf('Validation lesson'));
assert.ok(!nodes['#content'].innerHTML.includes('does not establish Calvin’s historical final placement'));
console.log('PASS: concise cover order, direct prototype link, Second Brain context and historical placement rationale.');

vm.runInContext('show(0)',context);assert.ok(nodes['#content'].innerHTML.includes('<table>'));assert.ok(!nodes['#content'].innerHTML.includes('class="metrics"'));assert.ok(nodes['#content'].innerHTML.includes('28-day window'));
vm.runInContext('show(4)',context);assert.ok(nodes['#content'].innerHTML.indexOf('<iframe')<nodes['#content'].innerHTML.indexOf('View checks'));assert.ok(nodes['#content'].innerHTML.includes('Demo checks: PASS'));
vm.runInContext("state.events=state.events.filter(e=>e.phase!=='response');state.pending_requests=['missing'];show(2)",context);assert.ok(nodes['#content'].innerHTML.includes('Response pending'));assert.ok(nodes['#content'].innerHTML.includes('still pending'));
console.log('PASS: streamlined insight, historical decision priority, prototype-first QA, and visible pending evidence.');
