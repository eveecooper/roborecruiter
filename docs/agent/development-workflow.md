# Development workflow

**How work gets from the plan into the code.** What to build is
[`docs/planning/10-build-plan.md`](../planning/10-build-plan.md); how to write it is
[`coding-standards.md`](coding-standards.md); this is who does what.

## New requests go into the plan before they get built

**This is the rule the rest of the file serves.** When the owner asks for something, it is
recorded before any code is written for it:

1. **Find its stage.** Does it depend on something that does not exist yet? That answers it. A
   feature needing fit scores cannot land before the model does.
2. **Write it down** - a row in [`12-feature-inventory.md`](../planning/12-feature-inventory.md),
   and a paragraph in the build plan if it changes what a stage contains.
3. **If it changes a decision**, it needs an ADR, not an edit. A decision that quietly changed is
   indistinguishable from a decision nobody made.
4. **If it cannot be placed**, say so rather than building it anyway. "Deferred, because X does not
   exist yet" is a complete answer.

Building something that is not in the plan is how the plan stops being true. It has already
happened once in this project: personas were implemented in `profile.yaml` and `config.py` before
appearing in any planning document, and the gap was found by accident rather than by a check.

**A large batch of requests is still one request at a time.** Each gets a stage or a deferral
before any of them get code.

## The plan is the delegation

**Do not build a project-manager agent.** Each step in the build plan already carries deliverables
and exit criteria. A PM agent would re-derive that context on every invocation and hand back a
lossier version of a document that is already explicit.

| Role | Use | Why not an agent |
| --- | --- | --- |
| Delegation | `to-tickets` over the build plan's steps, one ticket per step | The plan and tickets are the artifact; an agent re-reads them to say the same thing |
| Build | `implement`, the coding standards, and test-first where it fits | A fresh agent per ticket is right; what it needs is a *standard to read*, not a personality |
| Review | `/code-review`, plus `/bob` for scope and `/tbro` for feasibility | All three exist already and are read-only |
| Verify | Run the step's exit criteria | Evidence before claims is a procedure, not an actor |

## Token cost: more agents means more tokens, not fewer

Every fresh subagent re-reads the documents to rebuild context. The levers that actually reduce
usage here:

- Keep `CLAUDE.md` and [`README.md`](README.md) small. They load every session whether or not they
  are needed.
- Use `/rr-refresh` instead of cold-reading the planning set.
- Use subagents for **fan-out search**, where file dumps stay out of the main context and only the
  conclusion returns. Not for sequential handoffs, where the handoff is the cost.

## What makes a step land in few iterations

- **Acceptance criteria written before code.** Already in the build plan per step. A ticket whose
  "done when" is vague is not ready to delegate.
- **Steps sized to one session.** If a ticket cannot be finished *and verified* in one sitting,
  split it before starting.
- **Verification is part of the ticket**, so "done" means demonstrated rather than asserted.

## Debugging is expected

"No debugging required by the end" is not reachable, and designing for it produces worse code than
planning for cheap debugging. Bugs are how a wrong assumption gets found, and this plan names
several assumptions it has not verified.

Everything in the coding standards is chosen so a defect is cheap to fix: small modules, a fake at
every seam, structured logs, and numbers in config rather than in code, so a wrong value is an edit
rather than a rewrite.

**The measure is time-to-fix, not absence of bugs.**
