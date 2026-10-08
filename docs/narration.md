# A 3–4 minute walkthrough

Use the actual application and recorded evidence. Adjust the review/release/learning section to the current state. Do not narrate a pending approval as completed. The exported 3:30 evidence-log playback is available without recording software; a live browser recording would add interaction proof after manual verification.

## 0:00–0:15 — Context

“This reconstructs a workflow I built at Thinkific. The original connected Claude, Grok Bot, Confluence, Drive and Cursor. Today I’m using Codex and a local relay, with synthetic data and a small demonstration application.”

## 0:15–0:45 — The insight

“The work started with an insight, not a request to add a button. Certification adoption was comparable to other products, but analytics access and usage were lower. These numbers are synthetic. We compare the same window, and keep adoption, dashboard visits and useful actions separate.”

## 0:45–1:15 — Investigation

“I explored whether people couldn’t find the dashboard, whether it appeared at the wrong point in their workflow, or whether the report itself wasn’t useful. The strategy and challenger contributions here came from actual Codex work. A contextual link looked like a small improvement worth testing. Then we asked where it belonged.”

## 1:15–1:45 — The relay

“In my original setup, the cloud agents couldn’t access our warehouse. I built a Drive inbox and outbox so they could ask Claude for analysis and receive it automatically. This reconstruction executes that request-and-response mechanism locally. The request stays pending until the separate worker completes it, and the data agent notifies the discussion when it arrives.”

## 1:45–2:15 — Validation and judgment

“The demo deliberately includes a misleading comparison. One placement uses eligible admins; the other uses people exposed to the link. The validator corrects that mismatch. The overview looks promising in this synthetic evidence, but other differences could explain it. Combined with the workflow context, it supports an overview candidate, not a claim of causation.”

## 2:15–2:50 — Working product and QA

“Here is the baseline, and here is the contextual link beside the program list. It opens analytics across all programs. The report also supports a useful renewal action. Checks cover navigation scope, event capture and QA marking. We measure useful activity beyond clicks. I’m not claiming a historical usage increase, and the authoring environment could not complete visual browser verification.”

## 2:50–3:10 — Review and release

If pending: “The code checks are complete, but this run is waiting for genuine manual review. The controller refuses to merge until the exact tested change has both manual and separate reviewer approval. The original change did ship after my review and my EM’s approval.”

If genuinely released: “This run records my manual review and a separate code reviewer’s approval. Both match the tested artifact. The controller merged it locally, then checked the released artifact. Nothing has been published.”

## 3:10–3:30 — Learning

“The other half of the system is shared learning. Proposed lessons remain outside authoritative context until reviewed. Approved lessons flow back into the source of truth and the refreshed agent context pack. The next task then receives those lessons. That is how I connected practical automation with continuing product judgment.”

If a lesson or next task is still pending, show that state and say so. If a subsequent agent actually applies the lesson, show its response and lesson id; do not treat prompt preparation alone as that result.
