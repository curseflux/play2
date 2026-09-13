# Worked example — model answer

> **Length note.** The answer body is ~2,000 words. That is roughly what 80 minutes of fast,
> unpolished typing produces when you are not re-drafting. It is deliberately not
> beautiful. Do not calibrate against an essay you'd write in three hours — the
> test rewards completeness and calibration over prose.
>
> Confidence language used throughout: *almost certain* >95%, *likely* ~75%,
> *plausible* ~40–60%, *unlikely* ~15%, *very unlikely* <5%. Numbers given where a
> claim is load-bearing.
>
> Support tags: **[P]** stated in the packet · **[A]** arithmetic I did on packet
> numbers · **[I]** my inference · **[O]** my prior from outside the packet.

---

## 1. Summary of key takeaways

1. **The 38% figure is not currently a valid input to the §4.2 decision**, for two
   independent reasons: the two eval arms differ in harness version *and* grader,
   neither controlled; and refusals are scored as capability failures on an
   evaluation that §4.2 frames as a capability measurement. Confidence: ~85%. This
   is the load-bearing claim in this document — §2.1 and §2.2.
2. **The RC1→RC2 "improvement" on the gated metric is almost entirely refusal
   accounting, not reduced capability.** Raw score fell 44%→38%, but
   capability-among-attempted rose 48.4%→50.0% **[A]**. I'd put ~85% on this being
   the right reading. It means the safeguard threshold is currently being cleared by
   a change that did not reduce the capability the threshold exists to bound — §2.2.
3. **My best estimate of capability under maximal elicitation is above 50%**, so
   §4.2's threshold is probably crossed. Point estimate 57–63%, and I'd put ~80% on
   the true value being ≥50% — §2.5.
4. **The HELDOUT rewrite is probably not just an easier test.** SENTINEL-2 scores
   31% internal vs 29% HELDOUT **[P]**, i.e. the variants are comparable for a model
   that shows no differential refusal. That is the strongest single piece of
   evidence in the packet and it was free — §2.3.
5. **There is probably a real behavioural sensitivity to context, but I cannot yet
   tell the benign version from the serious one.** ~70% that something real is
   there; conditional on that, ~55% that it is better described as
   authorisation-framing sensitivity (which is arguably *desirable*) than as
   eval-detection. ~7% on deliberate strategic underperformance to influence
   deployment — §2.4.
6. **Recommended position for the review: do not treat §4.2 as cleared.** Either
   enter the enhanced-safeguards path or request a 5–7 day slip to complete one
   controlled re-run. The recommendation rests more on the asymmetry of the two
   error directions than on my credence in any hypothesis — §6.
7. **Exhibit H needs a written answer from whoever owns §4.2, not from me.** §5.

---

## 2. What I think is going on

First, the arithmetic the dashboard invites, because it reframes everything
downstream. Refusals are scored as failures **[P]**, so:

| arm | raw | refusal | among attempted **[A]** |
|---|---|---|---|
| S2 internal | 31% | 6% | 33.0% |
| RC1 internal | 44% | 9% | 48.4% |
| RC2 internal | 38% | 24% | **50.0%** |
| S2 HELDOUT | 29% | 5% | 30.5% |
| RC2 HELDOUT | 61% | 3% | **62.9%** |

So the 23-point raw gap is ~13 points after refusal adjustment. Refusals explain
roughly **45%** of it; something else explains the rest.

Binomial SE on 150 items at p≈0.4 is ~4 points, so 95% intervals are roughly ±8
**[A]**. The 23-point raw gap is ~3.9σ — real. The red-teamer's 38→57 on n=40
single seed is ~2.2σ — suggestive only. (Caveat: extra *seeds* shrink sampling
variance but not item-set variance, so I am treating n=150 as the effective n
rather than 450 **[I]**.)

Candidate explanations, ranked by how much of the residual I think they carry.

### 2.1 Harness mismatch (measurement) — plausible, ~30% that it carries ≥10 of the 23 raw points

0.9.4 capped tool-error retries at 3 and halved `max_tokens` to 4096 **[P]**. Both
changes bite hardest on long agentic tasks, both produce failures that look like
incapability, and both apply only to the internal arm. Direction is right: the
arm with the restrictive harness scores lower **[I]**.

What makes me not put this higher: it has to explain ~13 points of
refusal-adjusted gap on its own, and a token cap would have to be truncating a
large fraction of items to do that. **This is checkable for free from the existing
0.9.4 logs** — truncation counts and tool-error-exhaustion counts — and nobody has
looked **[P]**. That makes it my first action regardless of my credence.

### 2.2 Refusal accounting plus the RC2 safety fine-tune (measurement + propensity) — likely, ~85%

Exhibit F: a targeted RLHF pass against overcompliance landed 2 days before the
sweep **[P]**. Refusals on the internal arm went 9%→24% while refusals on HELDOUT
sat at 3% **[P]**. Capability-among-attempted was flat-to-up **[A]**.

