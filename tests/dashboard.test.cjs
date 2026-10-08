// Unit tests execute the real inline application script against a small DOM stub.
// These are not a browser, visual QA, or an indirect browser-access workaround.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('web/dashboard.html','utf8');
const script = html.match(/<script>([\s\S]*?)<\/script>/)[1];
function run(search){
  const elements = new Map();
  const element=id=>{if(!elements.has(id))elements.set(id,{textContent:'',hidden:true,style:{},classList:{add(v){this.value=v}},listeners:{},addEventListener(k,v){this.listeners[k]=v},setAttribute(k,v){this[k]=v}});return elements.get(id)};
  const bars=Array.from({length:6},()=>({style:{}}));
  const links=['?view=overview','?view=analytics','?view=program&program=first-aid'].map(href=>({href,dataset:{},getAttribute(){return this.href},addEventListener(){}}));
  const cta={href:'?view=analytics',dataset:{event:'analytics_cta_clicked',placement:'overview'},getAttribute(){return this.href},addEventListener(k,v){this[k]=v}};
  links.push(cta);const requests=[];const navigation=[];
  const context={URLSearchParams,location:{search,assign:v=>navigation.push(v)},document:{getElementById:element,querySelector:s=>s==='.chart'?element('chart'):s==='.analytics-cta'?cta:null,querySelectorAll:s=>s==='.bar'?bars:s==='[data-event]'?[cta]:s==='a[href^="?"]'?links:[]},fetch:async(url,args)=>{requests.push({url,body:JSON.parse(args.body)});return {ok:true}}};
  vm.runInNewContext(script,context);return {element,requests,navigation,cta,links,bars};
}
(async()=>{
  let app=run('?view=overview&qa=1');
  assert.equal(app.element('nav-certifications').className,'active');
  assert.equal(app.element('nav-analytics').className,'');
  assert.equal(app.requests[0].body.event,'analytics_cta_exposed');
  assert.equal(app.requests[0].body.test,true);
  assert.ok(app.links.every(l=>l.href.includes('qa=1')));
  await app.cta.click({preventDefault(){}});
  assert.equal(app.requests[1].body.event,'analytics_cta_clicked');
  assert.equal(app.requests[1].body.test,true);
  assert.equal(app.navigation[0],'?view=analytics&qa=1');
  app=run('?view=analytics&qa=1');
  assert.equal(app.element('nav-analytics').className,'active');
  assert.equal(app.element('nav-analytics')['aria-current'],'page');
  assert.equal(app.element('nav-certifications').className,'');
  assert.equal(app.requests[0].body.event,'dashboard_viewed');
  assert.equal(app.requests[0].body.program,null);
  app.element('report-action').listeners.click();
  assert.equal(app.element('activity-result').hidden,false);
  assert.equal(app.requests[1].body.event,'dashboard_action');
  assert.equal(app.requests[1].body.test,true);
  app=run('?view=analytics&program=first-aid&qa=1');
  assert.equal(app.element('issued-metric').textContent,'56');
  assert.equal(app.element('renewed-metric').textContent,'12');
  assert.equal(app.element('learners-metric').textContent,'312');
  assert.ok(app.element('activity-result').textContent.startsWith('18 learners'));
  assert.equal(app.requests[0].body.placement,'within_item');
  assert.equal(app.requests[0].body.program,'first-aid');
  assert.equal(app.bars[0].style.height,'35%');
  app=run('?view=program&program=first-aid');
  assert.equal(app.element('nav-certifications').className,'active');
  assert.equal(app.element('nav-analytics').className,'');
  app=run('?view=analytics&program=unknown');
  assert.equal(app.requests[0].body.program,null);
  console.log('PASS: exposure, click, navigation, QA propagation, useful action, filtered metrics and unknown scope (real inline JS unit tests; no browser QA).');
})().catch(e=>{console.error(e);process.exitCode=1});
