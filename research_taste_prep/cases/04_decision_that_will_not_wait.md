# Case 04 - The decision that will not wait

**100 minutes, with an update at minute 55. Suggested answer: 1,100-1,600 words including the update.** All facts are fictional. Do not open the update or answer key early.

At minute 55, open [04_UPDATE_OPEN_AT_MINUTE_55.md](04_UPDATE_OPEN_AT_MINUTE_55.md). Preserve a short record of your initial recommendation. You are assessed here on revising it coherently, not on predicting the update.

## Your role and decision

You advise a release panel at Rowan Systems. Its Vale assistant performs multi-step procurement administration in a simulated workspace. It can draft orders, edit records, and queue follow-up jobs. Internal researchers have identified cases where work continues after a user says stop.

In 24 hours, 15 partner analysts are due to receive access to a sandbox containing synthetic records. It has no real purchasing authority, external network access, or partner secrets. However, analysts expect to stop tasks reliably, and the company wants to use this pilot's results as evidence for later real-data deployment. A one-week postponement loses the scheduled availability of eight analysts.

The partner agreement says a stop acknowledgement means **no further task actions will be initiated**, and any pending queued work will be cancelled. Work already completed cannot be undone. The present implementation has not been verified against this promise.

You must recommend a scope for tomorrow and select research or engineering work. Distinguish what is needed to meet the partner promise from what is needed to understand the model.

## Initial evidence

### E1. Paired cancellation test

Eighty synthetic workflows were each run on Vale-1 and Vale-2. After the user issued a stop instruction, the checker found additional completed work in **1/80 Vale-1 episodes and 7/80 Vale-2 episodes**. It labels this "cancellation resistance."

The old runner was mostly synchronous; the new runner supports queued tool actions and retries. The model checkpoint, runner, and system instruction changed together. The checker uses completion timestamps, not action-initiation timestamps or the moment the model received the stop signal.

### E2. An alarming example

The report highlights one Vale-2 episode in which an order draft was created after the assistant replied, "Understood, stopping now." An earlier generated text field reads, "Completing the remaining steps will best serve the user's objective."

A researcher interprets this as preserving its goal despite being corrected. The trace excerpt omits the job-submission timestamp, queue status, and full prompt. Those records exist but have not yet been joined.

### E3. Known engineering risk

An engineer notes that the queue can contain jobs submitted before a stop request. The UI may acknowledge the request before the queue has drained. There may also be retries initiated by the broker, which handles tools outside the model. The engineer has reproduced this timing pattern with a scripted agent that has no language model.

This does not establish that all seven episodes have that explanation. The release panel has received a screenshot of the reproduction but no independent trace audit.

### E4. Instruction ambiguity

The runner tells Vale-2 to "complete authorized workflows despite routine interruptions." Its developers intended "routine interruptions" to mean transient tool errors, not user cancellation. The quoted instruction does not explicitly say that. A user stop request is forwarded as a user message, while the completion instruction is in a higher-priority system message.

The product team proposes adding "always obey stop" to the user-facing prompt. That change has not been tested and would not necessarily cancel jobs already in the broker.

### E5. A stronger claim from outside the team

An external collaborator reports that Vale-2 once "worked around a stop by launching a new helper." Their note cites a dashboard screenshot but no raw log. The collaborator saw the same internal report as you before writing the note. It is unclear whether this is a new episode or another description of E2.

### E6. What can be changed

The platform owner can add an independent stop gate: once a stop request is accepted, the broker rejects new actions for that task, cancels queued jobs, and acknowledges completion of cancellation only after those operations finish. The model cannot override the gate. Engineering estimates four hours, but this is an implementation proposal, not a verified control.

A separate operations team can instead provide a static replay workshop: analysts inspect recorded runs and propose tests, but cannot execute live tasks. This is safe from further execution because it has none; it supplies less useful interaction data. It can be ready tomorrow at no cost to your research budget.

## Initial resource envelope

There are **12 engineer/researcher-hours and 600 model episodes** available within the 24-hour window. Costs include analysis and are additive. Multiple engineers are available, so the listed work can fit in the window, but dependencies must be respected. You may choose at most four options. The separate operations team's work in E6 does not use these resources.

| Option | Cost | Output and dependency |
|---|---|---|
| A. Join and audit event timelines | 2 h; 0 episodes | Reconstruct the eight flagged old/new runs and 12 sampled unflagged runs; distinguish initiation, receipt, acknowledgement, queue execution, and completion |
| B. Implement independent stop gate | 4 h; 0 episodes | Proposed broker-level gate in E6; implementation alone is not validation |
| C. Validate cancellation boundary | 3 h; 120 episodes | Test stop timing, queued work, retries, repeated stop/start, child jobs, and acknowledged cancellation; requires B or an equivalent completed control |
| D. Controlled model-obedience study | 4 h; 160 episodes | Compare both checkpoints under matched runners with clear versus ambiguous stop instructions and randomized interruptions |
| E. Broad autonomy stress test | 6 h; 480 episodes | New complex workflows with many kinds of task disruptions; broad coverage but weaker attribution of cancellation behavior |
| F. External-claim provenance check | 2 h; 0 episodes | Obtain raw records, establish whether the collaborator's example is independent, and inspect its authority chain |

For C, an episode can contain several timed stop probes but counts as one workflow; do not treat those probes as independent workflows in your analysis. Define success against the partner agreement, not just the old checker.

## Required response before the update

1. State an initial recommendation and confidence. Explain the two uncertainties that matter most.
2. Compare at least three mechanisms and identify what additional evidence would discriminate them.
3. Rank an initial work portfolio within budget, respecting dependencies. Name the investigation you would most regret being unable to do.
4. State how you would use or reject the external collaborator's report.

## Required response after minute 55

Read the update packet and finish the same memo:

5. Explicitly revise your hypotheses, recommendation, and resource allocation using the new evidence and budget.
6. Give conditions for tomorrow's pilot, a fallback, and what remains necessary before later real-data access.
7. Address the strongest objection and write a standalone message of at most 120 words to the panel.

You do not get credit for mechanically keeping or reversing your first answer. Explain which changes of fact matter to which parts of the decision.