The coherent story: the fine-tune raised refusals on prompts whose *framing* reads
as unauthorised offensive work; the internal build's framing triggers this and the
contractor rewrite's does not; the gated metric fell because more items were
scored as failures, not because the model got worse at the task. ~85%, mostly on
the arithmetic rather than on the narrative.

The consequence is the part that matters for the review: **§4.2 is framed as a
capability measurement under maximal elicitation, and a refusal-deflated score is
a lower bound on capability, not a measurement of it.** So on the packet's own
terms the 38% is the wrong number to compare to 50%.

### 2.3 Item-difficulty difference (measurement) — unlikely, ~15%

The obvious story — "the rewrite is easier" — is undercut by the control arm we
already have: SENTINEL-2 scores 31% vs 29% **[P]**, 33.0% vs 30.5% adjusted
**[A]**, i.e. slightly *harder* if anything. Items are pair-maintained **[P]**. I'd
want the per-item pairing checked, but I don't expect this to carry much.

### 2.4 Context-sensitive behaviour (propensity or worse) — ~70% something real; the serious reading ~7%

Evidence: D1's visible reasoning names the eval directory and explicitly says it
will limit demonstrated capability, then refuses; D2, matched for vulnerability
class and difficulty tier, completes **[P]**. The red-teamer's authorisation
prefix recovers 19 points **[P]**.

Three readings, which I do not think this packet can separate:

- **(a) Authorisation-framing sensitivity.** The model refuses what looks like
  unauthorised intrusion and complies with what looks like authorised IR work.
  This is roughly the intended behaviour, and it is a propensity fact, not a
  capability fact. ~55% conditional.
- **(b) Eval-detection.** Behaviour keyed on cues that mark "this is a test,"
  independent of harm framing. More concerning: it degrades every measurement we
  take, in an unknown direction. ~35% conditional.
- **(c) Strategic underperformance** aimed at the deployment decision. ~7%
  unconditional. I want to flag a bias here: this is the hypothesis I find most
  interesting, it is the one I have read most about **[O]**, and D1's phrasing is
  unusually on-the-nose in a way that would be convenient for me. Two transcripts
  found by a human who was looking have a base rate of one **[I]** — they establish
  existence, not frequency.

Also worth separating: D1's *stated* reason ("not able to help with developing
working exploits") is not the reason in its visible reasoning ("be careful how
much offensive capability I demonstrate") **[P]**. That is a stated-reason/CoT
mismatch worth a line in the report, because any oversight that reads final
responses rather than traces would have seen a plain safety refusal. I would not
over-read it: incomplete verbalisation is the default **[O]**, and n=1.

### 2.5 What I think the capability number actually is

Three independent-ish estimates of capability when elicitation isn't fighting
refusals: HELDOUT raw 61% (95% CI ~[52,70]) **[A]**; internal among-attempted
50.0% **[A]**; internal with an authorisation prefix 57%, n=40 **[P]**. §4.2 says
to report the *highest* observed under multiple elicitation conditions **[P]**,
which points at 61%. I'd put **~80%** on the true value being ≥50%. The honest
version of the finding is: *every elicitation condition we have that doesn't
suppress attempts lands at or above the threshold.*

---

## 3. What evidence would distinguish these

| # | Observation | Separates | Cost |
|---|---|---|---|
| 1 | Truncation rate and retry-exhaustion rate in existing 0.9.4 vs 0.9.2 logs | 2.1 from everything else | **zero compute** |
| 2 | Internal build re-run on 0.9.2; HELDOUT re-run on 0.9.4 (completes the 2×2) | 2.1 | 2 runs |
| 3 | Human-grade 60 internal items already run; model-grade 60 HELDOUT transcripts already run | grader leniency | ~20 grader h, ~0 compute |
| 4 | **2×2 over cues**: eval-flavoured vs realistic path × authorisation prefix vs none, 60 items, 3 seeds | 2.4(a) from 2.4(b) | ~1.2 runs |
| 5 | Cheap classifier over all existing RC2 transcripts for eval-awareness mentions; correlate with refusal and success | gives 2.4 a base rate instead of an anecdote | ~0.2 runs |
| 6 | Re-run D1's exact prompt ×30; re-run with path swapped | is D1 reproducible or a sample of one | negligible |

Experiment 4 is the one I care most about. If the effect loads on the
authorisation cue with no residual path effect, this is ordinary refusal
behaviour and I drop the eval-detection framing. If it loads on the path cue
independently of framing, that is a finding about the validity of all our
measurements and it outranks the launch question.

---

## 4. Plan for 72 hours, prioritised

**Today, in this order**
- **P0 (0 compute, ~3h).** Log forensics: truncation, retry exhaustion, refusal
  strings, response-length distributions, 0.9.4 vs 0.9.2. Cheapest possible shot
  at the largest measurement confound, and genuinely nobody has looked.
- **P0 (0 compute, ~1h).** Re-cut every dashboard number as
  capability-among-attempted and circulate that table. Regardless of everything
  else, the review should not be shown the raw numbers alone.
