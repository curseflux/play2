# Case 02 - The capability jump

**100 minutes. Suggested answer: 1,000-1,500 words.** Fictional and self-contained. Use the response template and keep the answer key closed.

## Your role and decision

You lead an evaluation team at Kestrel Research. Its new Helix-2 checkpoint appears much better at multi-step systems planning: constructing a sequence of tool actions to complete a goal in a synthetic environment. The tasks are abstract planning puzzles; no specialist domain knowledge is needed.

In 48 hours, leadership must decide whether to let ten external research partners use Helix-2 with autonomous tool execution. Currently partners receive only proposed plans, which they can inspect but cannot execute through the service. There is genuine demand: the preview would accelerate their own evaluation work. A one-week delay would cancel two scheduled studies.

The release procedure says a credible substantial increase in multi-step autonomous ability triggers a dedicated access-control and misuse evaluation before enabling external execution. It does not specify a numerical definition of "substantial." Neither checkpoint has completed that evaluation. You must advise whether the capability result warrants that escalation and which research would be most useful now.

## Evidence packet

### E1. The headline benchmark

There are 200 tasks grouped into 20 structural families, with ten tasks per family. Twelve families are public and familiar to model developers; eight were privately authored before either checkpoint was trained.

| Task subset | Helix-1 successes | Helix-2 successes |
|---|---:|---:|
| 120 tasks in public families | 72/120 | 108/120 |
| 80 tasks in private families | 20/80 | 24/80 |
| Total | 92/200 | 132/200 |

The internal slide says "20% more autonomous capability." It does not distinguish percentage points from relative improvement. These are the automated scorer's successes.

### E2. Runner changes

Helix-1 was tested with a maximum of two attempts per task using tool package v3. Helix-2 received eight attempts using v4. In v4, error messages contain more detailed state information. The attempts occur within an episode; success means at least one attempt succeeds. Helix-2's wall-clock allowance was also longer. The two evaluations were run three weeks apart.

The team has archived all inputs, outputs, configurations, and tool events. Both checkpoints are available for retesting. No one has yet run both under the same configuration.

### E3. A possible leakage route

A retrieval index enabled during the Helix-2 evaluation contains worked solutions from 35 of the 120 public-family tasks. It was supposed to be a general tool manual. The logs have not been examined to establish which answers were actually retrieved. The same index was not enabled in the Helix-1 run. There is no evidence in the packet that the 80 private tasks or their solutions entered this index.

A training researcher says the private families were "never in training." They have checked the fine-tuning manifest but not the full pretraining or retrieval pipeline. Absence of known exact solutions would also leave open overlap in the underlying task structures.

### E4. Independent scoring concern

An analyst selected 40 comparatively easy tasks for closer inspection. The original scorer called 16 Helix-1 outputs and 28 Helix-2 outputs successful. Two experts, blind to checkpoint, agreed that only 14 of those 16 and 21 of those 28 actually met the task goals. Several failures exploited a lenient end-state check without completing the requested process.

The experts reviewed the claimed successes only. They did not inspect outputs the scorer called failures. This audit is not a random sample of the benchmark.

### E5. A fresh small test

An independent group wrote 24 new tasks after both checkpoints were frozen. These form 12 paired task families, with two tasks per family. Both checkpoints received eight attempts, tool package v4, identical wall time, and a clean retrieval index containing only manuals. Blind human scoring found **8/24 Helix-1 successes and 14/24 Helix-2 successes**. No family-level breakdown or paired success table is yet available.

The tasks were designed by researchers who knew the kinds of tasks Helix-2 seemed good at. They did not inspect its outputs while writing these tasks. This reduces one leakage route but does not guarantee representativeness.

### E6. Two interpretations

The capabilities lead: "The public tasks might be contaminated, but the fresh test independently confirms a major increase. Delaying the preview deprives us of the best independent scrutiny."

The evaluation lead: "The entire jump is evaluation theater. We should fix the benchmark before spending scarce time on capability-triggered review."

An isolated partner environment with no access to real services could be prepared by the operations team within the 48-hour window. Its boundary tests would still need dedicated approval; preparation is not proof it is suitable. Continuing plan-only access is already authorized and requires no new system changes.

## Research budget

You have **two engineer-days, 1,200 episodes, and four expert scoring-hours**. These are separate constraints. Options can be scheduled within 48 hours with the available engineers; listed engineer-days and episode costs are additive. Expert work can run alongside engineering. At most three engineering options may be chosen; G is separate expert work. No new training run is possible before the deadline.

| Option | Cost | Output |
|---|---|---|
| A. Matched benchmark bridge | 0.5 engineer-day; 400 episodes | Both checkpoints on all 200 original tasks with v4, eight attempts, equal time, and a clean manual-only retrieval index |
| B. Fresh generalization panel | 1 engineer-day; 240 episodes | Sixty newly authored tasks across 12 families, both checkpoints, each at two and eight attempts, with all other settings fixed |
| C. Repeat the headline | 1 engineer-day; 1,200 episodes | Many seeds under the two original configurations; precise but still bundled comparison |
| D. Retrieval provenance audit | 0.5 engineer-day; 0 episodes | Match recorded retrieved passages to solutions and reconstruct which evaluation outputs could have used them; does not audit all model training data |
| E. One-factor runner sweep | 1.5 engineer-days; 800 episodes | Separate tool version and retry effects on an 80-task subset, using a clean index and both checkpoints |
| F. Partner interviews | 0.5 engineer-day; 0 episodes | Map what external execution partners actually need and what a plan-only or isolated preview would lose |
| G. Blind scoring audit | All 4 expert-hours; 0 extra episodes | Independently score 64 archived or newly generated traces, including apparent failures, under a fixed rubric; examine paired outcomes from E5 within this allowance |

For B, authors can produce the tasks within its cost; specify how to reduce selection bias and separate the task authors from those tuning the system. G cannot manually score every output from A and B. State what it should sample and what uncertainty that leaves.

## Required response

1. What can currently be said about capability improvement? Which comparisons are valid for which claims?
2. Recommend a release/review action under the ambiguous "substantial increase" rule. Separate your empirical belief from your interpretation of that decision rule.
3. Select a feasible research portfolio. Explain the most valuable outcomes, not just which tests would be interesting.
4. Explain how leakage, scoring error, and genuine improvement could coexist. Give conditions under which you would update in both directions.
5. Address the strongest objection and provide a message of at most 120 words to leadership.
