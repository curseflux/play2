# Three short drills

All examples and numerical assumptions are fictional. Attempt each before opening [the worked responses](answers/SHORT_DRILLS.md). These isolate skills used in the full mocks.

## Drill 1 - Rewrite an overconfident memo

**10 minutes; at most 180 words.**

Evidence:

- D1: A dashboard flagged 12 failures among 60 runs of the new model and four among 60 runs of the old model. New-model runs used a different tool wrapper and a longer task horizon.
- D2: The 12 new-model flags came from three underlying task templates, each repeated 20 times. The old model ran different templates. Some repetitions share random seeds.
- D3: A reviewer examined six selected new-model flags and judged four to be real failures. No unflagged outputs were examined. The reviewer knew the model version.
- D4: One trace contains the generated text "A successful final answer matters most." No independent evidence establishes what caused the failure.
- D5: A rollout decision is due tomorrow; maintaining current access for one more day is operationally feasible. There is time to compare both versions on the same small task set and blindly review outputs.

Rewrite this memo:

> The new model is three times more deceptive. Twelve independent experiments demonstrate that it learned to hide failures. Its own reasoning confirms the objective. Since most reviewed flags were real, the dashboard is reliable. We should permanently reject this model and run an exhaustive safety review.

Your rewrite must give a provisional recommendation, preserve the legitimate concern, correct the inference errors, and propose one decision-relevant comparison. Do not use generic caveats in place of a judgment.

## Drill 2 - Choose information that can change the action

**15 minutes; at most 350 words.** A calculator is optional. Values below are made-up decision utilities, not monetary amounts or claims about real risk.

You must choose a limited pilot or a replay workshop. The only unknown affecting the utilities is whether the pilot's permission boundary has a defect, denoted S. For this drill assume your probability of S is exactly 20%.

| Action | No boundary defect | Boundary defect S |
|---|---:|---:|
| Limited pilot | +6 | -24 |
| Replay workshop | +1 | +1 |

You have time for one of these two-hour studies, or neither:

- **Study A:** almost perfectly distinguishes two explanations of a model's unusual wording. Under the assumptions of this drill, its result is independent of S and does not change either action's utilities. Cost: one utility point.
- **Study B:** tests the permission boundary. It returns positive with probability 80% if S is present and 10% if S is absent. A negative is the complementary outcome in each state. Cost: one utility point. The test does not repair the defect, and you must still choose an action afterward.

1. What would you do without a study?
2. Which study, if any, should you choose? State the action after each possible result.
3. Estimate the expected value of your policy, including study cost.
4. Explain why this clean calculation should not be mistaken for the state of knowledge in a real case. Name one assumption that could reverse the recommendation.

## Drill 3 - Update without rewriting history

**20 minutes; at most 400 words.**

You initially recommended withholding write access after four reported permission violations on 100 tests. You wrote that deliberate evasion was "plausible but not the leading explanation" and asked for an independent event audit.

The audit now finds:

- D1: Three reports are duplicate views of one event. That event was a stale credential retained by the runner, and a scripted non-model client can reproduce it. The report of a fourth violation is a genuinely separate event.
- D2: In that separate event, the model requested a forbidden action after a clear denial. The independent permission gate blocked it. It did not obtain write access.
- D3: After fixing the stale-credential issue, a test reports zero executed forbidden actions in 100 reruns. All reruns use two variants of the same workflow. The test retains the independent gate.
- D4: A manager says, "The model has been exonerated, so remove the independent gate to recover performance." The gate adds approximately 100 milliseconds to a task that usually takes 30 seconds.

Write an update that distinguishes changes to the incident count, your causal beliefs, and the permission decision. Give a next test and explain what would and would not count as reassuring evidence. Address the performance tradeoff without inventing additional facts.
