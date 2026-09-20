# Agent materials

**For coding agents. A person does not need anything in this folder** - start at the
[root README](../../README.md) instead.

These files exist because the planning documents carry history an agent cannot infer from reading
them: which draft is current, which conflicts are deliberate, and which questions are open on
purpose. Without that, an agent reading the oldest document first will confidently implement
decisions that were reversed.

| File | Read it when |
| --- | --- |
| [`doc-precedence.md`](doc-precedence.md) | Before acting on anything in `docs/planning/`. Which document wins, and why they disagree |

[`CLAUDE.md`](../../CLAUDE.md) at the repo root carries the rules that always apply and is loaded
automatically. This folder holds the detail behind them, read on demand.

## Keeping this folder useful

It is loaded into a limited context window, so it stays small. Detail belongs in the planning
documents; this folder holds only what an agent needs *before* it can read those correctly.

If something here duplicates a planning document, the planning document is the source of truth and
the copy here should become a link.
