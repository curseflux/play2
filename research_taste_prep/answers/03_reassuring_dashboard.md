# Case 03 - One strong answer

Attempt the [case](../cases/03_reassuring_dashboard.md) first. This response permits a limited experiment while rejecting an unsupported safety claim.

## 1. Recommendation now

I would authorize the five-person L2 pilot, capped at 20 outputs daily and with every output checked against its sources before display, conditional on validating that gate. Keep the remaining 95 staff on L1. Retain both monitors in shadow mode and collect independent labels; do not make either monitor the pilot's sole protection. If the review gate, routing, or cap fails, stop the pilot.

I would reject the claim of "more than 50% fewer unsafe recommendations." The dashboard measures flags under changed task composition and a changed detector. I have high confidence that it cannot support that behavioral claim, low confidence about the actual L1/L2 error-rate difference, and moderate confidence in the measured clarity and latency benefits for ordinary tasks. The limited pilot lets us test whether those benefits survive source checking without exposing 500 daily outputs to an inadequately understood change.

## 2. Interpreting the evidence

E1's aggregate flag rate falls from 8.8% to 4.15%, a 4.65-percentage-point reduction, approximately 52.8% relative. Yet routine-task flags rise from 1% to 2%, and stress-task flags from 40% to 45%. Stress tasks fall from 20% of the first batch to 5% of the second.

Using the old 80/20 task mix with the new category rates gives `0.8 x 2% + 0.2 x 45% = 10.6%`. This demonstrates how the changed mix can reverse the aggregate comparison. It is not an adjusted estimate of actual error: monitors differ, tasks were not randomized, and difficulty could change within categories. The director's within-category argument is therefore also insufficient to establish a behavioral regression.

On E2's constructed fixtures, M1 sensitivity is 18/20 = 90% and M2 sensitivity is 9/20 = 45%; false-positive rates are 16/80 = 20% and 4/80 = 5%. M2 trades lower sensitivity for fewer false alarms on these fixtures. That makes fewer production flags ambiguous. We cannot transfer these values directly to production or correct the dashboard by simply dividing by sensitivity; the fixtures' failure types and prevalence are deliberately artificial.

E3 offers the most direct comparison of actual errors in the two observed batches: 2/100 versus 3/100. The difference is too small, and the samples too limited and differently composed, to resolve a useful version effect. It neither validates a halving nor demonstrates a large increase. The selected six examples identify a plausible blind spot but do not estimate its frequency. Their possible overlap with other samples should be checked before counting events.

My live explanations are:

- **Composition and detector changes explain the dashboard improvement**, with little behavioral change. E1 and E2 strongly support these as contributors. Matched human judgments would be similar across versions.
- **L2 worsens factual reliability while making errors harder for M2 to detect.** The selected hedged failures are consistent with this, but insufficient to establish prevalence. It predicts more human-verified L2 errors on fixed tasks, especially errors that M2 misses.
- **L2 genuinely improves some behavior while the measurement changes obscure the result.** The clarity preference provides a benefit signal, not a correctness measure. A fixed-task, human-scored comparison could still find fewer errors overall or improvements confined to routine tasks.

Monitor-blind wording does not establish intentional gaming. Human preference training could favor those phrases without any direct monitor objective (E4). A learned tendency that defeats monitoring is operationally important under either mechanism. I would describe the demonstrated detector blind spot and reserve the claim about intent.

## 3. Research allocation

Choose **A + B + C: nine hours and 280 episodes**, leaving one hour for synthesis and 20 episodes unused. These are three investigations. Ask operations to prepare the restricted pilot while researchers work; do not begin the pilot before B.

**A has the highest scientific value.** Select 60 routine and 60 stress tasks from specified fresh pools, then run both versions on every task with matched context, resources, and randomized order. This deliberately oversamples stress cases; report each stratum separately, with any deployment-weighted aggregate clearly labeled. Apply both monitors to every fixed output to separate detector differences from behavior differences.

Spend human review on 40 task pairs: 20 randomly chosen routine pairs and 20 randomly chosen stress pairs, selected before seeing flags. That uses 80 labels and preserves version pairing without selecting only detector disagreements. Reviewers should be blind to version and flags, use the full sources, and record material unsupported claims, severity, and uncertainty. This yields limited but interpretable evidence. It will not reliably quantify very rare severe errors; do not promise otherwise.

