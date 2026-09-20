---
doc: open-investigations
status: open-items
derived_from: 01-engineering-plan.md
---

# Open Engineering Investigations

> **Open questions.** An item here is undecided on purpose, and no answer should be inferred
> from any other document. Each brief names who should answer it, what it unblocks, and what it
> costs to keep deferring it.

These investigations intentionally follow the engineering plan rather than blocking the first build.

| Brief | Question | Unblocks | Status |
| --- | --- | --- | --- |
| A | Discovery-noise threshold | M1 exit, discovery config | Deferred - needs M1 data |
| B | Cross-source entity-resolution threshold | Auto-merge policy | Deferred - needs a second source |
| C | Browser-prefill submit boundary | Post-M6 prefill adapters | Deferred - needs M6 complete |
| D | Source policy: crawler identity, robots vs. ToS, retention | M2 start | **Open now - blocks M2** |
| E | Hiring-platform census | M4 adapter build list | Open at M2 completion |
| F | Claim-check feasibility without a model | M5 acceptance criteria | **Open now - blocks M5 wording** |
| G | Effort instrumentation and its statistics | M6 acceptance criteria | Open - small, owner decision |

## Investigation A - Discovery-noise threshold after M1

**Best owner:** senior data/relevance engineer, search quality engineer, or applied data scientist with experience in information retrieval evaluation and labeled datasets.

**Start condition:** M1 discovery spike has completed and produced the full returned-employer set plus discovery-accounting labels.

**Unblocks:** the discovery noise threshold in run configuration, and the M1 regression gate for later Overture releases.

**Cost of deferring:** none for the first build. Without a threshold, discovery noise is observed and reported but not gated, so a later Overture release could quietly degrade precision without failing anything.

**Question:** What regression threshold should the project use for discovery noise without hiding meaningful employer recall?

**Inputs:** all M1 returned records; the sampled answer key and the applicant's recalled list, kept separate; accounting labels (eligible, closed, duplicate, wrong-category, outside-radius, junk/unverifiable, eligible-without-website); query/config fingerprint; Overture release.

**Work:**
1. Define the measurement denominator explicitly. Report both raw-result precision and post-dedup/filter precision rather than a single ambiguous "noise rate."
2. Treat eligible-without-website as valid, not noise.
3. Calculate counts and rates for each failure category and the downstream handling cost of each category. Weight the categories rather than pooling them into one rate: a closed restaurant costs one wasted fetch, while a wrong-category record costs a fetch, a Gate 1 row, and applicant attention. Report a cost-weighted noise rate with the weights written down.
4. Bootstrap or use a binomial/Wilson interval where appropriate so the proposed threshold is not based only on one point estimate. Note the asymmetry before starting: precision is measured over the full returned set, likely hundreds of rows, and can support a threshold from one pilot. Recall is measured over a much smaller answer key, where at 20 employers the interval is roughly plus or minus 17 points, and cannot. Do not spend effort trying to set a recall SLO the data cannot carry.
5. Evaluate how tighter filters affect known-employer recall. Do not optimize noise independently of recall.
6. Propose a regression SLO only if the sample is large enough to support one. Otherwise propose a monitoring band and require another pilot area before setting a hard threshold.

**Deliverable:** short ADR or experiment report defining the metric, denominator, baseline, confidence interval, proposed threshold/monitoring band, and the observed recall tradeoff.

**Acceptance:** the proposed threshold has an explicit rationale tied to applicant workload and coverage; it is not an arbitrary percentage.

---

## Investigation B - Cross-source employer entity-resolution threshold

**Best owner:** senior data engineer or ML/data scientist specializing in entity resolution, record linkage, deduplication, geospatial data, or search indexing.

**Start condition:** at least one fallback employer source has been run over the same pilot area so Overture/Foursquare/Google/manual records overlap.

**Unblocks:** whether automatic cross-source employer merging is enabled at all, and at what threshold.

**Cost of deferring:** low. Flagged-only merging is the safe default and is already the plan. The cost is applicant review time on duplicate candidates, bounded by the number of overlapping sources, which is currently one.

**Question:** Which employer-location matches are safe to auto-merge, which require review, and which must remain separate?

**Inputs:** overlapping source records with name, address, coordinates, website/domain, phone, categories, source IDs, and manually labeled same/different employer-location pairs.

