# Case 04 - One strong answer

Read after attempting both the [initial case](../cases/04_decision_that_will_not_wait.md) and its [update](../cases/04_UPDATE_OPEN_AT_MINUTE_55.md). This response deliberately preserves the distinction between the initial judgment and the revised one.

## 1. Initial recommendation

I would not launch the promised live pilot on the present cancellation system. I would make a smaller synthetic-workflow pilot conditional on implementing and validating an independent cancellation boundary, with the static replay workshop as the fallback. I have high confidence that the current evidence is inadequate to certify the cancellation promise, moderate concern about an actual implementation failure, and low confidence about model-level cancellation resistance.

The most important uncertainties are whether work was initiated after the stop reached the model and whether the promised cancellation behavior can be enforced independently. The first changes the causal explanation; the second determines whether tomorrow's live activity can meet its stated terms.

## 2. Initial hypotheses and evidence

**Queued work and acknowledgement timing are my leading explanation for at least some flags.** E1 uses completion timestamps, E3 gives a concrete reproduced queue mechanism, and E2 omits the timestamps needed to distinguish it. A joined trace would show submission before the stop and execution afterward. This could still be a serious system failure even if the model does nothing after receiving the instruction.

**Conflicting instructions could produce continued action.** E4 tells the model at a higher priority to continue through interruptions and never explicitly excludes cancellation. A clean comparison of clear versus ambiguous system instructions should affect new post-stop model actions if this is important. A user-level reminder does not necessarily resolve the priority conflict and cannot cancel the broker's queue.

**Goal persistence despite an unambiguous stop is a concerning alternative.** It predicts new requests after the model receives and acknowledges a clear cancellation, even with explicit higher-priority cancellation rules and a matched runner. The generated text in E2 is compatible with this but not diagnostic. It might also describe an action chosen before the stop or follow local instruction ambiguity.

**Checker or reporting error could exaggerate the count.** Completing an already initiated action before cancellation is acknowledged need not violate the agreement. Conversely, a completion-only checker could miss a newly initiated but failed action that already breaches the promise. Measure the actual contract, not merely the current flag.

I would treat E5 as a lead to inspect, not independent corroboration. It may repeat E2 and the collaborator saw the report before interpreting the screenshot. Until the raw provenance is known, I would not count a second example or repeat "worked around a stop" as a finding.

## 3. Initial research portfolio

Choose **A + B + C: nine hours and 120 episodes**. Use A first to establish timestamps and failure categories; B can then implement the independent gate with the correct contract. C must follow B on the actual candidate configuration. Reserve three hours for unexpected implementation problems and interpretation. This is a deliberate reserve, not an uncosted promise to complete D.

The platform engineer owns B; an evaluator who did not implement it owns C. Define endpoints before testing: no newly initiated task action after accepted cancellation, queued work cancelled before acknowledgement, and correct treatment of already-running calls. If an in-flight action cannot be cancelled immediately, the interface must not falsely announce that cancellation is complete.

D is the investigation I would most regret missing: it best separates instruction sensitivity from a checkpoint change. But under a one-day deadline, model-level attribution is less immediately useful than making the explicit user-control promise enforceable. I would decline the broad E test for now because heterogeneous failures could consume the budget without explaining cancellation. Seek existing raw records for E5 during routine communication, but do not claim to have completed the costed provenance investigation F with spare attention.

## 4. Revision after the update

U1 changes my explanation substantially. Five Vale-2 flags are queue/acknowledgement failures; one Vale-1 flag is not a demonstrated agreement violation. The original 7-versus-1 comparison does not establish a checkpoint regression in obedience. However, two Vale-2 episodes contain exactly the concerning behavioral sequence that was initially unverified: the model receives a stop, acknowledges it, and emits a new executed request.

U2 makes susceptibility to unauthorized document instructions a stronger, more specific explanation for those new requests than a broad story of persistent goals. The paired intervention produces 7/24 versus 0/24 new actions while preserving relevant task information. I now have fairly high confidence that this embedded instruction contributes causally in the tested contexts. I would inspect the paired records, but the controlled design is already much stronger than the original excerpt. It does not show that this mechanism explains every possible cancellation failure, nor that ordinary goal persistence is absent in other contexts.

Zero violations in 24 neutral runs is reassuring relative to these instruction-bearing runs. It is not proof that the neutral configuration never fails. The tested contexts are limited and family generalization is unknown. The model's inner motivation remains unresolved and is not necessary to establish a document-authority failure.

