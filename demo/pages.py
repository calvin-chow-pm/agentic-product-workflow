"""Export a static, inspectable snapshot for GitHub Pages; never grant approvals."""
import argparse
import json
import re
from pathlib import Path
from .core import ROOT, Demo, digest, now, write
from .record import chapters


def static_app(source):
    source = source.replace('padding:36px 42px;margin:auto', 'padding:36px 42px;margin:0 auto')
    source = source.replace('href="/"', 'href="index.html"')
    source = source.replace('Demo workspace · All numbers are sample data', 'Interactive preview · All numbers are sample data')
    start = source.index('async function track(')
    end = source.index("document.querySelectorAll('[data-event]')", start)
    source = source[:start] + """async function track(event,placement){const labels={analytics_cta_exposed:'Analytics link displayed.',analytics_cta_clicked:'Analytics link opened.',dashboard_viewed:'Analytics dashboard opened.',dashboard_action:'Renewal activity shown.'};document.getElementById('event-note').textContent='Demo interaction: '+(labels[event]||'Preview updated.');}
""" + source[end:]
    return source


def export(demo, output):
    output = Path(output)
    state = demo.public()
    candidate_path = demo.base / 'application/index.html'
    if not candidate_path.exists():
        raise ValueError('Build an actual local candidate before exporting a snapshot.')
    candidate = static_app(candidate_path.read_text())
    baseline = static_app(demo.render(None, 'Captured baseline'))
    captured_at = now()
    payload = json.dumps(state, ensure_ascii=False).replace('<', '\\u003c')
    workflow = (ROOT / 'web/workflow.html').read_text()
    workflow = workflow.replace("const token='{{TOKEN}}';", 'const capturedState=' + payload + ';')
    start = workflow.index('async function action(')
    end = workflow.index('function selectPreview(', start)
    workflow = workflow[:start] + "async function action(){notify('Saved run: approvals and workflow commands run in the local version.');}\n" + workflow[end:]
    start = workflow.index('async function load(')
    end = workflow.index('const initial=', start)
    workflow = workflow[:start] + 'async function load(){state=JSON.parse(JSON.stringify(capturedState));render()}\n' + workflow[end:]
    workflow = workflow.replace("$('#content').innerHTML=html;", """$('#content').innerHTML=html;
    document.querySelectorAll('#content details.explore-details').forEach(section=>{
      if(['Try the local release checks','Try the learning & context refresh'].includes(section.querySelector('summary').textContent))section.remove();
    });""")
    workflow = workflow.replace('ACTUAL LOCAL RUN · SYNTHETIC EVIDENCE', 'SAVED ACTUAL RUN · INTERACTIVE PREVIEW')
    workflow = workflow.replace('Current demo status', 'Captured run status').replace('Refresh records', 'Reload snapshot')
    workflow = workflow.replace('Activity from this Codex reconstruction.', 'Saved activity from this Codex reconstruction.')
    workflow = workflow.replace('href="/"', 'href="index.html"')
    workflow = workflow.replace("'/baseline'", "'baseline.html'").replace("'/app'", "'app.html'")
    workflow = workflow.replace("'/baseline?qa=1'", "'baseline.html?qa=1'")
    notice = (' <span><strong>Hosted snapshot:</strong> captured on ' + captured_at[:10] + '. Agents do not run live here. '
              '<a href="manifest.json">Snapshot provenance</a> · <a href="run.json">Execution record</a></span>')
    workflow = workflow.replace('</div><div class="layout">', notice + '</div><div class="layout">', 1)
    values = chapters(demo)
    # Include the completed follow-up reasoning, not just prompt assembly.
    values[-1]['evidence']['applied_reasoning'] = [e['evidence'] for e in state['events'] if e['phase'] == 'reuse-result']
    values[-1]['events'] += [e for e in state['events'] if e['phase'] == 'reuse-result']
    recording = json.dumps({'chapters': values, 'run': state, 'candidate': candidate, 'baseline': baseline}, ensure_ascii=False).replace('<', '\\u003c')
    playback = (ROOT / 'web/playback.html').read_text().replace('{{PAYLOAD}}', recording)
    playback = playback.replace("const set=v=>$('#artifact').srcdoc=v;", "const set=v=>$('#artifact').src=v===recording.baseline?'baseline.html?qa=1':'app.html?qa=1';")
    output.mkdir(parents=True, exist_ok=True)
    cover = (ROOT / 'web/cover.html').read_text()
    cover = cover.replace('href="/workflow', 'href="workflow.html')
    cover = cover.replace('href="/app', 'href="app.html').replace('src="/app', 'src="app.html')
    prototype = candidate.replace('<title>Academy · Certification workspace</title>', '<title>Certification Programs Prototype · Calvin Chow</title>')
    prototype = re.sub(r'<div class="notice">.*?</div>', '<div class="notice">Certification prototype · Reconstructed with sample data</div>', prototype, count=1)
    for name, value in [('index.html', cover), ('workflow.html', workflow), ('app.html', candidate), ('prototype.html', prototype), ('baseline.html', baseline), ('walkthrough.html', playback)]:
        (output / name).write_text(value)
    (output / '.nojekyll').write_text('')
    write(output / 'run.json', state)
    historical = json.loads((ROOT / 'docs/historical-outcomes.json').read_text())
    write(output / 'historical-outcomes.json', historical)
    manifest = {'captured_at': captured_at, 'format': 'Static snapshot of actual local execution with interactive browser prototype', 'agent_inference': 'Recorded only; no live inference or background workers on the hosted site', 'prototype_changes': 'Browser-tab sample edits only; preview events are not sent to a server', 'local_candidate_sha256': digest(candidate_path), 'source_cover_sha256': digest(ROOT / 'web/cover.html'), 'historical_outcomes': 'User-confirmed historical account, separate from synthetic execution records', 'source_workflow_sha256': digest(ROOT / 'web/workflow.html'), 'snapshot_files': {name: digest(output / name) for name in ['index.html', 'workflow.html', 'app.html', 'prototype.html', 'baseline.html', 'walkthrough.html', 'run.json', 'historical-outcomes.json']}, 'released_locally': state['released'], 'manual_review': state['human_review'], 'separate_review': state['reviewer'], 'context_version': state['context_pack']['version'], 'publication': 'Prepared files only; export does not publish or approve a release'}
    write(output / 'manifest.json', manifest)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime')
    parser.add_argument('--output', default='site')
    args = parser.parse_args()
    print(json.dumps(export(Demo(args.runtime), args.output), indent=2))


if __name__ == '__main__':
    main()
