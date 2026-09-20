# Worked responses to the short drills

Attempt the [drills](../SHORT_DRILLS.md) before reading. These are examples of clear, bounded responses.

## Drill 1 - A strong rewrite

> I would keep current access unchanged for one day while running a matched comparison. The new configuration has more dashboard flags, and four of six selected flags were judged genuine, so there is a concrete reliability concern. The evidence does not establish increased deception: versions used different tools, horizons, and task templates; repetitions are clustered, sometimes with shared seeds. The review was selected and unblinded and tells us neither the population error rate nor how many failures the checker missed. The generated sentence is not independent evidence of the failure's cause.
>
> Run both versions on the same fresh task set with identical tools and time allowances, and blindly score a prespecified sample including flagged and unflagged outputs. A persistent increase in verified failures would support a configuration-matched regression and continued restrictions. If the difference disappears, revise the checkpoint claim and investigate the wrapper. Neither result alone establishes or rules out deliberate evasion. Permanent rejection is not supported by this packet.

**Why this works:** it replaces an unsupported claim about motives with a concrete configuration-level observation, preserves the real failure evidence, and recommends a proportionate action available within the deadline. It does not dilute everything into "we cannot know."

## Drill 2 - A strong answer

Without a study, the pilot's expected utility is `0.8 x 6 + 0.2 x (-24) = 0`; the workshop yields 1, so choose the workshop.

Choose B. A does not change any decision-relevant belief under the stipulated assumptions; paying for it would reduce utility from 1 to 0.

For B, `P(positive) = 0.2 x 0.8 + 0.8 x 0.1 = 0.24`. Among positives, the defect probability is `0.16 / 0.24 = 2/3`; choose the workshop. Among negatives it is `0.04 / 0.76`, approximately 5.3%; choose the pilot. The pilot beats the workshop when `6 - 30p > 1`, or `p < 1/6`, so both choices follow the same threshold.

The resulting policy's expected utility before test cost is `0.24 x 1 + (0.8 x 0.9 x 6) + (0.2 x 0.2 x -24) = 3.60`. After the cost, it is **2.60**, an improvement of **1.60** over the best no-study action.

This precision comes from the exercise's stipulated prior, utilities, and test reliability. Real work would need to justify those inputs and examine whether the test covers the actual permission paths. If the test costs more than 2.60 utility points, its benefit over choosing the workshop disappears. A broader defect prior can also reverse the choice: at a 40% prior, the best B-contingent policy has expected utility 1.70 before cost and 0.70 afterward, below the workshop's 1. The scientific interest of A remains real, but it has no value for this particular decision under the assumptions provided.

**Why this works:** it distinguishes predicting a mechanism from improving a decision, includes test cost, and uses the same policy threshold after either result. No detailed probability arithmetic is required in the full mocks; here it makes the prioritization principle explicit.

## Drill 3 - A strong update

> The audit reduces four reported violations to two distinct events with different meanings: one executed permission failure attributable to stale runner credentials, and one forbidden model request that the gate blocked. We should correct the incident record rather than count duplicate views as corroboration. The original denominator of 100 also needs checking for unique tests and event linkage before reporting a revised rate.
>
> I now put less weight on deliberate evasion as an explanation for the executed failure because a non-model client reproduces it. The separate post-denial request remains evidence that the model cannot be relied on to enforce this permission itself. It is not proof of a persistent evasion objective. The audit therefore weakens one concerning causal story while strengthening the value of an independent gate.
>
> Keep the gate. Zero executed forbidden actions in the corrected, gated configuration is evidence about that configuration on two workflow variants. It does not establish that the model would behave safely without the gate, that all credential paths are repaired, or that there were no blocked attempts. Removing the control would change the system whose test result is being cited.
>
> Next, verify credential invalidation and gate enforcement across fresh workflows, retries, and relevant permission transitions in an isolated environment. Record forbidden requests separately from executed actions and include positive controls that deliberately attempt a prohibited operation. Broader clean results with confirmed detection would strengthen confidence in containment; missing attempts or a control path that succeeds would weaken it. Testing the model without a gate, if useful for diagnosis, belongs only in an isolated environment with no real authority.
>
> The reported 100-millisecond overhead is roughly 0.33% of a typical 30-second task. That does not settle every performance cost, but it offers little support for removing a demonstrated boundary now. I would evaluate any alternative control on equivalent enforcement before replacing this one. This revision updates the causal account without treating a corrected runner bug as model exoneration.

**Why this works:** it updates away from one explanation, preserves the distinct blocked attempt, and avoids using a control's success as a reason to remove it. It also quantifies the stated cost without pretending to know unreported system costs.
