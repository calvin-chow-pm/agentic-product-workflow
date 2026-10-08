// Render the exported page in a DOM stub; no browser or live inference.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('site/index.html','utf8');
const nodes={};let removed=[];
const context={document:{querySelector:s=>nodes[s]??={style:{},setAttribute(k,v){this[k]=v}},querySelectorAll:()=>['Try the local release checks','Try the learning & context refresh','Full design reasoning & alternatives'].map(text=>({querySelector:()=>({textContent:text}),remove(){removed.push(text)}}))},location:{hash:''},history:{replaceState(){}},setTimeout(){}};
vm.createContext(context);vm.runInContext(source.match(/<script>([\s\S]*?)<\/script>/)[1],context);
assert.ok(nodes['#content'].innerHTML.includes('Adoption was healthy'));
for(let selected=0;selected<7;selected++){vm.runInContext(`show(${selected})`,context);assert.ok(nodes['#content'].innerHTML.includes('section'));}
assert.ok(removed.includes('Try the local release checks'));
assert.ok(removed.includes('Try the learning & context refresh'));
assert.ok(!removed.includes('Full design reasoning & alternatives'));
assert.ok(nodes['#content'].innerHTML.includes('Defined successful exports'));
vm.runInContext("selected=4;render();selectPreview('baseline')",context);
assert.equal(nodes['#preview'].src,'baseline.html?qa=1');assert.equal(nodes['#full-workspace'].href,'baseline.html?qa=1');
vm.runInContext("selectPreview('candidate')",context);assert.equal(nodes['#preview'].src,'app.html?qa=1');
vm.runInContext("action('release')",context);assert.ok(nodes['#message'].textContent.includes('Saved run'));
for(const file of ['app.html','baseline.html','walkthrough.html']){
 const html=fs.readFileSync('site/'+file,'utf8');
 for(const match of html.matchAll(/<script>([\s\S]*?)<\/script>/g))new vm.Script(match[1]);
}
assert.ok(fs.readFileSync('site/app.html','utf8').includes('View certification analytics'));
assert.ok(!fs.readFileSync('site/baseline.html','utf8').includes('data-event="analytics_cta_clicked"'));
console.log('PASS: seven static tabs, relative preview paths, hidden local controls, captured reasoning, safe action fallback and script syntax.');