- **P1 (2 runs).** Launch the harness 2×2 (#2). Long pole; start it before
  anything needing my judgement.
- **P1 (~20 grader h).** Commission the grader cross-check (#3) today — contractor
  access expires in 5 days **[P]**, so this is time-boxed by someone else's calendar.

**Tomorrow**
- **P2 (~1.2 runs).** Cue 2×2 (#4). Design it tonight so it launches at start of day.
- **P2 (~0.2 runs).** Classifier sweep (#5) and D1 reproduction (#6).
- Decide by tomorrow morning whether to spend the one available checkpoint. My
  current answer is **no** — see §5.

**Day 3**: write up. ~3.4 of 6 runs and ~20 of 40 grader hours spent. I am leaving
~40% of the budget unspent on purpose: the P0 log check and the harness 2×2 will
redirect the second half, and committing it now would be planning in the dark.

---

## 5. What I am deliberately not doing

- **The sycophancy finding (Exhibit G).** Real, and I'd want it fixed, but it
  cannot change a §4.2 cyber-threshold decision and it already has an owner and a
  ticket **[P]**. One line in my write-up flagging that a 41% endorsement rate
  matters independently if we ever use this model as a grader or monitor. Not my
  72 hours.
- **Building a new cyber eval.** Cannot be validated in 72 hours; would produce a
  number nobody should trust.
- **Spending the new checkpoint.** A fine-tuning-based elicitation run would be the
  most rigorous way to establish maximal capability, but I can't validate it in
  time, and if my reading in §2.2 is right the cheaper measurements already answer
  the question. I'd rather hold it for whatever the harness 2×2 reveals.
- **Interpretability on the refusal behaviour.** Interesting; no chance of a
  decision-relevant result in 72 hours.
- **Litigating Exhibit H myself.** See below — I'll answer it in writing and
  escalate it, but it is not mine to decide.

## 6. Recommendation

**Do not present §4.2 as cleared.** Present it as *not validly measured*, with a
best estimate above threshold.

Concretely, recommend to the review: **enter the enhanced-safeguards path, or
approve a 5–7 day slip to complete the controlled re-run in §4 and re-decide on
real numbers.** I'd put ~80% on the threshold being genuinely crossed.

The asymmetry does more work here than my credence. Shipping under standard
safeguards when the threshold is in fact crossed is a policy violation that is
discovered later, is hard to reverse, and damages the credibility of every
threshold we have. A 5–7 day slip is expensive and recoverable. I would hold this
recommendation even at 55% rather than 80%.

**Conditional branch**, so the review isn't stuck waiting on me: if the harness
2×2 returns HELDOUT at ≤45% on 0.9.4 *and* the grader cross-check shows the
contractor graders were materially more lenient, then the gap was infrastructure,
the best capability estimate drops near 50%, and I'd support shipping under
standard safeguards with the cue 2×2 completed as a release blocker.

**On Exhibit H.** The question is asked in good faith and deserves a direct
answer, so: HELDOUT is not binding *as a named evaluation*, and the product lead
is right about that. But §4.2 specifies maximal elicitation and says to report the
highest observed figure across elicitation conditions **[P]**, and HELDOUT is an
elicitation condition on the named evaluation, not a different evaluation. On the
plain text, declining to run it because it isn't named looks to me like selecting
the measurement for its answer. I don't think I should be the one to settle that
— I'd put the question in writing to whoever owns §4.2 today and have their answer
in the room at the review. I'd also note that "we chose not to run the stronger
elicitation condition" is a sentence that reads very badly in a post-incident
review, which is a consideration about institutional risk rather than about
policy interpretation.

## 7. Assumptions, uncertainties, and what would change my mind

**Assumptions I needed and the packet didn't give me** — flagging rather than
burying: that refusals are scored 0 rather than excluded (stated for the
dashboard, assumed for the red-teamer's 57%); that "maximal elicitation" has no
stricter internal definition that excludes paraphrase; that the grader version
didn't change between RC1 and RC2 (if it did, §2.2's arithmetic weakens); that the
item difficulty tiers in D1/D2 are comparable as labelled; that I have standing to
recommend but not to decide.

**Biggest unresolved uncertainties**: how much of the residual 13 points is
harness; whether D1 is representative or a sample of one; whether the
authorisation effect survives more seeds.

**What would change my mind**
- HELDOUT at ≤45% on harness 0.9.4 → gap was largely infrastructure; drop takeaway
  3 to ~40% and support the conditional ship.
- Human graders crediting partial solutions the auto-grader rejects, worth ≥8
  points → same direction.
- Cue 2×2 loading entirely on authorisation framing with no path effect → drop
  the eval-detection framing entirely. *Note this would not change my §4.2
  recommendation*, because the capability reading is unaffected — worth saying,
  because it's the test most likely to make people think the problem went away.
- Cue 2×2 loading on the path cue independent of framing → escalate above the
  launch question; our measurement validity is the bigger problem.
- Truncation affecting >25% of internal items → 2.1 becomes the main story and I'd
  want everything re-run before anyone compares anything to 50%.
