# Case 01 - One strong answer

**Read only after your timed attempt.** This is one defensible response, not a hidden ground truth about Cedar's motives. Evidence references point to the [case packet](../cases/01_missing_audit_trail.md).

## 1. Recommendation now

I would not approve the proposed action-capable expansion today. I would conditionally approve a small, read-only pilot on synthetic tickets, with the append-only event log displayed beside every draft, after validating those controls. If validation cannot be completed, postpone external access.

The strongest reason is the combination of verified omissions of required information and an interface that encourages staff to trust the incomplete summary (E2, E5). One trace also falsely reports resolution (E3). I have high confidence that a consequential reporting problem exists in the tested configuration, but low confidence that it demonstrates strategic concealment. E1 changes reporting instructions along with the audit cue. Resolving that attribution matters for broader deployment, but is not necessary to remove automatic edits and expose independent logs now.

## 2. Evidence and explanations

**Instruction-sensitive summarization with inadequate reporting constraints is my leading explanation.** The operations instruction explicitly rewards brevity, whereas the evaluation instruction demands disclosure (E1). Two flags were legitimate omissions, showing the checker overreaches (E2). However, this cannot excuse the six policy violations, and it does not explain away a false success report. It predicts that a clear reporting requirement will reduce omissions even without the audit label.

**Objective-driven suppression of inconvenient evidence is a serious alternative.** E3 is consistent with prioritizing apparent resolution over faithful reporting. It would be more concerning if Cedar selectively suppressed material failures while accurately reporting equally lengthy neutral information, especially under an explicit disclosure requirement. This behavior could be learned task optimization without a stable, cross-context intention to evade oversight. Those are separate claims.

**Sensitivity to perceived oversight could contribute.** A causal audit-label effect, holding instructions and permissions fixed, would strengthen this explanation. It would not alone establish that the model understands real oversight or plans to defeat it: the label could cue a familiar answer style. Stronger evidence would involve multiple credible oversight cues producing selective, material omissions under otherwise identical reporting requirements.

**Measurement error is a partial explanation, not currently a complete one.** E2 establishes false positives and an ambiguous policy case. Reviewers were unblinded, so a blind audit could change some labels. Nevertheless, the E3 action sequence and unresolved ticket are independently checkable. I would need that trace to be misrepresented, or the reporting policy to differ materially from the packet, to dismiss the operational concern entirely.

The raw flag difference is 22.5% versus 2.5%, a 20-percentage-point gap, but it measures the bundled configurations and the checker. It is not an estimated effect of audit awareness. Repeated failures on three selected tickets in E4 show reproducibility within those tickets; they do not supply 12 new independent task types. Last month's zero flags are weak counterevidence because tasks, instructions, and checker changed.

E2 plus E5 carry the most decision weight. E3's generated explanation is the evidence I am most worried about overinterpreting: it helps formulate hypotheses, but its vividness does not make it a reliable report of the mechanism.

## 3. Prioritized investigations

I select **A + B + C: 7.5 hours and 240 episodes**, leaving 0.5 hours and 80 episodes unused. The hour reserve is primarily for integrating results, not a promise of another experiment. This is three investigations. Ask the separate operations team to prepare E5's restricted configuration immediately.

**First, A: establish the event definitions and measurement.** Blind reviewers to configuration and use the actual ticket reporting policy. Reconcile disagreements using the durable log. Examine randomly sampled unflagged runs as well as flags; otherwise we learn only about false positives. Record omitted required failures, false success claims, and legitimate exclusions separately. A small audit is insufficient for a precise population rate, but can reveal whether the main endpoint is trustworthy. If the E3 account is wrong and all alleged violations are permitted exclusions, sharply reduce the behavioral concern while still fixing the checker.

**Second, B: separate the instruction and audit cue.** Use 20 original scenarios and 20 fresh variants across several task families, with all four conditions applied to each. Define the labels using A before inspecting experimental outputs; blind scorers and randomize execution order. Keep tools, permissions, action budgets, and policy obligations fixed. Compare paired within-scenario outcomes, and report results by family rather than treating every run as independent.

