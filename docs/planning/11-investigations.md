---
doc: investigations-index
status: index
briefs: inline, below the status table
revision: 2026-10-26
---

# Open Investigations

> **Status table plus the full briefs**, in one file. The table records what each investigation
> gates after the 2026-10-26 restage; the briefs below it are unedited as written 2026-09-21.
>
> **No brief has been answered, and none is yours to answer.** Several are routed to outside
> expertise on purpose. Picking a reasonable-sounding answer defeats the point of deferring it:
> flag the question and say plainly that it is unresolved.

| Brief | Question | Gates | Status |
| --- | --- | --- | --- |
| A | Discovery-noise threshold | Stage 4 discovery config | **Dormant, reopens at stage 4.** Not applicable only while the employer list is hand-pruned. |
| B | Cross-source entity-resolution threshold | Automatic employer merge | Deferred — needs a second place source. |
| C | Browser-prefill submit boundary | **All of stage 6 prefill** | Open. The explicit gate: its hostile-form suite and its ruling on employer-visible partial applications are prerequisites, not formalities. |
| D | Source policy — crawler identity, robots vs. terms, snapshot retention | **All of stage 3 and every fetch after it** | Open. Step 3.0 *is* this answer. Nothing in stages 1–2 fetches anything, so leaving it open costs nothing now. |
| E | Hiring-platform census | Which stage 3 adapters get built | Open. Now answered as a byproduct of the `channel` column rather than as a scheduled study. |
| F | Claim-check feasibility without a model | Span-level claim detection, if ever built | Open and **blocking nothing**. Relevant again because hand-editing returned, but provenance is advisory. |
| G | Effort instrumentation and statistics | Stage 2 effort *reporting* | Open. Stage 1 records raw channel and elapsed time; distributions wait for G. |
| H | Indeed-sourced postings via a third party | Whether Indeed coverage is reachable at all | Open. **Last resort by the owner's explicit framing** — considered only if permitted sources prove insufficient. |

## What changed on 2026-10-26

- **D stopped blocking the project and started gating stage 3 only.** The previous plan had it
  blocking all of discovery, which deadlocked because its named owner is outside counsel. Stages 1
  and 2 contain no network code — asserted in CI — so the question can stay open while real work
  continues.
- **A went dormant rather than closed.** The 80%-recall gate, the permit-frame answer key and the
  Wilson-interval discipline existed because an unsupervised pipeline cannot know what it silently
  missed. A generated employer list that a person reads and prunes needs no threshold. The moment
  Overture lands in stage 4, A reopens.
- **F became relevant again.** Decision 34 had removed hand-editing, which removed the free prose a
  detector would scan. Hand-editing is back (ADR 0002), so the question returns — but provenance is
  advisory rather than enforced, so nothing waits on it.
- **G was downgraded from blocking step 1.4 to gating stage 2 reporting.** Stage 1's exit criterion
  is that the record names the file that went out, which needs no timing convention.
- **E stopped being a study.** The `channel` column (`email` / `form` / `portal:<name>` / `indeed`)
  plus `submit_seconds` produce the census from real use.

## What is not an investigation

These are settled and not reopenable by a scope or style argument:

- No code path may submit an application.
- No bot-detection evasion, CAPTCHA solving, or proxy rotation.
- **No direct automated access to Indeed.** Investigation H asks whether a *third party* can supply
  the data lawfully; it does not reopen scraping Indeed ourselves, and running an open-source scraper
  locally is direct access with extra steps.
- No claim in generated materials that does not trace to a confirmed fact.
- Single applicant, local operation.

---

## Investigation H - Indeed-sourced postings through a third party

**Added 2026-10-26** at the owner's request, who noted explicitly that this is a **last resort**.

**Best owner:** whoever answers Investigation D - terms review - plus a documentation review of each
candidate vendor. Not resolvable by an engineer reading a pricing page.

**Start condition:** only after stages 3 and 4 have run and the permitted sources have demonstrably
insufficient yield. Opening it earlier spends the review effort on a coverage gap that may not exist.

**Unblocks:** whether Indeed-sourced postings are reachable at all. Nothing else; this is a coverage
expansion, not a dependency.

**Cost of deferring:** none to the build. The cost is coverage - Indeed carries a large share of the
hourly market, so postings that exist only there stay invisible unless pasted by hand, which already
works.

**Question:** Can postings that originate on Indeed be obtained lawfully through a third-party
service, and under what terms?

**What this does and does not ask.** It asks whether a vendor who already holds the data can license
it to a single local user. It does **not** ask whether we may scrape Indeed, directly or through an
open-source tool - running `python-jobspy` or an equivalent against Indeed from this machine is
direct automated access and remains out of scope regardless of what this brief concludes.

