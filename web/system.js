'use strict';
const stepButtons = [...document.querySelectorAll('[data-step]')];
const panels = [...document.querySelectorAll('.panel')];
const titles = ['Gather & route', 'Evaluate', 'Review & improve', 'Connect to action'];
let current = 0;
function selectStep(index, focusButton = false) {
  current = Math.max(0, Math.min(index, panels.length - 1));
  panels.forEach((panel, i) => { panel.hidden = i !== current; });
  stepButtons.forEach((button, i) => { button.setAttribute('aria-pressed', String(i === current)); });
  document.getElementById('progress').textContent = `Step ${current + 1} of 4 · ${titles[current]}`;
  document.getElementById('previous').disabled = current === 0;
  document.getElementById('next').disabled = current === panels.length - 1;
  document.getElementById('next').textContent = current < panels.length - 1 ? `Next: ${titles[current + 1]} →` : 'Walkthrough complete';
  if (focusButton) stepButtons[current].focus();
}
stepButtons.forEach((button, i) => {
  button.addEventListener('click', () => selectStep(i));
  button.addEventListener('keydown', event => {
    const targets = {ArrowRight: (i + 1) % panels.length, ArrowLeft: (i + panels.length - 1) % panels.length, Home: 0, End: panels.length - 1};
    if (event.key in targets) { event.preventDefault(); selectStep(targets[event.key], true); }
  });
});
document.getElementById('previous').addEventListener('click', () => selectStep(current - 1, true));
document.getElementById('next').addEventListener('click', () => selectStep(current + 1, true));
selectStep(0);
