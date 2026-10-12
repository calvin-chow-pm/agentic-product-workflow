# From usage insight to shipped improvement

**Reconstructed from a workflow I built and used at Thinkific. The interactive pages use sample data and a demonstration application; original company code is excluded.**

I led certification and recertification at Thinkific from customer research through launch, then directed an AI agent team to find and fix a post-launch analytics adoption gap. Bulma, my staff-engineer bot, prepared the pull request through Cursor; after agent QA and my review in the preview environment, my engineering manager approved and merged it; then QA rechecked production.

**+4 points net revenue retention** for target certification customers (93% → 97%, quarter over quarter) after certification and recertification launched. **Dashboard click-through moved from 10% to 35%** within two weeks of release among certification users with dashboard access. Those windows are separate, not one causal chain. Deals lost mainly to certification gaps were cut in half (12 → 6, $143K). Certificate designer time, the setup guardrail, moved from about 230 seconds to about 190 seconds.

## What you can open

The public site is [https://calvin-chow-pm.github.io/agentic-product-workflow/](https://calvin-chow-pm.github.io/agentic-product-workflow/). `site/index.html` is the cover, `site/workflow.html` is the seven-step walkthrough, and `site/system.html` is monitoring and evaluation. Sample program edits stay in the browser tab. The hosted pages do not run agents, read a warehouse, or approve a release.

Preview the static site locally:

```sh
python3 -m http.server 8767 --bind 127.0.0.1 --directory site
```

Open http://127.0.0.1:8767/. The local demo needs Python 3.9+ and no API key: run `python3 -m demo init`, then `python3 -m demo serve`, and open http://127.0.0.1:8766/.

Publish steps, agent briefs, checks, and the captured-run guide are in [docs/full-walkthrough.md](docs/full-walkthrough.md).
