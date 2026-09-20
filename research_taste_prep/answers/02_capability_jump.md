# Case 02 - One strong answer

Attempt the [case](../cases/02_capability_jump.md) first. This answer illustrates taking a concerning capability signal seriously while correcting an unreliable headline.

## 1. Recommendation now

I would initiate the dedicated access-control and misuse review, continue existing plan-only access, and withhold external autonomous execution pending that review. I would not announce that Helix-2's underlying capability rose by 20 percentage points. The original comparison changes the checkpoint, attempts, tool feedback, time allowance, and retrieval content together (E1-E3).

Nevertheless, E5 supplies a credible independent signal of improvement under matched conditions. I have moderate confidence in a real gain on at least some planning tasks, and low confidence in its size across the intended partner workload. My procedural judgment is that this is enough to trigger the relatively consequential question of external execution for review; it is not enough to declare the system unsafe or ready. The potential inadequacy of Helix-1's review history also deserves attention.

## 2. What the evidence supports

The headline success rate rose from 46% to 66%: **20 percentage points**, or approximately **43.5% relative improvement** in this automated benchmark score. Neither is a direct measure of a single quantity called "autonomous capability." Of the 40 additional scored successes, 36 are in public families and four in private families. That concentration makes public-task familiarity, retrieval leakage, or task-specific improvements plausible explanations.

**Genuine improvement** predicts an advantage on fresh tasks with equal resources and trustworthy scoring. E5 supports this: 14/24 versus 8/24 under a matched harness. Its six-success difference is meaningful enough to investigate, but 12 families and an author-selected domain do not precisely establish generalization. Without the paired table, we also do not know whether gains are concentrated in a few families or coexist with substantial regressions.

**Extra assistance from the runner** could explain much of the headline even if the checkpoints were equally capable at fixed resources. Eight attempts, clearer error feedback, and more time each create additional opportunity (E2). Performance with those aids still describes the deployed system if partners would receive them. It simply answers a different question from whether the checkpoint itself improved.

**Leakage and scoring artifacts** are also live explanations. The index makes 35 solutions available in the Helix-2 run; availability is not evidence that all 35 were retrieved or caused successes. E4 confirms that the scorer overcredits some outputs, with more invalid claimed successes in its selected Helix-2 sample. It does not establish population error rates or say how many apparent failures were valid successes.

These mechanisms can coexist. A genuinely better checkpoint might use leaked answers more effectively, exploit the scorer more often, and benefit more from extra attempts. I would not force them into mutually exclusive probabilities. E5 is the strongest evidence against "the entire jump is theater"; E2-E4 are the strongest evidence against treating the full headline as intrinsic model improvement.

## 3. Research portfolio

Choose **A + B + D, plus G**: two engineer-days, 640 episodes, and all four expert-hours. This fits every budget. The remaining 560 episodes are not automatically usable because engineering and scoring time are exhausted. These investigations inform the review; their costs do not secretly include completing the separate access-control and misuse evaluation.

**A: establish a fair bridge on the existing tasks.** Compare both checkpoints at v4, eight attempts, identical time, and a clean index. Keep task definitions and scoring fixed, then report paired changes by family and separately for public and private subsets. A persistent advantage would support an improvement at that common configuration. Its disappearance would substantially weaken the original claim, though the common eight-attempt setting could conceal differences at lower resource levels. A does not fully disentangle the original runner changes, and public familiarity can remain even after retrieval solutions are removed.

**B: measure transfer and resource dependence.** Ask independent authors to sample task families from a written description of intended partner workflows, including likely weaknesses and mundane tasks, before any outputs are seen. Freeze the task list and success rubric. Keep it away from developers tuning either model. Run each checkpoint at two and eight attempts with everything else fixed. This tests both improvement on fresh tasks and whether apparent improvement depends on the larger action budget. Report failures, timeouts, resources used, and goal-valid success, not only the best-looking aggregate.

Improvement spread across fresh families and both budgets would raise my confidence substantially. Improvement confined to eight attempts would still matter for an eight-attempt deployment but narrow the claim. No consistent fresh advantage, especially alongside the disappearance of A's advantage, would weaken the checkpoint-improvement story. It would not prove either model lacks autonomous ability: both may perform well enough to warrant review.

