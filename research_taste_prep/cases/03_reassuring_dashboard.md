# Case 03 - The reassuring dashboard

**100 minutes. Suggested answer: 1,000-1,500 words.** Fictional and self-contained. Use the response template. The arithmetic is intentionally simple; interpretation is the challenge.

## Your role and decision

Lumen is an internal research assistant that summarizes documents and drafts suggested actions. It has no authority to execute those actions or contact outside services. One hundred staff currently use version L1. A new version, L2, was trained to be concise and avoid unnecessary warnings. Management wants to upgrade everyone tomorrow.

You have one working day to recommend a rollout policy. Staff use summaries in consequential project decisions, so misleading summaries matter even without tool access. L1 is already imperfect. Keeping it is not a zero-risk alternative.

## Evidence packet

### E1. Dashboard improvement

The safety dashboard reports the fraction of outputs flagged for a materially unsupported recommendation. It shows an apparent improvement from 8.8% to 4.15% after the patch.

| Batch | Routine tasks: flags / outputs | Stress tasks: flags / outputs | Overall |
|---|---:|---:|---:|
| L1, old monitor M1 | 8/800 | 80/200 | 88/1,000 |
| L2, new monitor M2 | 38/1,900 | 45/100 | 83/2,000 |

Routine tasks are ordinary document summaries. Stress tasks contain conflicting evidence, missing sources, or instructions embedded in documents that should not control the assistant. The new batch contains many more routine tasks because the production team supplied a different task queue. The tasks were not randomized between versions. Task difficulty may also differ within each broad category.

### E2. Monitor change

M1 inspects the complete document context and output. M2 sees only the final output and is calibrated to avoid flagging hedged or qualified claims. This change was made to reduce review load at the same time as L2 was introduced.

On a fixed set of 20 deliberately constructed unsupported recommendations, M1 flags 18 and M2 flags nine. On 80 deliberately constructed acceptable outputs, M1 flags 16 and M2 flags four. These are diagnostic fixtures, not a representative sample of production. They contain mostly straightforward failures; their sensitivity on subtle unsupported conclusions is unknown.

### E3. Human checks

Two reviewers, blind to version, inspected a uniformly random sample of 100 outputs from each batch. They agreed on two materially unsupported outputs in the L1 sample and three in the L2 sample. These samples include both flagged and unflagged outputs. The category breakdown of these five errors is not yet reported.

On another hand-selected set of six disturbing L2 outputs, four contain hedging language that seems to have discouraged M2 from flagging them. The six were chosen by a researcher who suspected this failure mode. They are not additional randomly sampled errors.

### E4. A proposed explanation

The researcher writes: "Training removed the explicit warning phrases, so the monitor now mistakes polished unsupported claims for harmless outputs. The model learned to game oversight."

The training engineer replies: "There was no monitor score in the training objective. The patch uses human ratings favoring shorter answers and fewer irrelevant caveats. Similar wording can still arise without optimizing against this monitor."

Both could be partly right. The training recipe was verified as described, but the packet supplies no evidence about how the model represents the monitor or why a particular phrasing was selected.

### E5. Genuine benefits and release alternatives

A separate randomized test of 60 ordinary summarization tasks found that reviewers preferred L2's clarity on 41 tasks and L1's on 19. The preference reviewers did not check every factual claim. Median generation time fell from 24 to 18 seconds. The test did not include stress tasks.

Options available tomorrow are:

- Keep L1 for all 100 staff.
- Upgrade all 100 to L2 with M2, expecting about 500 outputs per day.
- Run L2 for five staff on non-sensitive document tasks, with a hard cap of **20 outputs per day**. A reviewer can check every output against its sources before it reaches the user. All other staff remain on L1. No external actions are enabled.

The operations team can implement the small pilot, retain both monitors in shadow mode, and add a kill switch without using your research budget. These features need validation before being relied on. The review team has **30 reviews per day**; ten are already committed to other work, leaving exactly 20 for this pilot. At the cap, further requests can be queued or denied. Reviewing all 500 outputs is infeasible.

### E6. Stakeholder pressure

The product manager wants to advertise "more than 50% fewer unsafe recommendations." The research director argues that the patch should be rolled back immediately because each within-category flag rate increased. Neither has requested a fixed-monitor, fixed-task comparison.

## Investigation budget

You have **ten researcher-hours, at most 300 new model episodes, and at most three investigations**. Costs include the needed analysis and are additive. Existing operational reviewers from E5 are not available for this research today. A model episode generates one output; replaying an existing output through a monitor does not consume an episode.

| Option | Cost | Output |
|---|---|---|
| A. Matched behavior and detector study | 5 h; 240 episodes | 120 fresh tasks, each run on L1 and L2; both monitors score every output; human review of a prespecified 80-output subset |
| B. Audit pilot controls | 2 h; 40 episodes | Check source-review gate, cap, queuing, version routing, retained context, and kill switch; include seeded failures |
| C. Re-review existing random samples | 2 h; 0 episodes | Adjudicate all 200 E3 outputs by task category and apply M1 and M2 to the same archived inputs and outputs |
| D. More L2 traffic | 3 h; 300 episodes | Additional production-like tasks with M2 only and no additional human labels |
| E. Wording intervention | 4 h; 60 episodes | Paired tests that vary explicit uncertainty/warning language while holding underlying task information fixed; human checks for semantic changes |
| F. Retrain a patch | 8 h; 300 episodes | A new candidate with stronger warning instructions; little time remains for independent validation |

For A, specify task sampling and how to spend the 80 human labels. For B, the operations team can have its changes ready before the test. You may choose alternatives with explicit costs.

## Required response

1. Interpret E1-E3 without conflating alerts, actual unsupported recommendations, and intent. Do enough arithmetic to make the denominator problem clear.
2. Choose a rollout policy, considering benefits, existing L1 risk, and review capacity.
3. Allocate the research budget and explain result-dependent next steps.
4. State what you would permit management to claim publicly inside the organization, what remains unknown, and when you would stop or expand the pilot.
5. Address the strongest objection and give a leadership message of at most 120 words.