**Work:**
1. Generate candidate pairs by blocking before labeling anything. Labeling all pairs is quadratic in the number of records and will not get done. Block on any of: within 150 metres, same normalized domain, same normalized phone, or a shared rare name token. Record blocking recall separately so the next reader knows what the blocker itself discarded before any model saw it.
2. Build a labeled pair set from those candidates containing easy matches, hard matches, chains, restaurants in shared complexes, moved locations, duplicate listings, and similarly named but distinct businesses.
3. Evaluate deterministic exact/normalized rules first: native crosswalk IDs if available, normalized phone, normalized domain, exact address plus name, and tight geospatial matches.
4. Evaluate fuzzy features only after the deterministic baseline: token/name similarity, address similarity, phone/domain agreement, category agreement, and distance.
5. Measure precision and recall for candidate thresholds. Weight a false merge more heavily than a missed merge because a false merge can corrupt application history and duplicate prevention. The reverse cost is largely absorbed by the employer-plus-role duplicate guard in the engineering plan, which catches a double application even when two records were never merged. That guard is what allows this band to stay conservative, so confirm it is in place before relying on the asymmetry.
6. Confirm, rather than assume, Overture's stability guarantee for GERS identifiers across monthly releases, and whether a changed GERS ID implies a genuinely different place. The plan's source-ref design assumes repeat scans update observations instead of creating new logical employers, and that assumption rests on this.
7. Recommend three bands: auto-merge, manual-review candidate, and no-merge.
8. Add a regression fixture of labeled pairs before enabling automatic fuzzy merge.

**Deliverable:** entity-resolution ADR containing features, labeled-set composition, confusion matrix/PR curve, auto-merge threshold, review band, and examples of failure modes.

**Acceptance:** the auto-merge band demonstrates very high measured precision on the labeled overlap set and every rule is reproducible. If the evidence is not strong enough, retain manual/flagged merge only.

---

## Investigation C - Browser-prefill submit-boundary and portal adapter safety

**Best owner:** senior browser-automation engineer with Playwright expertise plus web-application security experience. Ideal background includes form automation, SPA behavior, iframe/shadow-DOM handling, network interception, and threat modeling. A security engineer should review the final design before production use.

**Start condition:** M6 succeeds without browser prefill and the pilot identifies the one or two hiring platforms worth automating first.

**Unblocks:** any browser-prefill adapter reaching production.

**Cost of deferring:** none to correctness. Prefill is a time saver, not a capability the pipeline depends on, and M6 completes without it. Deferring costs applicant minutes per application and nothing else.

**Question:** Can a bounded portal adapter fill approved fields and reliably hand off before human verification, attestations, or submission, including when the portal changes or behaves unexpectedly?

**Important constraint:** do not attempt to prove that one generic browser worker can prevent every conceivable third-party page from triggering an equivalent submission action. The investigation should establish a defensible safety boundary for specific supported adapters and define fail-closed behavior for unknown pages.

**Work:**
1. Threat-model all ways a final action can occur: submit buttons, Enter-key submission, auto-submit JavaScript, multi-step forms where "Continue" becomes final submission, iframe controls, SPA network calls, keyboard shortcuts, and navigation side effects.
2. Keep the production API narrow: `prefill_until_handoff()` only. Do not expose `submit()` to the workflow layer.
3. Build a synthetic hostile-form test site that attempts auto-submit on input/change/Enter/navigation and records all submit-equivalent network events.
4. Instrument the browser worker to observe navigation, form submit events, and relevant network requests; fail closed when behavior is outside the adapter's expected state machine.
5. Disable inherited sessions, extensions, arbitrary downloads, and unrelated credentials; use an ephemeral isolated context/process.
6. For each target hiring platform, model an explicit state machine and enumerate which controls the adapter may interact with. Pin a portal fingerprint, a hash of the form's structural signature, checked at session start, so a portal redesign is detected before the adapter touches anything rather than discovered by its behaviour partway through. Add recorded/saved fixtures where possible and live smoke tests where permitted.
7. Verify handoff behavior for CAPTCHA, MFA, login/account creation, attestations, voluntary demographic sections, unknown free-form questions, unexpected DOM/layout, and final review/submit screens.
8. Model server-side partial-application creation as a distinct outcome, separate from final submission. On many portals, uploading a file or completing step one of a multi-step form persists state the employer can see. That is an outward-facing side effect with no submit event to detect, and an acceptance criterion counting only final-submit events would pass while it happens. Decide per platform whether the adapter stops before any request that persists state employer-side, or whether that behaviour is documented and accepted.
9. Decide whether additional containment is warranted, such as network-level blocking of known submission endpoints until human takeover. This must be platform-specific; do not generalize endpoint assumptions across portals.

**Deliverable:** portal-prefill ADR, threat model, synthetic hostile-form test suite, adapter state machine, fail-closed rules, and a per-platform go/no-go checklist.

**Acceptance:** each enabled platform adapter passes its state-machine tests and hostile-form tests, reaches a deterministic handoff state, and records zero automated final-submit events and no unapproved server-side partial application. A portal redesign is detected and fails closed rather than being tolerated. Unknown or changed states stop rather than guessing.

---

## Investigation D - Source policy: crawler identity, robots versus terms, and snapshot retention

**Best owner:** technology and privacy counsel, with a crawler engineer for the technical half.

**Start condition:** open now. This one blocks M2 rather than following it.

**Unblocks:** M2 fixture capture, the crawler's user-agent decision, and the retention period left open in the engineering plan.

**Cost of deferring:** M2 proceeds on an unwritten policy. Saved fixtures are the part at risk, because they are the one place the project retains third-party content, and reversing that decision later means discarding the fixture corpus the detector was built against.

