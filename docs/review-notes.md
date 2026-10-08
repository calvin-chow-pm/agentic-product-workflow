# Independent review and corrections

The captured run used real Codex strategy/design work and a separate Codex code reviewer. The reviewer identified:

1. Learning reuse initially emitted fixed instructions. It now builds the next task prompt from the actual approved lesson text; prompt assembly is not presented as completed subsequent reasoning.
2. Program filtering initially changed only scope text. Synthetic program-specific counts, chart and renewal result now change as well.
3. QA marking could be lost across navigation. All internal query links now preserve it.
4. Production checks initially inspected the candidate. They now inspect the production route/artifact and reviewed release hash.
5. Proposal content could override provenance. Reserved fields are now rejected.
6. Released placement could be changed. Released runs now reject reselection.
7. Link comparisons assumed valid data. Counts and common windows are now validated before pooling.

The Python acceptance tests and real inline-JavaScript unit tests pass. Visual browser verification remains unavailable because the browser security-policy check failed. No approval by Calvin or a historical EM is fabricated.

The exported execution log records whether genuine manual review and separate approval have been supplied for the current candidate. Disposable test fixtures exercise approvals/merge using explicitly synthetic reviewer names; those are not imported into the actual run.
