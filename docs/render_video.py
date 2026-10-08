"""Typeset real exported event evidence as captioned frames, never fake screenshots."""
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "recordings"
CHAPTERS = json.loads((OUT / "chapters.json").read_text())


def font(size, mono=False, bold=False):
    names = ["Menlo.ttc"] if mono else (["Arial Bold.ttf", "Arial.ttf"] if bold else ["Arial.ttf"])
    for folder in [Path("/System/Library/Fonts/Supplemental"), Path("/System/Library/Fonts")]:
        for name in names:
            path = folder / name
            if path.exists():
                return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def wrapped(draw, text, xy, f, fill, width, gap=9):
    x,y = xy
    line = ""
    for word in text.split():
        candidate = (line + " " + word).strip()
        if draw.textlength(candidate, font=f) > width and line:
            draw.text((x,y), line, font=f, fill=fill)
            y += f.size + gap
            line = word
        else:
            line = candidate
    if line:
        draw.text((x,y), line, font=f, fill=fill)
        y += f.size + gap
    return y


def excerpt(index, chapter):
    evidence = chapter["evidence"]
    if index==0:
        return ["Actual Codex contributions", "Executable Python analysis relay", "Local Git candidate + QA checks", "Explicit review + learning gates", "", "No company code or live company data"]
    if index==1:
        rows=evidence["rows"]
        return ["Product       Adoption   Access  Action", "--------------------------------------"] + [f"{r['product']:<13} {r['adoption']*100:5.1f}%   {r['access']*100:5.1f}%  {r['engagement']*100:5.1f}%" for r in rows] + ["", "Same 28-day window", "Access/action: active product admins", "Adoption: eligible admins"]
    if index==2:
        return ["OBSERVATION", "Comparable adoption; lower reach", "", "HYPOTHESES", "Discoverability / timing / report value", "", "ALTERNATIVES", "Overview link / contextual program link", "Improve report value / check access", "", "No causal conclusion"]
    if index==3:
        es=evidence['relay_events']
        return ["placement-001", "operation: link_usage", "", "_outbox -> analysis worker -> _inbox", ""] + [f"{e['id']:02d}  {e['phase']}" for e in es]+["", "Repeated request: no duplicate work", "Missing response: remains pending"]
    if index==4:
        return ["SEEDED FAILURE", "71 / 240 eligible admins = 29.6%", "49 / 175 exposed admins = 28.0%", "", "CORRECTED", "71 / 155 exposed admins = 45.8%", "49 / 175 exposed admins = 28.0%", "", "Candidate: overview context", "Not a randomized experiment"]
    if index==5:
        qa=evidence.get('qa') or {}
        return ["Actual candidate commit", (evidence.get('candidate_commit') or '')[:20], "", f"HTTP checks: {'PASS' if qa.get('passed') else 'PENDING'}", "CTA placement + destination scope", "Event capture + raw-data routes denied", "", "Inline JavaScript unit checks: PASS", "Visual browser verification: unavailable", "No measured CTA uplift"]
    if index==6:
        return ["Manual review:", "Recorded" if evidence['human_review'] else "PENDING - not fabricated", "", "Independent code review:", "Recorded" if evidence['separate_reviewer'] else "Pending", "", "Local release:", "Completed" if evidence['released'] else "BLOCKED until actual manual review", "", "No remote publication"]
    context=evidence['context_pack']
    return [f"Context pack v{context['version']}", f"Approved demo lessons: {len(context['learnings'])}", "", "Pending lessons excluded", "Explicit two-way context refresh", "", "Subsequent task:", "Prompt prepared from approved lessons" if evidence['subsequent_task'] else "PENDING reviewed context", "", "Canonical career sources unchanged"]


manifest={"format":"Captioned video of recorded event evidence; no browser footage or audio", "frames":[], "output":"recordings/walkthrough.mp4"}
elapsed=0
for i,c in enumerate(CHAPTERS):
    image=Image.new("RGB",(1600,900),"#f3f6f7")
    draw=ImageDraw.Draw(image)
    draw.rectangle((0,0,1600,78), fill="#153143")
    draw.text((65,27),"CALVIN CHOW / AGENTIC PRODUCT WORK",font=font(20,bold=True),fill="#b5ded6")
    draw.text((1060,29),"ACTUAL RUN EVIDENCE · SYNTHETIC INPUTS",font=font(15),fill="white")
    draw.text((65,116),f"{i+1:02d} / {len(CHAPTERS):02d}    {elapsed//60}:{elapsed%60:02d}",font=font(20,bold=True),fill="#087e81")
    wrapped(draw,c['title'],(65,168),font(52,bold=True),"#153143",1450,7)
    wrapped(draw,c['subtitle'],(65,294),font(23),"#627985",1420,6)
    draw.rounded_rectangle((65,373,817,760),radius=16,fill="white",outline="#dce5e8",width=2)
    draw.text((92,401),"PRODUCT JUDGMENT",font=font(17,bold=True),fill="#087e81")
    wrapped(draw,c['takeaway'],(92,455),font(30),"#153143",685,12)
    draw.rounded_rectangle((844,373,1535,760),radius=16,fill="#e8f0ef",outline="#dce5e8",width=2)
    draw.text((871,401),"CAPTURED OUTPUT / ACTUAL EXECUTION",font=font(17,bold=True),fill="#087e81")
    y=445
    for line in excerpt(i,c):
        draw.text((871,y),line,font=font(20,mono=True),fill="#35545c")
        y+=26
    draw.text((65,798),"Reconstructed from a workflow I built and used at Thinkific. Original company code excluded.",font=font(18),fill="#627985")
    draw.text((65,831),"Edited evidence-log walkthrough · Not a browser screen recording · No CTA uplift asserted",font=font(17),fill="#627985")
    draw.rectangle((0,885,1600,900),fill="#dce6e5")
    draw.rectangle((0,885,int(1600*(i+1)/len(CHAPTERS)),900),fill="#087e81")
    path=OUT/f"chapter-{i+1:02d}.png"
    image.save(path)
    manifest['frames'].append({"path":"recordings/"+path.name,"duration":c['duration']})
    elapsed+=c['duration']
(OUT/'video-manifest.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({"frames":len(CHAPTERS),"duration_seconds":elapsed,"manifest":str(OUT/'video-manifest.json')}))