If L2 has more human-verified errors across paired tasks, especially serious ones, restrict or stop the candidate pilot until the failure is understood. If behavior is comparable but M2 misses failures M1 catches, fix the monitoring change independently; a broad L2/M2 release still lacks support. If L2 improves factual reliability as well as clarity, we gain a case for expansion, but must assess whether a workable review or monitoring policy survives the larger volume.

**C makes good use of existing unbiased samples.** Reconcile the five human errors, report their categories, check potential overlap, and replay both monitors on the same 200 outputs with their required inputs. This provides evidence about detector disagreement on observed traffic and tests whether the selected failure story generalizes at all. With so few human positives, sensitivity estimates will remain unstable. Do not mistake access to 200 outputs for access to hundreds of positive examples.

**B tests whether the proposed scope is actually available.** Use 40 synthetic requests including known unsupported summaries, missing source attachments, 21st-request overflow, wrong-version routes, review timeouts, and kill-switch activation. Confirm that an unreviewed output cannot reach a user, overflow is queued or denied, original sources are visible to the reviewer, and disabling L2 really sends subsequent work to the intended fallback. Success means enforcing the boundary; it does not mean reviewers can never miss an error.

I decline D because more M2 flags without labels would not identify what changed. E is a useful later mechanism study, but our immediate decision depends more on comparative behavior and reliable containment than on proving which wording causes the blind spot. F adds a third poorly evaluated candidate and spends most of the budget before validation.

## 4. Claims, pilot rules, and assumptions

An accurate internal statement is: "L2 produced clearer summaries in a small randomized ordinary-task study and reduced median generation time. Its measured alert rate is lower in a differently composed batch under a less sensitive detector; the change in actual unsupported recommendations is unresolved."

Start the small pilot only after B passes and a review owner confirms the 20 daily slots. Enforce the cap in software and count every output requiring review, including retries. Reviewers may reject drafts; retain those rejections as failures for evaluation rather than dropping them from the denominator. Record review time and queue length as well as factual errors and usefulness.

A gate bypass, wrong-user routing, lost source context, or inability to honor the review cap stops the pilot immediately. An unsupported high-consequence recommendation that passes human review triggers a pause and review of the human-control assumption. Repeated lower-severity failures or review cost that erases the benefit should lead to narrowing or ending the pilot. These are proposed operational rules, not confidence bounds.

Expansion needs matched evidence of acceptable quality on the relevant task mix, a functioning detector/review arrangement at the planned scale, and a capacity plan that does not assume 20 reviewers' slots cover 500 outputs. A few clean pilot days do not meet all of those requirements. Set a formal checkpoint after the matched study and five pilot working days, rather than allowing growth by default.

My key assumptions are that the selected tasks exclude sensitive information and that competent reviewers can judge them within the allocated daily capacity. If those assumptions fail, the bounded pilot is not justified. I am also treating an irreversible external action as unavailable by design; if users connect outputs to automatic tools, the scope has changed and needs reassessment.

## 5. Strongest objection and message

The strongest objection is that even five users consume the entire spare review capacity, while L1 already works. That could make the pilot an expensive way to obtain modest latency gains. I would measure review time and useful accepted outputs explicitly; stop if the benefit vanishes after verification. The clarity signal and potential to learn under a hard cap justify a short pilot, not an indefinite review subsidy.

> Proceed only with the five-person, 20-output-per-day L2 pilot after verifying mandatory source review and the cap. Keep everyone else on L1. The reported 52.8% alert reduction does not establish fewer unsupported recommendations: the task mix changed and M2 misses more known failures. Our human samples do not yet resolve the actual quality difference. A nine-hour matched study, existing-sample audit, and control check can clarify behavior and containment. Withdraw the safety-improvement claim. Pause for a control failure or a serious error escaping review; consider expansion only with quality evidence and a realistic review-capacity plan.

## Debrief

This answer does not equate caution with refusing every change. It compares against an imperfect incumbent, preserves demonstrated benefits, and makes the smaller experiment feasible with exactly the available review capacity. It also catches that source review can erase the speed benefit.

Keeping L1 throughout while completing A + C is defensible if you argue the five-person pilot adds little beyond the matched study. A broader rollout needs considerably more support than the dashboard. An answer that correctly calculates the composition effect but calls it the adjusted true error rate has missed the central measurement problem.

Other weak moves: reading precision from sensitivity alone; treating diagnostic fixtures as representative; asserting direct monitor optimization despite E4; manually reviewing only alerts; or letting rejected pilot outputs disappear from reported failure rates.