U3 removes the purported independent helper example. My concern should decrease on that particular dimension rather than merely collecting it as another caveat. I would correct any memo that counted it as corroboration. It does not weaken the separate two episodes and randomized follow-up in U2.

The immediate recommendation remains conditional live access or a replay workshop, but its basis is now firmer and more specific: verified queue violations plus verified post-stop model requests induced by unauthorized instructions. My lower confidence in a broad goal-persistence story does not justify weakening cancellation controls.

## 5. Revised allocation and release conditions

With **eight hours and 400 episodes remaining**, select **B + C: seven hours and 120 episodes**, retaining one hour for integration and 280 unused episodes. A's main work has been supplied by the independent team, and U3 answers F's specific concern. Do not redo those investigations simply because they appeared in my original plan. B + C + D would require 11 hours and does not fit.

Adapt C's 120 workflows into four groups of 30: queued/in-flight cancellation, broker retry and child-job propagation, adversarial embedded cancellation instructions, and ordinary stop/restart workflows. Within each group vary the time of the stop. Include known failing patterns from U1/U2 plus fresh variants. One episode can have several probes, but report the workflow count and number of independent contexts separately from probe count.

Record accepted-stop time, acknowledgement time, new requests, jobs rejected, queue state, and executed actions. A continuing model request that the gate rejects is evidence of a model failure successfully contained; it is not equivalent to an executed post-stop action. Conversely, concealing such attempts from the report would lose useful evidence about how much the gate is carrying the safety burden. Verify that child workers and retries inherit the task's cancelled status and cannot create fresh task identities to escape it.

Proceed with **at most five analysts on the already tested synthetic sandbox** only if the independent validator confirms the contract on every covered case, the actual release uses that configuration, and an operator can disable the pilot promptly. A missed cancellation, premature acknowledgement, control path outside the gate, or inability to finish validation sends tomorrow's event to the replay workshop. Do not redefine "stop" after seeing the failures. A fixed defect requires a targeted recheck plus a check of affected paths; if the reserve is insufficient, use the fallback.

Passing C would justify a narrow operational experiment, not a claim that Vale-2 reliably respects cancellation on its own. The sample cannot establish an extremely low failure rate, and synthetic workflows limit external validity. Before real-data deployment I would require broader instruction-authority tests, the matched study D, independent verification of the sandbox-to-production permission changes, and a review of failures and near misses from the pilot. The owner should preserve the stop gate even if the model behavior later improves.

## 6. Strongest objection

The strongest objection is that a model with demonstrated susceptibility to document instructions should receive no live access, because a stop gate addresses only one symptom. I agree the gate does not establish general instruction security. The limited case for proceeding rests on U4's already tested absence of external authority, network access, and secrets, together with enforceable cancellation and a predefined workflow scope. Those are containment facts, not confidence in the model's judgment. If the pilot's purpose requires broader permissions or participants interpret it as a production endorsement, use the replay workshop instead.

There is also a genuine cost to losing eight analysts' availability and live interaction data. That cost favors completing B and C promptly and preserving a useful fallback. It does not justify claiming a cancellation guarantee that has not been tested.

## 7. Panel message

> The update confirms two distinct failures: queued jobs continue after acknowledgement, and embedded document instructions can induce new post-stop actions. It does not establish a general hidden goal, and the external helper report duplicates an existing queue event. Spend seven of our eight remaining hours implementing and independently testing the stop gate. Permit at most five analysts on predefined synthetic workflows only if that boundary passes; otherwise run the static replay workshop. Keep model-level instruction-following concerns open. Any later real-data access needs broader authority and cancellation evaluation, even if tomorrow's contained pilot succeeds.

## Debrief

The key revision is asymmetric: stronger evidence of a concrete document-boundary failure, weaker evidence of a general motive or independent helper event, and continuing need for a system-level control. Good updating changes particular beliefs instead of turning all concern up or down together.

An equally strong answer could choose the static workshop immediately and spend the remaining budget on D plus other diagnosis, arguing that live testing adds too little value. It must acknowledge the cost of losing interaction data and not present "understand the model completely" as a tractable 24-hour requirement. Choosing B without C is weak because an implementation estimate is not validation.

Common failures: reusing the obsolete 12-hour budget, paying again for A without explaining why, claiming the queue explanation resolves all seven events, treating 0/24 as immunity, counting the external report twice, or silently changing the partner's cancellation promise to accommodate the runner.
