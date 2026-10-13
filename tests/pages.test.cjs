// Published Pages files redirect to the portfolio root and keep query and hash.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const redirects={
  'index.html':['/','https://calvin-chow-pm.github.io/'],
  'workflow.html':['/workflow/','https://calvin-chow-pm.github.io/workflow/'],
  'system.html':['/system/','https://calvin-chow-pm.github.io/system/'],
  'prototype.html':['/prototype/','https://calvin-chow-pm.github.io/prototype/'],
  'app.html':['/app/','https://calvin-chow-pm.github.io/app/'],
  'baseline.html':['/baseline/','https://calvin-chow-pm.github.io/baseline/'],
  'walkthrough.html':['/walkthrough/','https://calvin-chow-pm.github.io/walkthrough/'],
};
for(const [file,[path,canonical]] of Object.entries(redirects)){
  const html=fs.readFileSync('site/'+file,'utf8');
  assert.ok(html.includes(`rel="canonical" href="${canonical}"`), file);
  assert.ok(html.includes(`http-equiv="refresh" content="0; url=${canonical}"`), file);
  assert.ok(html.includes(`location.replace("${path}" + location.search + location.hash)`), file);
  const location={search:'?view=overview',hash:'#5'};
  let replaced='';
  location.replace=url=>{replaced=url;};
  const context={location};
  vm.createContext(context);
  vm.runInContext(html.match(/<script>([\s\S]*?)<\/script>/)[1],context);
  assert.equal(replaced, path+'?view=overview#5', file);
}
console.log('PASS: published pages redirect to the portfolio root and keep query and hash.');

// The cover source still leads with strategy and outcomes.
const cover=fs.readFileSync('web/cover.html','utf8');
assert.ok(!cover.includes('<iframe'));
assert.ok(cover.includes('id="prototype" href="https://calvin-chow-pm.github.io/agentic-product-workflow/prototype.html?view=overview"'));
assert.ok(cover.includes('Try the certification prototype'));
assert.ok(cover.includes('The system behind my agents'));
assert.ok(cover.includes('<strong>10% → 35% analytics engagement</strong>'));
assert.ok(!cover.includes('dashboard engagement'));
assert.ok(cover.includes('<span>Setup stayed simple</span><br>as features were added'));
assert.ok(cover.includes('+10% new active programs after release'));
assert.ok(cover.includes('shipped by my agent team and approved by my EM'));
assert.ok(cover.includes('powered by my AI second brain'));
assert.ok(cover.includes('The product story behind certification'));
assert.ok(cover.includes('Usage lagged behind comparable product dashboards, despite similar adoption.'));
assert.ok(cover.includes('<strong>New active programs +10%</strong> month over month after launch, still rising</p>'));
assert.ok(cover.includes('<span aria-hidden="true">↑</span> Read from activation up'));
assert.ok(cover.includes('How my agent team’s evidence was scored, corrected and used in decisions.'));
assert.ok(cover.indexOf('Shipped improvement')<cover.indexOf('AI Second Brain'));
assert.ok(cover.indexOf('AI Second Brain')<cover.indexOf('Monitoring &amp; evaluation'));
assert.ok(!cover.includes('click-through'));
assert.ok(cover.includes('+4 pts NRR'));
assert.ok(cover.includes('From activation to retention'));
assert.ok(cover.includes('<strong>Recertification enablement</strong> <strong>80%</strong> in beta <span class="signal">Expansion signal</span>'));
assert.equal((cover.match(/North star/g) || []).length, 1);
assert.ok(cover.includes('<strong>Certificates issued +9%</strong> month over month after certification launched</p>'));
assert.ok(cover.includes('Business outcome</div><p><strong>NRR</strong> <strong>+4 pts</strong>'));
assert.ok(cover.includes('<strong>Program-creation conversion</strong> <strong>63.8% → 68.9%</strong>'));
assert.ok(cover.includes('More launched programs give learners more to complete'));
assert.ok(cover.includes('Each completion issues a certificate, where admin and learner value meet'));
assert.ok(cover.includes('Issued certificates show customers value, so they renew and expand'));
assert.ok(!cover.includes('Signals from different measurement windows'));
assert.ok(cover.indexOf('class="ladder-cue"')<cover.indexOf('class="ladder-layout"'));
assert.ok(cover.indexOf('</h2></div><p class="ladder-cue"')>0);
assert.ok(cover.includes('~230 → ~190 seconds'));
assert.equal((cover.match(/63\.8% → 68\.9%/g) || []).length, 1);
assert.ok(cover.indexOf('id="outcomes"')<cover.indexOf('id="strategy"'));
assert.ok(cover.indexOf('id="outcomes"')<cover.indexOf('<div class="actions bottom">'));
assert.ok(!cover.includes('Saved execution evidence'));
assert.ok(!cover.includes('Why analytics belonged on the overview'));
console.log('PASS: concise cover order, direct prototype link, Second Brain context and historical placement rationale.');