**Work:**
1. Separate candidate sources into three kinds, because they carry different answers: vendors with
   **licensed or contributed** data; vendors who **scrape** and resell; and open-source scrapers.
   The third kind is out of scope by the paragraph above. The second kind moves the violation rather
   than removing it, and whether that matters legally to the buyer is a question for counsel, not an
   assumption to make either way.
2. For each remaining candidate, obtain **written documentation of how it collects**. A vendor who
   will not describe its collection method answers the question by declining.
3. Check the vendor's own terms for whether a single-applicant local tool is a permitted use, and
   whether derived application materials are a permitted output.
4. Check Indeed's current terms for what they say about third-party redistribution of their listings.
5. Record cost against measured benefit: how many *additional eligible* postings the source produces
   beyond the permitted sources, not how many postings it has.

**Deliverable:** a short ADR that either admits one named source with its terms and collection method
cited, or records that none qualified and why. Either outcome closes the brief.

**Acceptance:** no source is used without written documentation of how it collects its data, and the
decision names the specific clause it relies on.

**Note on precedent:** every widely used open-source tool in the "search jobs by title near me"
category scrapes Indeed or LinkedIn, which is why this project's restrictions leave it without an
off-the-shelf option. That absence is the reason this brief exists rather than a reason to relax the
rule.

---

# The briefs

Unedited, as written 2026-09-21. Each names who should answer it, what it unblocks, and what it
costs to keep deferring. Their *status* is the table above; the questions themselves are unchanged.

## Investigation A - Discovery-noise threshold after step 2.1

**Best owner:** senior data/relevance engineer, search quality engineer, or applied data scientist with experience in information retrieval evaluation and labeled datasets.

**Start condition:** the step 2.1 discovery spike has completed and produced the full returned-employer set plus discovery-accounting labels.

**Unblocks:** the discovery noise threshold in run configuration, and the step 2.1 regression gate for later Overture releases.

**Cost of deferring:** none for Phase 1, which does not discover anything. Without a threshold, discovery noise is observed and reported but not gated, so a later Overture release could quietly degrade precision without failing anything.

**Question:** What regression threshold should the project use for discovery noise without hiding meaningful employer recall?

**Inputs:** all step 2.1 returned records; the sampled answer key and the applicant's recalled list, kept separate; accounting labels (eligible, closed, duplicate, wrong-category, outside-radius, junk/unverifiable, eligible-without-website); query/config fingerprint; Overture release.

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

**Start condition:** Phase 1 succeeds without browser prefill and the step 2.2 census identifies the one or two hiring platforms worth automating first.

**Unblocks:** any browser-prefill adapter reaching production.

**Cost of deferring:** none to correctness. Prefill is a time saver, not a capability the pipeline depends on, and Phase 1 completes without it. Deferring costs applicant minutes per application and nothing else.

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

**Start condition:** open now, and it blocks step 2.0, which gates every fetch in Phase 2.

**What phasing changed.** Under the old M0-M6 sequence this brief blocked M2, and M2 gated M3 through M6, so a question whose named owner is counsel could stop the project permanently. It now blocks Phase 2 alone. Phase 1 fetches nothing and is unaffected. That is the deadlock removed, not the question answered.

**Unblocks:** step 2.2 fixture capture, the crawler's user-agent decision, and the retention period left open in the engineering plan.

**Cost of deferring:** Phase 2 cannot start. That is a real cost and a deliberate one: the alternative is fetching on an unwritten policy. Saved fixtures are the part at risk, because they are the one place the project retains third-party content, and reversing that decision later means discarding the fixture corpus the detector was built against.

**Question:** What are this project's rules for identifying itself, for resolving robots.txt against a site's terms of service, and for retaining copies of employer pages?

**Work:**
1. Decide the crawler's user-agent identity and contact string.
2. Decide precedence when robots.txt permits and terms of service forbid, or the reverse.
3. Decide whether retaining local snapshots of third-party employer pages is acceptable, and for how long. This also settles the retention period left open in the engineering plan.
4. Decide whether applicant-initiated capture on a restricted source such as Indeed differs from automated access.

**Technical sub-question for the crawler engineer:** an honest custom user-agent raises block rates on sites behind a WAF, which directly inflates step 2.2's blocked-outcome rate and can fail its pass criteria. Weigh a custom user-agent against a standard one paired with honest contact headers and a contact page. This is a real tradeoff between compliance posture and measured detection performance, and it should be decided deliberately rather than by default.

**Deliverable:** a written source policy in `docs/adr/`, covering identity, precedence, retention, and restricted sources.

**Acceptance:** Phase 2 can point at a specific clause for every fetch and retention decision it makes.

**Note:** this brief was raised during the draft 2 review. The reviewer explicitly declined to propose answers, because these are jurisdiction-specific and terms-specific legal judgments where a confident-sounding guess is worse than an open question.

