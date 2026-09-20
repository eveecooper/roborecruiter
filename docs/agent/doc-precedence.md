# Which planning document wins

The planning documents contradict each other in places. This is deliberate: the project was planned
in drafts, and a later draft revised an earlier one rather than replacing it. Both were kept, the
first as a record of intent and the second as the working plan.

## The rule

| Rank | Document | Authoritative on |
| --- | --- | --- |
| 1 | [`docs/adr/`](../adr/) | The single decision each ADR records. Outranks everything below |
| 2 | [`01-engineering-plan.md`](../planning/01-engineering-plan.md) | Anything operational: scope, stage design, data model, milestones, acceptance criteria, standards, technology |
| 3 | [`00-product-overview.md`](../planning/00-product-overview.md) | Product intent only: goals, limitations, accepted restrictions. Its engineering specifics are stale |
| - | [`02-deferred-investigations.md`](../planning/02-deferred-investigations.md) | Nothing. An item here is an *open question* that no document settles |

When the two drafts conflict, the engineering plan wins. Draft 1 lists the known conflicts in its
own [Superseded points](../planning/00-product-overview.md#superseded-points) section, but that
table records the conflicts found during review, not necessarily all of them.

The concrete trap: draft 1 says browser prefill is in the first build, that applications should take
under five minutes, and that a daily cap exists. Draft 3 reversed all three. Citing draft 1 for an
engineering fact means reading the wrong document.

## Lineage

```
00-product-overview.md   draft 1   original product brief
        | revised into
01-engineering-plan.md   draft 2   engineering revision of the brief
        | reviewed, findings applied
01-engineering-plan.md   draft 3   current - see 03-review-log.md for what changed and why
        | unresolved items spun out to
02-deferred-investigations.md      open questions A through G
```

Drafts 2 and 3 are the same file; git holds the history. Draft 1 is a separate document because it
records intent rather than implementation, and that intent is still worth reading.

## Open questions are not yours to close

Investigations A through G are open on purpose. Several are routed to outside expertise - legal
review of crawl policy, entity-resolution thresholds, browser submit-boundary safety. Picking an
answer because one seems reasonable defeats the point of having deferred it. Flag the question
instead, and say plainly that it is unresolved.

## Conventions

- Every planning document carries YAML front matter with `draft` and `status`. If front matter and
  this page disagree, fix one immediately: a precedence rule that contradicts itself is worse than
  none.
- Numeric filename prefixes give reading order, not importance.
- Filenames describe the document, not the editing event. "Revised", "final", and "v2" belong in
  git history.
- A change to a planning decision gets recorded in
  [`03-review-log.md`](../planning/03-review-log.md) with its reasoning. No silent rewrites.
