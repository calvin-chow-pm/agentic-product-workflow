# QA and independent review task

Review the implemented candidate and exact commit. Check placement, destination scope, QA event persistence, meaningful action, release freshness and provenance. Run `python3 -m demo qa` and, with Node available, `node tests/dashboard.test.cjs`.

Distinguish HTTP, unit, static and visual checks. If browser access is blocked, disclose it; do not bypass security controls. A code reviewer may approve code scope under their own identity, but must not impersonate Calvin or an EM. Human manual review remains separate. Recheck the released artifact only after an actual release.
