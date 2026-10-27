# Coding standards

**Read this before writing code on any ticket.** It is short on purpose. What to build and in what
order is [`docs/planning/10-build-plan.md`](../planning/10-build-plan.md); this file is only *how*.

The goal these serve is not elegance. It is that a wrong decision is cheap to reverse, because this
plan contains several assumptions it openly flags as unverified.

## Configuration over code

Thresholds, limits, model aliases, caps, filter weights, radii, timeouts and retry counts live in
`config/`, never as literals in a function. **A number that might change is a config key.**

Every config file carries a `schema:` integer, checked at load. A file with an unexpected value is
**refused with a message**, never parsed on a best-effort basis. Alembic migrates database tables;
nothing migrates YAML, so this field is the only defense against silently mis-reading an old file.

## Config profiles, never branches

Environments are configuration, not code. Long-lived `demo` / `dev` / `prod` branches would mean
three codebases that drift, every fix needing three merges, and a bug fixed in one silently alive in
the others. **Branches are for work in progress.**

The mechanism is overlay files and one switch, not a flag framework:

- `config/run.yaml` — shared defaults
- `config/run.dev.yaml` — real data, verbose logs, low caps
- `config/run.demo.yaml` — sample data, nothing recorded as a real application, no network
- `config/run.prod.yaml` — the actual job search

`rr --profile demo <command>` selects one; `prod` is the default when the flag is absent. Where a
capability must be switchable independently of profile, add a named boolean to the config — not a
fourth profile.

**Three environments, not four.** The fourth would be UAT, where someone other than the developer
validates a release. On a single-applicant tool the owner is both people, and an unexercised fourth
config path is a liability rather than a safety net.

## One module per concern, one seam per swappable thing

The seams are listed in the build plan. A new tool **replaces an implementation behind a seam; it
never edits a caller.** If swapping a component requires touching its consumers, the boundary is in
the wrong place.

Write for the next rewrite: small files, explicit inputs and outputs, no hidden state. **If a module
cannot be understood without reading its callers, the boundary is wrong.**

Excluded as premature: adapter registries, plugin entry points, dependency-injection containers,
import-linter. One process, plain function calls, direct imports. The only justified separate process
is the eventual browser worker, and only because it makes "exposes no submit" a process-level claim
rather than a code-review claim.

## Tests at the seam, not at the function

**Every seam gets a fake implementation.** That is what makes a swap cheap and what keeps a failure
local instead of cascading into an unrelated test.

Test the behaviour at the boundary, not the internals behind it — internals are expected to be
replaced, and a test bound to them turns a planned replacement into a rewrite of the test suite.

Three assertions are non-negotiable and run from step 1.0:

1. No module exposes a submit, click-to-submit, or form-post operation.
2. No module imports `httpx`, `requests`, or `playwright` (stages 1–2).
3. Posting text is never used as an instruction, a path, a filename, or a shell argument.

## Type annotations, checked

Annotate every public function. The checker is **Pyright in `basic` mode**, which is what the
VS Code Pylance extension runs, so the editor and CI agree rather than disagreeing.

Not `strict`: it demands annotations for third-party internals this project does not own, and the
noise trains people to ignore the output. Basic catches the errors that actually happen here -
a wrong argument type, an unhandled `None`, a renamed field still referenced somewhere.

The previous engineering plan specified "strict type checking with mypy or pyright". This is the
narrower version of that, chosen because an unread checker is worth nothing.

## Structured logs

Every log line carries the run, posting and application identifiers where they apply. This is the
difference between reading a log and reproducing a problem. Omit or redact personal information that
the line does not need.

## Readable over clever

Google-style docstrings on public interfaces. Comments explain **why**, never what the code already
says. Keep comments short and sweet, and dense meaning. No metaphors, straightforward explanation, and plain and simple explanation. Don't be clever. Match the surrounding style if it makes sense to.

## Untrusted input

Posting text, employer pages, and anything fetched are untrusted data in every stage. They are never
concatenated into an instruction, a template context without escaping, a file path, or a shell
argument. The renderer accepts only fields the template declares.

## What "done" means on a ticket

- The exit criteria in the build plan for that step are demonstrated, not asserted.
- Verification is part of the ticket, so finishing means having run it.
- If a ticket cannot be finished and verified in one working session, **split it before starting.**

## Debugging is expected, and that is the point

An earlier goal for this project was that no debugging would be required by the end. That is not
reachable, and designing for it produces worse code than planning for cheap debugging — bugs are how
a wrong assumption gets found, and this plan has several it names as unverified.

Everything above is chosen so that a defect is cheap: small modules, a fake at every seam, structured
logs, and numbers in config rather than in code, so a wrong value is an edit rather than a rewrite.

**The measure is time-to-fix, not absence of bugs.**
