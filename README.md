# From usage insight to shipped improvement

**Reconstructed from a workflow I built and used at Thinkific. Uses synthetic data and a demonstration application; original company code is excluded.**

I noticed that certification analytics had lower dashboard access and usage than other product areas despite comparable product adoption. That prompted an investigation of the customer workflow, followed by a question about where to add a contextual analytics link. I connected strategy, design, analysis and delivery agents so that they could get missing evidence, work through alternatives, and implement the change.

The original Analytics CTA was agent-built and agent-reviewed before human review and shipping, followed by another agent review in production. Bulma (staff engineer bot) built the change; my QA agent checked staging; I manually reviewed the ephemeral environment and GitHub checklist; my EM reviewed the PR; the engineering agent merged it; QA checked production. Dashboard click-through rose from **10% to 35% (+25 percentage points) over two weeks** among all certification users with dashboard access; **new active programs created increased approximately 10% month over month**. Higher-volume professional academies engaged more after clicking through, and recertification-enabled programs trended upward. These are user-confirmed historical observations, not synthetic demo results or isolated proof of causality. Calvin confirmed the historical placement was the overview: a link inside a program could imply program-specific analytics, while the initial dashboard covered all programs. Program-specific analytics was planned for a later slice. The expected interpretation was his hypothesis, not a measured expectation in the demo; synthetic placement analysis remains separate from the historical decision.

My prototyping covered two related experiences: the advanced analytics dashboard, and the certification overview, certificate designer and full end-to-end flow across the initial credential-rebuild slice and subsequent shipped slices for certification at scale. The cover links directly to a reconstruction of the overview; it does not reproduce original company designs or the complete historical designer and flow.

Before this workflow, I partnered with Analytics to create the advanced certification dashboard. I defined segments, jobs, requirements and longer-term strategic considerations, prototyped the experience and aligned success measures; Analytics implemented it. The legacy dashboard had not served professional certification customers' growing needs, especially recertification. The usage investigation started after the advanced dashboard launched.

My hypothesis was that visibility into program health and repeat-program revenue encouraged some customers to create more recertification-enabled programs. No revenue uplift or quantified recertification effect is claimed. `docs/historical-outcomes.json` records the confirmed scope and separate measurement windows.

## What you can inspect

The interactive workflow is the main experience. Edited recordings remain repository reference material; they are not linked from the cover or workflow. The page keeps concise comparison, design, QA and learning details. Raw request/response records and the repeated event timeline belong in repository evidence; the page links to that repository.