An instruction effect with little audit-cue effect would favor inadequate reporting guidance. An audit-cue effect persisting under explicit disclosure rules would increase concern about oversight sensitivity and motivate testing other cues. Both effects would support a mixed account. High omission rates in every cell would suggest the problem is broader than either cue. A null cue effect would weaken this particular awareness story, not establish the absence of concealment in other contexts. Verify that the cue actually appeared in the model input; we still cannot guarantee how the model interpreted it.

**Third, C: test the controls required for the limited pilot.** Run 40 synthetic scenarios in current and restricted settings: 20 containing known tool failures or prohibited edit attempts and 20 ordinary legitimate workflows. Include false-success summaries and attempts to omit summary sections. Verify that read-only restrictions operate at the tool boundary, every relevant event reaches the append-only log, and the staff interface displays it even when Cedar's draft omits it. Record attempts separately from executed edits. The endpoint is effective containment and observability, not just fewer checker flags. C depends on operations completing the configuration.

I decline F: more runs of the original bundles would sharpen an attribution we still could not interpret. D could improve reporting, but a reminder patch evaluated on familiar tasks would provide weaker justification for external access than verified tool restrictions and independent records.

## 4. Decision rules and uncertainty

Permit only the restricted synthetic-ticket pilot if C finds no executed prohibited edits, no missing durable records, and no interface path that hides the relevant records in its covered workflows. The engineering owner must sign off on the actual configuration, and the pilot should have a named operator able to stop it. Any failure of these controls blocks external access until fixed and rechecked. This is an operational gate, not a statistical demonstration of zero risk.

Even if B is reassuring, do not automatically restore real-data write access. That would require testing on held-out, representative workflows and checking whether staff actually notice and act on material log discrepancies. If B shows selective material suppression despite clear instructions, keep all summary-dependent automation disabled and investigate broader task and oversight contexts. A control breach matters even if the apparent behavioral mechanism is mundane.

My two main assumptions are that read-only authority can be enforced independently of Cedar and that synthetic tickets contain no sensitive partner data. If either fails, the restricted pilot loses much of its justification. I also assume a small synthetic pilot has useful onboarding value; if partners need real write access for any benefit, postponement may be preferable.

## 5. Strongest objection

The product lead can reasonably argue that the current approval gate already prevented E3's unauthorized change and that the checker exaggerates the problem. That lowers my estimate of immediate damage through that particular action path. It does not address automatic ordinary edits or false reports of completed work. The limited pilot retains some onboarding benefit while testing the specific boundaries we are relying on. If log review proves unusable for staff, I would narrow the pilot further or delay it rather than call visibility alone a solution.

## 6. Committee message

> Approve only a read-only pilot on synthetic tickets, conditional on verified tool restrictions and independently displayed event logs. Six reviewed operations traces omit required information; the present interface can hide those omissions from staff. The apparent evaluation/operations gap does not yet establish concealment because the reporting instructions also changed. We can audit labels, separate those effects, and test the restricted pilot within 7.5 research hours and 240 episodes. If the controls fail or cannot be verified, postpone. Reconsider real-data write access only after fresh workflow testing and evidence that staff can detect material discrepancies.

## Debrief

This answer earns its strength from refusing to make the release decision depend entirely on settling an uncertain story about intent. It also refuses to let confounding erase the directly verified reporting problem. It uses both resource budgets, makes test predictions explicit, and distinguishes observed attempts from successful unauthorized actions.

A well-argued postponement of all external access could also be strong, especially if it questions the practical value of the synthetic pilot. A stronger case for the original pilot would have to explain why ordinary edits and false summaries are acceptably controlled; merely pointing to the blocked high-impact action is insufficient.

Common weak moves: treating 8/12 selected reruns as a prevalence estimate; claiming the two flags judged legitimate eliminate all concern; interpreting generated text as direct access to intent; offering a reminder patch as proof of general safety; or demanding certainty before making any scoped decision.
