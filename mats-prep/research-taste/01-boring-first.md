# The boring-explanations checklist

Run this *before* you write a word about model psychology. It takes three
minutes from memory and it is the thing that most separates strong answers from
plausible-sounding ones. In real pre-deployment work the large majority of
startling eval results are one of these.

The point is not to conclude "it's a bug." The point is to be able to write
*"I considered and can rule out / cannot yet rule out X, and here is the cheap
test"* — which is a different and much stronger move than either believing the
alarming story or dismissing it.

## A. Is the comparison even a comparison?

1. **Harness / scaffold version.** Retry policy, tool-error handling, timeouts,
   step limits, parallelism. A retry cap change silently converts transient tool
   failures into task failures.
2. **Prompt template / system prompt.** Whitespace, ordering, few-shot count, the
   presence of a safety preamble, a developer message the eval adds.
3. **Sampling parameters.** Temperature, top-p, `max_tokens`, thinking/reasoning
   budget. A lowered token cap truncates long agentic tasks and scores them zero.
4. **Checkpoint identity.** Which snapshot? Pre- or post- the late fine-tune?
   Quantised? Served from which endpoint?
5. **Tool availability.** Was the browser up? Rate limits? Did the sandbox have
   network? Was a tool silently erroring?

## B. Is the measurement measuring what you think?

6. **Grader difference.** Model grader vs human grader, grader version, grader
   prompt, grader model's own capability. Lenient partial credit moves scores
   10+ points with no change in the model.
7. **Answer extraction.** A regex or parser that fails on a changed output format
   produces a clean, confident, completely wrong score drop. Absurdly common.
8. **Refusals, abstentions and timeouts scored as failures.** Recompute over
   attempted items. Decide whether the metric is supposed to measure capability
   (then refusals are noise that biases *downward*) or propensity (then they're
   the signal).
9. **Truncation.** Did responses hit the token cap? Check length distributions,
   not just scores.
10. **Item set difference.** A "rewrite" or "translation" or "held-out variant"
    may be easier or harder, not merely differently worded. Look for a control
    arm: an older model's score on both variants is a free ruler.
11. **Contamination.** Public eval in pretraining data inflates scores. Check the
    *direction*: contamination rarely explains a score going *down*, so if the
    anomaly is a drop, contamination is usually the wrong story.
12. **Scoring-rule change.** Partial credit, pass@k vs pass@1, per-item weights.

## C. Is it noise, or selection?

13. **Sample size and seeds.** `SE ≈ sqrt(p(1-p)/n)`. At p≈0.5, n=120 → SE≈4.6,
    so ±9 at 95%. Single-seed agentic results are especially noisy.
14. **Multiple comparisons.** If the dashboard has 40 metrics, some will look
    alarming. Ask how many were looked at before this one was flagged.
15. **Selection in how the examples reached you.** Were those two transcripts
    sampled at random, or found by someone searching for them? A cherry-picked
    transcript has a base rate of one. This does not make it unimportant — a
    single proof-of-existence matters for severity — but it tells you nothing
    about frequency, and you should say so explicitly.
16. **Bookkeeping.** Wrong date, wrong row, stale dashboard cache, someone
    pasted the wrong column.

## D. Is it people?

17. **Annotator disagreement / drift.** Inter-rater reliability, a new contractor
    cohort, a changed rubric.
18. **Who is telling you and what do they know.** A contractor who found something
    "by accident" with n=40 and one seed is a lead, not a result. An infra engineer's
    Slack aside about version numbers is often the most load-bearing sentence in
    the whole packet.
19. **Incentives in the room.** A launch commitment, a team that owns the metric,
    someone who will look bad. Note these as facts about the evidence-generating
    process, not as accusations.

## The direction test

For every candidate explanation, ask: **does it predict the sign of the effect?**
This one question kills most wrong hypotheses in seconds. Contamination predicts
scores going up. A truncated token budget predicts long-task scores going down.
A lenient grader predicts the *leniently graded* arm being higher. If your
favourite hypothesis doesn't predict the direction you observe, it is not your
explanation, however fashionable it is.

## The cheapest-decisive-test habit

For each surviving hypothesis write the single cheapest observation that would
distinguish it from its nearest rival, and its cost. Then sort by
`(how much it would change the decision) / (cost)`. This is value of
information, and using it explicitly — including to *reject* an expensive test
whose result couldn't change the decision — is one of the clearest signals of
research taste you can put on a page.

A test that cannot change any decision is not worth running even if it is
interesting. Say that out loud in your answer about at least one thing.