- `recordings/walkthrough.html`: a self-contained **3:30 edited playback of actual run evidence**. It performs no new inference and includes the captured candidate application. It is not an uninterrupted browser screen recording.
- `recordings/run.json`: actual local execution records, real Codex contributions, analysis results, checks, candidate commit and explicit approval state.
- `recordings/manifest.json`: export provenance and hashes. Missing human approvals remain pending.
- `recordings/walkthrough.mp4`, when present: captioned video rendered from the same recorded evidence; no audio or browser footage. The HTML version provides inspectable detail.
- `docs/narration.md`: narration and recording guide for a future browser walkthrough on your own machine.
- [AI Second Brain — Product Case Study](https://calvin-chow-pm.github.io/pm-ai-second-brain/): the original system's design, adoption and historical outcomes. Those outcomes are not attributed to this new reconstruction.

## GitHub Pages version

`site/` is the prepared hosting version. It opens with a concise cover page (`index.html`), then the seven-step workflow (`workflow.html`) and interactive baseline/candidate prototype, with a clearly labeled **saved snapshot of actual local execution**. It does not run agents, process warehouse requests, record server telemetry, or change release/learning approvals. Sample program edits stay in the visitor’s browser tab. The snapshot includes the approved lesson and subsequent Codex reasoning; local release remains pending. `site/manifest.json` records the source and output hashes.

For local review, open the cover at **http://127.0.0.1:8766/** or the static hosting preview at **http://127.0.0.1:8767/**. The cover leads with customer need, product response, post-launch investigation and outcomes. A smaller prototype link sits beside the product response; the larger interactive preview remains in Build & QA. The standalone prototype is published at `https://calvin-chow-pm.github.io/agentic-product-workflow/prototype.html?view=overview`. It opens the new certification experience directly, with browser-only sample edits. Future resume bullets can link to the cover, the standalone prototype, or `index.html#strategy`, `index.html#outcomes` and `workflow.html#2` for specific evidence. The walkthrough explains that its requests, analysis, agent outputs and checks are captured reconstruction records, rather than live agents on the hosted site.

To publish when ready:

1. Push **this folder’s contents as the repository root**, including `site/`, `.github/`, and the source. Exclude `.runtime/` and surrounding job-search documents; `.gitignore` already excludes runtime files.
2. In the repository’s **Settings → Pages**, choose **GitHub Actions** as the source.
3. In **Actions**, choose **Publish demo to GitHub Pages → Run workflow**. It validates and publishes only `site/`.
4. Use the URL shown by the deployment as the application link.

Updates to `site/` merged into `main` automatically validate and publish the prepared snapshot. The manual Run workflow option remains available. The public demo is at https://calvin-chow-pm.github.io/agentic-product-workflow/. Setup follows [GitHub’s custom Pages workflow documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

To preview just the static hosting version:

```sh
python3 -m http.server 8767 --bind 127.0.0.1 --directory site
```

Open **http://127.0.0.1:8767/**. The source works under a project URL such as `/repository-name/`; internal site paths are relative.

To refresh the snapshot after a genuine new local run:

```sh
python3 -m demo.pages --output site
python3 tests/test_pages.py
node tests/pages.test.cjs
```

This exports actual runtime state and requires an existing candidate; it never supplies missing approvals or replays old agent output as new inference. Commit the refreshed `site/` and merge into `main` to publish, or rerun the manual publishing workflow. The hosting walkthrough is regenerated with the snapshot; the earlier files in `recordings/` retain their original export provenance and earlier narrative. They predate the historical-outcome clarification; use the current cover and workflow for the confirmed account.

Both versions contain eight sample programs. The baseline program table contains Program, Course and edit/delete actions. The candidate adds Status, Certificate template and Tags, replacing per-row issued/renewal counts. Courses are required for certificate issuance. Use the row menu’s Manage tags modal to add or remove up to five tags; two show initially, with expand/collapse for the rest. The candidate also supports selecting rows or all programs, bulk tag addition/removal, and confirmed bulk deletion. Bulk tag edits validate the five-tag limit for every selected program before changing any row. Course, tag and deletion changes affect sample data in the browser tab only.

## Run locally

Requires **Python 3.9+**, **Git**, and a browser on macOS or Linux. The working demo uses only the Python standard library; no model API key, Claude Code, Grok Bot, cloud service, npm install or original company repository is required. Automated JavaScript unit checks additionally need Node.js. Optional video rendering needs Pillow and macOS developer tools/AVFoundation; neither is needed to run the demo.

From this folder:

```sh
python3 -m demo init
python3 -m demo serve
```

Open **http://127.0.0.1:8766**. The current workspace retains the actual run. In a freshly extracted source bundle, initialization starts a new baseline; the captured run remains available at `/walkthrough`.

Use `python3 -m demo --runtime /tmp/my-new-demo init` to start a separate run without overwriting one. Repeat `--runtime /tmp/my-new-demo` on every command for that run.

## Reproduce with Codex

This repository does not contain a pretend autonomous agent runtime. **Codex supplied actual strategy, challenger, design, engineering and independent review work during the captured run.** The files under `agents/` are portable task briefs, not automatically installed Codex configurations. In a new run, give Codex the relevant brief and let it call the scoped tools; its output and choices may differ.

1. Run `python3 -m demo discover`. The trusted analysis worker exports an initial insight with explicit populations and denominators.
2. Ask Codex to perform the strategy task in `agents/strategy.md`. It reads `python3 -m demo tool read_workspace`, submits a structured proposal and requests `placement-001` evidence. **Do not copy frozen proposals and call them new AI reasoning.** The JSON files in `recordings/` preserve this run's contributions.
3. Before servicing the request, `python3 -m demo tool check_inbox` reports pending. Run `python3 -m demo relay`, then `python3 -m demo validate`. Repeating the relay does not duplicate completed work; a changed completed request is rejected.
4. Ask Codex to perform challenger and design tasks using the exported response and validation.
5. Select an implementation candidate and create the working change:

```sh
python3 -m demo choose overview --rationale "Candidate based on validated evidence and workflow needs; measure before asserting an effect."
python3 -m demo build
python3 -m demo qa
```

The controller builds the chosen variant from the implemented application template and commits it on a **local fixture feature branch**. This is an actual Git operation, not a remote GitHub PR. The UI's original navigation remains available, alongside the proposed contextual CTA.

6. Review “Build & QA” in the browser. Manually inspect both the baseline and candidate, navigation, context and the useful analytics action. Record genuine manual review through the UI or `human-review`. Ask a separate reviewer to inspect the exact candidate, then record their actual review through `reviewer-approve`. No agent tool can grant either approval. The local form is an attestation, not an authenticated identity system.
7. Run `python3 -m demo release` and `python3 -m demo qa --production`. The controller checks the exact file hash, commit, clean tree, passing QA, two approvals and distinct reviewer names before merging locally. An absent review blocks release. Nothing is published.
8. Stage a lesson with the `stage_learning` scoped tool. `python3 -m demo sync` excludes pending lessons. After an actual human approves a lesson in the UI or with `approve-learning`, run `sync` again. Approved lessons return to authoritative context and appear in the next context pack.
9. Run `python3 -m demo reuse`. It **assembles the subsequent task prompt from actual approved lesson text**. Give that prompt to Codex to perform the subsequent task. Prompt assembly alone is not represented as completed agent reasoning.
10. Run `python3 -m demo record` to refresh the immutable playback and provenance manifest from the actual run.

For JSON tool arguments, use `--file` to avoid shell quoting issues:

```sh
python3 -m demo tool submit_proposal --file my-proposal.json
```

The file shape is `{"role":"strategy","value":{"observations":[],"hypotheses":[],"alternatives":[],"recommendation":"..."}}`. The controller supplies provenance; proposals cannot overwrite it.

## The boundary and the relay

The cloud-agent surface exposes only five tools: exported workspace reading, fixed aggregate analysis requests, inbox checking, proposal submission and learning staging. There is **no shell, filesystem path, raw SQL, raw-data read, release approval or learning approval tool**. The trusted worker alone reads the analysis dataset through this interface. Unsupported operations, path traversal and extra request parameters are rejected.

`python3 -m demo mcp` exposes this surface as a standard stdio MCP server. A client must be configured to use only that server, with generic filesystem/shell tools and unrelated connectors disabled, for the demonstrated tool boundary to apply. No app settings or connector permissions have been changed by this project. The Codex authoring sessions used the same command interface under task instructions, but had trusted host access: **this is not an operating-system sandbox or protection from a malicious local user.** All source data is intentionally synthetic and inspectable in this repository.

The local HTTP server binds only to loopback. It exposes the UI and curated run state, not raw-data or arbitrary-file routes. A per-server review token protects mutating UI actions from ordinary cross-origin requests. It does not authenticate reviewer identity.

## Historical architecture versus this reconstruction

| Historical setup | Current reconstruction |
|---|---|
| Claude: PM self, memories, communication and decision preferences, domain context | Versioned authoritative context with illustrative preferences and reviewed demo lessons |
| Grok Bot: persistent specialized agents and group discussions | Real Codex tasks with explicit roles; captured contributions |
| Confluence: context pack refreshed automatically weekly, both ways | Local context pack; explicit two-way `sync` command |
| Google Drive `_outbox` / `_inbox`: automatic deep-data request relay | Executable local request/response relay; explicit worker command |
| Claude analysis via company systems unavailable to Grok Bot | Trusted worker over synthetic aggregate datasets |
| Bulma / Cursor: prepare and implement code changes | Codex-built demo application and local Git fixture |
| Agent build → agent staging review → manual review → EM approval → merge → agent production review | Executable checks plus explicit human and separate reviewer gates; identity and scope disclosed |

The original system replaced fragmented context, manual cross-tool analysis handoffs, repeated corrections, and disconnected product-to-engineering preparation. This reconstruction demonstrates those mechanisms without claiming an identical infrastructure deployment.

## What did not work, and what changed

- A deliberately seeded comparison used eligible admins for one placement and exposed active admins for the other. The validator corrected it. **This particular failure is invented for the demo**, not a historical incident.
- Real historical failure lessons included confidently fabricated evidence, incompatible prototype assumptions, and a silently failing digest. Those motivated explicit evidence checks and review. No private transcripts or internal files are reproduced here.
- During this reconstruction, independent review caught program filtering that changed only a label, QA markers lost during navigation, and learning reuse that was initially predetermined. Those were corrected and tested; actual review findings are preserved in `docs/review-notes.md`.

## Verification and limits

```sh
python3 -m unittest discover -s tests -v
node tests/dashboard.test.cjs
node tests/programs.test.cjs
node tests/pages.test.cjs
```

Tests exercise comparable populations, pending responses, duplicate and concurrent processing, altered requests, invalid cohorts/windows, scoped tools, provenance, stale approvals, separate reviewers, actual local Git merge, production hashes and reviewed context propagation. JavaScript unit tests execute the real inline app script against a small DOM stub; they are **not visual browser QA**.

Browser automation was blocked by an unavailable security-policy check in the authoring environment. No alternate browser automation was used to bypass it. Visual layout and end-to-end browser interaction remain for manual review; the recording is accurately labeled as evidence-log playback. No customer uplift is measured by the synthetic reconstruction. Historical outcomes are separately attributed to Calvin’s confirmed account; no company-wide AI policy, LLM accuracy score or reconstructed-system performance improvement is asserted.

## Publication boundary

Only this demonstration folder belongs in the public repository. `.runtime/`, its fixture Git history, caches and surrounding career-source files are excluded from the source bundle. The exported recordings contain synthetic evidence and public professional context. The repository and Pages site contain only this demonstration folder. No application submission or outreach is performed by the demo.
