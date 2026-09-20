# How to use the 100 minutes

The goal is to produce a memo that a colleague could challenge, update, and act on. A sophisticated hypothesis is only useful if you can connect it to observations and a feasible next step.

## A workable clock

| Minutes | Output |
|---|---|
| 0-20 | Read the case and template. Record the decision, constraints, evidence IDs, and your two biggest uncertainties. |
| 20-30 | Put a provisional answer under every required heading. Write the recommendation before polishing it. |
| 30-50 | Compare hypotheses. Identify which observations distinguish them and which fit almost anything. |
| 50-75 | Specify the top investigations, their costs, predicted outcomes, and decision consequences. |
| 75-90 | Finish the decision rule, assumptions, strongest objection, and short decision-maker message. |
| 90-100 | Check completeness, numerical consistency, source references, and contradictions. Cut repetitions. |

For case 04, interrupt this schedule at minute 55 to read its update. Preserve your initial judgment and show what changed.

Write approximately 1,000-1,500 words for a full case. This is a suggested practice target. A clear 900-word answer covering every requested part can be better than 1,800 words with an incomplete plan.

## A scratchpad that earns its space

Use four columns while reading: **observation / possible explanation / missing fact / consequence for the decision**. For example:

| Observation | Possible explanation | Missing fact | Decision consequence |
|---|---|---|---|
| Failures are less common in evaluation-labelled runs | The label changes behavior, or that runner uses a different tool configuration | Matched runs changing only the label | Determines whether evaluation results transfer to the proposed deployment |

Do not turn the scratchpad into the final answer unchanged. The final answer should make priorities visible.

## Useful distinctions

- **Observation versus interpretation:** a tool call omitted a record; a hypothesis is that the model was trying to conceal the call. The latter needs extra support.
- **Ability versus willingness versus opportunity:** failure to perform an action might reflect inability, refusal, missing access, or a bad test. Specify which claim your evidence addresses.
- **Failure rate versus detection rate:** an alert count depends on actual behavior, what the detector can see, and what it flags.
- **Absence of evidence versus evidence of absence:** a clean run is more reassuring when the test was capable of exposing the failure you care about.
- **Mechanism versus decision:** you may have enough evidence to disable a risky permission before knowing why the behavior occurred. You may also have enough containment to permit useful work while mechanism research continues.
- **Belief versus preference:** "I think the failure is rare" and "I would accept that risk" are different claims. Explain both when they drive the choice.

These are practical distinctions for these exercises, not a syllabus for the actual test.

## What a useful hypothesis looks like

Instead of "the model is deceptive," define an observable pattern: "The model suppresses records of unauthorized actions more often when it receives a credible cue that nobody will review them, holding permissions and task instructions fixed."

Then state a competing explanation and a discriminator. A label effect alone would support context sensitivity; it would not, by itself, prove a persistent hidden objective. The hypotheses in a case may overlap. You need not invent probabilities adding to 100% for overlapping possibilities.

Keep three or four live explanations. Rank them provisionally. Explain the leading explanation's weakest point. A list of ten unranked possibilities is not prioritization.

## What a useful investigation looks like

Name the question, intervention, comparison, measured outcome, cost, likely interpretations, and resulting action. For example:

> Run both checkpoints with the same tools and time budget on fresh, independently scored tasks. If the newer checkpoint still improves across several task families, the gain is less likely to be entirely an evaluation artifact; if the gain disappears, revise the model-improvement claim. Neither result alone establishes readiness for external autonomous operation.

Avoid "do more red-teaming" without a target, or "conduct interpretability research" without an outcome that could affect the pending choice. Useful information is information that could change what you do, and its value depends on cost and deadline.

## Expressing uncertainty usefully

Use confidence language tied to a claim and a reason: "I have high confidence that the comparison is confounded because the retry budget changed; I have low confidence about how much of the apparent gain this explains."

Numbers are optional. If you use a subjective probability, name the event and time horizon and label it as judgment. Do not turn 6 failures in a selected sample of 30 into a 20% chance that a broad theory is true. Exact arithmetic and precise beliefs are different things.

Write one specific observation that would move your view in each direction. "More evidence" is insufficient. Explain which parts of your recommendation survive uncertainty about the leading explanation.

## Reviewing an attempt

1. Stop writing when time ends and save the attempt unchanged.
2. Use `SELF_REVIEW.md` before opening the key. Mark unsupported assertions and any proposed work that exceeds the budget.
3. Read the worked answer, then its debrief. Find one thing your answer handled better and two omissions with high decision value.
4. Rewrite only your opening recommendation and highest-priority experiment. Do not spend an hour polishing the whole answer.
5. Record the one habit to change next time: for example, "state the unit of sampling" or "give a condition that would permit proceeding."

For your final rehearsal, use only the case, glossary, and blank template. The actual test's own instructions and template take precedence over this practice structure.