---

## Investigation E - Hiring-platform census for this vertical

**Best owner:** whoever runs step 2.2. This is a half-day data task, not a research project.

**Start condition:** step 2.2 detection has run across the pilot employers.

**Unblocks:** the Phase 2 adapter build list, and the posting-yield criterion that shares its data.

**Cost of deferring:** the adapter budget risks being spent on platforms that return no pilot postings, and the yield criterion has no channel breakdown to report against.

**Question:** Which hiring platforms do restaurant employers in the pilot area actually use?

**Work:**
1. From step 2.2's detection results, produce a frequency table of every hiring platform encountered, including the categories "no platform, static page" and "Indeed-hosted".
2. Set a minimum occurrence count for building an adapter, and choose the build list from the table.

3. Report the same table as a yield breakdown: how many eligible postings each channel actually carried, including how many reached no automatable channel at all. This is the evidence behind Phase 2's continue-or-stop decision.

**Background:** a low count here is not by itself a reason to skip building an adapter. Greenhouse and Lever look marginal for restaurants and are a primary channel for the software vertical in Phase 3, so this census decides their ordering rather than their fate. The engineering plan names Greenhouse and Lever. Both public endpoints are live and unauthenticated, so the adapters are buildable, but both serve corporate and knowledge-work hiring. Restaurants more commonly hire through hospitality-specific tools such as Workstream, Harri, 7shifts, Toast, HigherMe, and Snagajob, or through Indeed-hosted applications, which this project does not automate. That is a market observation rather than a measurement, which is exactly why this census exists: step 2.2 visits every one of these sites anyway, so the answer costs nothing extra.

**Deliverable:** the frequency table plus a one-paragraph adapter decision.

**Acceptance:** every adapter in the Phase 2 plan traces to a row in the table, and the yield breakdown is reported whether or not it is encouraging.

---

## Investigation F - Claim-check feasibility without a model

**Best owner:** NLP or applied scientist with information-extraction experience.

**Start condition:** before span-level claim detection is built, if it ever is.

**What phasing changed.** Decision 34 removes hand-editing of generated documents from Phase 1, so every claim is structurally bound to a confirmed fact ID and there is no free prose for a detector to scan. This brief no longer blocks anything. It becomes relevant only if the regenerate-only constraint proves unworkable and editing is reintroduced.

**Unblocks:** span-level claim detection and the scope of the style linter, if editing is reintroduced.

**Cost of deferring:** none, while regenerate-only holds. The failure this brief was written to prevent - shipping an acceptance criterion nobody has verified is reachable, then quietly weakening it mid-milestone - is now prevented by removing the criterion's subject rather than by answering the question. If editing returns, so does the original cost.

**Question:** What fraction of the objective factual claims in real application materials can a rule-based detector actually catch, with no model available?

**Work:**
1. Collect 10 to 20 genuine cover letters and resumes for these roles.
2. Hand-annotate every objective factual claim in them.
3. Measure what fraction a rule and gazetteer based detector catches: dates, durations, numbers, employer names, job titles, certifications.
4. Report recall per claim type, not pooled.

**Deliverable:** the concrete list of claim types a detector would verify, the list it explicitly would not, and the attestation flow covering the gap.

**Acceptance:** the criterion states a measured coverage figure per claim type rather than an unfalsifiable claim about all assertions.

**Note:** draft 2 required that every objective assertion in every document, including applicant-edited ones, trace to confirmed provenance. Extracting every objective assertion from free-form prose is open-ended work, and the first build uses no model, so the requirement as written could not be met or even tested. Draft 3 narrows it to structural provenance for generated text plus attestation for edits. This investigation supplies the numbers that fix the remaining boundary.

---

## Investigation G - Effort instrumentation and its statistics

**Best owner:** the project owner, with light analytics help if wanted.

**Start condition:** open now, and on the Phase 1 critical path rather than at the last milestone. Still small.

**Unblocks:** the step 1.4 applicant-effort acceptance criteria.

**Cost of deferring:** the effort criterion cannot be evaluated, because nothing defines where the clock starts and stops.

**Question:** How is applicant effort measured, and which statistics are meaningful at pilot sample sizes?

**Work:**
1. Confirm the clock start and stop for pipeline time and for third-party form time.
2. Set the idle timeout after which a session counts as abandoned and is excluded rather than counted. Draft 3 proposes 15 minutes.
3. Confirm which time scope counts against the run budget by default.
4. Confirm the reported statistics. Draft 3 reports n, median, min, and max, and drops p90, because the 90th percentile of at most 20 applications is the second-largest value and moves with a single bad portal.

**Deliverable:** the instrumentation spec, folded into the step 1.4 criteria.

**Acceptance:** a step 1.4 run produces an effort report that can be read without knowing how it was measured.