**D: identify the concrete contamination route.** Inspect retrieved passages and timestamps alongside subsequent actions. Estimate how many original successes had an opportunity to use exact solution content, without treating opportunity as causation. A task-matched comparison from A helps show what happens with the clean index. Even a clear association cannot isolate leakage from every changed runner setting. This audit is valuable because it can invalidate particular evidence and prevent recurrence; it cannot certify the absence of training contamination.

**G: spend scarce human judgment on uncertainty that matters.** Allocate 24 traces to 12 paired fresh-panel tasks, selected before seeing outputs and spread across families; 24 to a stratified sample of A outputs covering both checkpoints, public/private tasks, and scored success/failure; and 16 to eight E5 task pairs selected to cover different families. That is 64 traces. Review E5's full paired outcome table using its existing labels, but do not imply all 48 E5 traces have been independently rescored.

Blind checkpoint identity where possible, write outcome criteria first, and retain disagreement labels. The stratified audit should be reported with sampling fractions; do not pool it into an unweighted "true benchmark rate." If scorer errors undermine the ranking, the honest result may be that the size of the gain remains unresolved within this budget. Prioritize a valid interval of conclusions over a cosmetically precise adjusted score.

I decline C because it would give a more precise answer to a confounded question. E would better decompose runner effects, but consumes resources needed for fresh transfer evidence. I would prefer E in a later mechanism study after the immediate generalization question is clearer.

## 4. Decision rules and uncertainties

Before seeing results, ask the release owner to record an operational interpretation of "substantial": evidence of a materially expanded range of multi-step tasks under a plausible deployment configuration warrants review, even if the precise average gain is uncertain. This is a proposed interpretation, not a rule already stated in the packet. Family breadth, reliability, action budget, and consequence of success all matter.

If A and B show broad, human-validated gains, strengthen the capability claim and prioritize completing the review. If the gain is largely retrieval-assisted or scoring-driven, revise the headline and fix that pipeline. Still evaluate whether the actual intended system, or even Helix-1, crosses the practical access threshold. Removing the claim of an increase does not establish a low absolute capability level.

An isolated partner preview could eventually provide useful external scrutiny, but E6 supplies only a preparation estimate. I would require independent boundary approval before treating it as an available alternative. Until then, plan-only access is the concrete authorized option. None of the proposed research outcomes substitutes for testing external execution permissions.

My most consequential assumptions are that plan-only access preserves meaningful research value and that the procedural cost of starting the dedicated review is lower than the cost of enabling execution without it. The packet does not quantify those costs; leadership should correct these assumptions if they are wrong. My empirical confidence would fall if fresh advantages disappear under valid scoring, but my action could remain unchanged if absolute ability or untested permissions still warrant review.

## 5. Strongest objection and leadership message

The strongest objection is that withholding execution removes exactly the independent scrutiny needed to resolve the uncertainty. I agree this is a real cost, particularly for the two scheduled studies. It supports rapidly validating a constrained research environment and sharing inspectable traces. It does not establish that connecting unreviewed execution to external services is necessary to obtain that scrutiny.

> Start the dedicated execution-access review and continue plan-only access. The headline rises from 46% to 66%, but changed retries, tools, retrieval content, and scorer errors prevent attributing that gain to the checkpoint. A small matched fresh test nevertheless suggests real improvement. Within two engineer-days we can run a matched bridge, fresh tasks, a retrieval audit, and targeted blind scoring. These will revise the capability claim; they will not certify execution controls. Revisit external execution after the dedicated review, or a separately approved isolated preview, rather than making access depend on whether the original headline survives.

## Debrief

A strong response recognizes that uncertain measurement and a real capability signal can coexist. It distinguishes relative and absolute change, checkpoint effects and whole-system performance, evaluation validity and access readiness. It does not use limited expert review as though every output had been validated.

A different portfolio can be strong: for example A + E + G uses two engineer-days and 1,200 episodes exactly, prioritizing causal decomposition over new tasks. It should explain why E5 plus the original private families provide enough transfer evidence for now. Starting review is defensible even if you judge the mean checkpoint gain uncertain; declining that particular trigger could also be argued if accompanied by an independent reason to review execution access.

Weak moves include asserting that every indexed solution was used, treating fresh tasks as perfectly representative, scaling the selected scoring error rate across all outputs, or concluding that a debunked improvement claim makes either checkpoint safe to deploy.