**Question:** What are this project's rules for identifying itself, for resolving robots.txt against a site's terms of service, and for retaining copies of employer pages?

**Work:**
1. Decide the crawler's user-agent identity and contact string.
2. Decide precedence when robots.txt permits and terms of service forbid, or the reverse.
3. Decide whether retaining local snapshots of third-party employer pages is acceptable, and for how long. This also settles the retention period left open in the engineering plan.
4. Decide whether applicant-initiated capture on a restricted source such as Indeed differs from automated access.

**Technical sub-question for the crawler engineer:** an honest custom user-agent raises block rates on sites behind a WAF, which directly inflates M2's blocked-outcome rate and can fail its pass criteria. Weigh a custom user-agent against a standard one paired with honest contact headers and a contact page. This is a real tradeoff between compliance posture and measured detection performance, and it should be decided deliberately rather than by default.

**Deliverable:** a written source policy in `docs/adr/`, covering identity, precedence, retention, and restricted sources.

**Acceptance:** M2 can point at a specific clause for every fetch and retention decision it makes.

**Note:** this brief was raised during the draft 2 review. The reviewer explicitly declined to propose answers, because these are jurisdiction-specific and terms-specific legal judgments where a confident-sounding guess is worse than an open question.

---

## Investigation E - Hiring-platform census for this vertical

**Best owner:** whoever runs M2. This is a half-day data task, not a research project.

**Start condition:** M2 detection has run across the pilot employers.

**Unblocks:** the M4 adapter build list.

**Cost of deferring:** M4 risks spending its adapter budget on platforms that return no pilot postings.

**Question:** Which hiring platforms do restaurant employers in the pilot area actually use?

**Work:**
1. From M2's detection results, produce a frequency table of every hiring platform encountered, including the categories "no platform, static page" and "Indeed-hosted".
2. Set a minimum occurrence count for building an adapter, and choose the M4 build list from the table.

**Background:** the engineering plan names Greenhouse and Lever. Both public endpoints are live and unauthenticated, so the adapters are buildable, but both serve corporate and knowledge-work hiring. Restaurants more commonly hire through hospitality-specific tools such as Workstream, Harri, 7shifts, Toast, HigherMe, and Snagajob, or through Indeed-hosted applications, which this project does not automate. That is a market observation rather than a measurement, which is exactly why this census exists: M2 visits every one of these sites anyway, so the answer costs nothing extra.

**Deliverable:** the frequency table plus a one-paragraph adapter decision.

**Acceptance:** every adapter in the M4 plan traces to a row in the table.

---

## Investigation F - Claim-check feasibility without a model

**Best owner:** NLP or applied scientist with information-extraction experience.

**Start condition:** open now, before M5 acceptance criteria are finalized.

**Unblocks:** the M5 claim-check acceptance criteria and the scope of the style linter.

**Cost of deferring:** M5 ships with an acceptance criterion nobody has verified is reachable, which tends to be resolved by quietly weakening it during the milestone.

**Question:** What fraction of the objective factual claims in real application materials can a rule-based detector actually catch, with no model available?

**Work:**
1. Collect 10 to 20 genuine cover letters and resumes for these roles.
2. Hand-annotate every objective factual claim in them.
3. Measure what fraction a rule and gazetteer based detector catches: dates, durations, numbers, employer names, job titles, certifications.
4. Report recall per claim type, not pooled.

**Deliverable:** the concrete list of claim types the first build will verify, the list it explicitly will not verify, and the attestation flow covering the gap.

**Acceptance:** the M5 criterion states a measured coverage figure per claim type rather than an unfalsifiable claim about all assertions.

**Note:** draft 2 required that every objective assertion in every document, including applicant-edited ones, trace to confirmed provenance. Extracting every objective assertion from free-form prose is open-ended work, and the first build uses no model, so the requirement as written could not be met or even tested. Draft 3 narrows it to structural provenance for generated text plus attestation for edits. This investigation supplies the numbers that fix the remaining boundary.

---

## Investigation G - Effort instrumentation and its statistics

**Best owner:** the project owner, with light analytics help if wanted.

**Start condition:** open now. Small.

**Unblocks:** the M6 applicant-effort acceptance criteria.

**Cost of deferring:** the effort criterion cannot be evaluated, because nothing defines where the clock starts and stops.

**Question:** How is applicant effort measured, and which statistics are meaningful at pilot sample sizes?

**Work:**
1. Confirm the clock start and stop for pipeline time and for third-party form time.
2. Set the idle timeout after which a session counts as abandoned and is excluded rather than counted. Draft 3 proposes 15 minutes.
3. Confirm which time scope counts against the run budget by default.
4. Confirm the reported statistics. Draft 3 reports n, median, min, and max, and drops p90, because the 90th percentile of at most 20 applications is the second-largest value and moves with a single bad portal.

**Deliverable:** the instrumentation spec, folded into the M6 criteria.

**Acceptance:** an M6 run produces an effort report that can be read without knowing how it was measured.
