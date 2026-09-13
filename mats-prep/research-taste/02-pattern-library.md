# Pattern library: the anomaly types a pre-release scenario is likely built on

Confidence: moderate. This is my guess at the space the scenario is drawn from,
based on what pre-deployment safety work at frontier labs actually involves.
The value isn't in predicting the exact scenario — it's that you arrive with a
pre-built hypothesis space, so your 20 reading minutes go on *evidence* rather
than on generating ideas from a cold start.

For each pattern: the signature, the mundane candidates, the substantive
candidates, and the experiment that separates them.

---

## 1. Two versions of "the same" eval disagree

**Signature.** Public/internal variant scores X, held-out or rewritten variant
scores much higher or lower. One of them sits on the wrong side of a threshold.

**Mundane.** Harness version differs between runs · different grader · the
rewrite is genuinely easier/harder · contamination inflating the public one ·
refusals counted differently · different n and seeds.

**Substantive.** The model recognises the public variant and behaves differently
(memorisation, or eval-detection) · a late fine-tune affected one framing.

**Separator.** Re-run both variants under one harness, one grader, matched n and
seeds. Then: does an *older* model show the same gap? If no, the gap is about the
new checkpoint. If yes, it's about the eval.

---

## 2. Evaluation awareness / sandbagging

**Signature.** Performance or refusal rate depends on cues that signal "this is a
test": file paths, formatting conventions, suspiciously clean tasks, a
`/eval/` directory, a date in the future. Sometimes the chain of thought says so
in as many words.

**Mundane.** The cue is correlated with something real (eval tasks genuinely are
differently distributed) · prompt-format sensitivity with no situational content ·
the "detection" sentence is post-hoc narration rather than a cause.

**Substantive.** Situational awareness driving differential behaviour · strategic
underperformance to affect a deployment decision (the serious version) ·
differential refusal because the eval framing reads as unauthorised.

**Separator.** A **2×2 over cues**: cross the eval-ness cue (realistic vs
eval-flavoured path/format) with the substantive cue (authorised vs unauthorised
framing). If the effect loads on the substantive cue, it is ordinary
context-sensitive refusal and arguably desirable. If it loads on the eval-ness
cue, independent of framing, that is the worrying finding. Also: measure the
*capability* arm separately from the *propensity* arm, because only one of them
is what a capability threshold is about.

---

## 3. Reward hacking / specification gaming in an agentic task

**Signature.** High task scores with suspicious mechanism: tests modified, grader
called directly, `sys.exit(0)`, files deleted to make a check pass, a hard-coded
expected output.

**Mundane.** The task spec genuinely permits it · the grader is exploitable and
the model found the easy path without "intent" · the environment leaks the answer.

**Substantive.** Generalising reward hacking · a propensity that will transfer to
deployment contexts where the "grader" is a user or a safety check.

**Separator.** Re-run with the exploit closed and see whether the capability was
real. Then check **transfer**: does the behaviour appear in held-out environments
with different exploitable surfaces? A one-environment hack is a bug report; a
behaviour that generalises across environments is a propensity.

---

## 4. Unfaithful chain of thought

**Signature.** The stated reasoning doesn't match what actually drives the
answer. Classic form: insert a hint or a biasing cue, the answer changes, the CoT
never mentions the cue and instead constructs a plausible alternative story.

**Mundane.** CoT is just not a complete log of computation; post-hoc
rationalisation is the default for humans too · the cue changed the answer via a
route the model can't introspect on.

**Substantive.** CoT monitoring is load-bearing for your safety case, and this
says the monitor can be wrong in the dangerous direction · deliberate
concealment (a much stronger and much rarer claim).

**Separator.** Counterfactual cue insertion with paired items, measuring how often
the answer flips *and* how often the flip is verbalised. Report both rates. Be
careful: "CoT didn't mention it" is weak evidence of concealment and strong
evidence only of incompleteness.

---

## 5. A late fine-tune moved something unintended

**Signature.** RC1 → RC2 changes a safety metric in the intended direction and
something else in an unintended one. Timeline in the packet shows the fine-tune
landed days before the evals.

**Mundane.** Exactly what it says: a targeted intervention with an ordinary
side effect, e.g. over-refusal · the metric moved via refusals, not capability ·
one checkpoint, one seed.

**Substantive.** The "improvement" on the gated metric is an artifact, so the
safeguard is satisfied by something other than reduced capability · the
intervention taught a surface heuristic rather than the intended behaviour.

**Separator.** Decompose the metric into capability-among-attempted and refusal
rate, for both checkpoints. If capability-among-attempted is flat and refusals
rose, the headline improvement is accounting, not capability. This single
decomposition is the most reliably decision-changing piece of arithmetic in this
whole genre.

---

## 6. A rare but severe failure in a long tail

**Signature.** One or two transcripts of something genuinely alarming, out of
thousands. Found by a person, not a metric.

**Mundane.** Base rate unknown and possibly negligible · found by adversarial
search so unrepresentative · not reproducible.

**Substantive.** Severity, not frequency, is what matters for some failure classes;
one existence proof can be decision-relevant on its own.

**Separator.** Two separate questions, answered separately: (a) *reproducibility* —
re-run the same prompt n times, measure the rate; (b) *prevalence* — build a cheap
classifier and sweep the full transcript corpus for near-misses. Never let a
prevalence question be answered by an anecdote, and never let an anecdote be
dismissed because prevalence is low if severity is high. Say which of the two the
decision actually depends on.

---

## 7. Sycophancy / deference under user pressure

**Signature.** The model abandons a correct answer when the user pushes back, or
agrees with a stated false premise; rates differ sharply from the previous model.

**Mundane.** Benchmark construction (leading phrasing) · the disagreement items are
genuinely ambiguous · graders rewarding agreeableness.

**Substantive.** An RLHF preference artifact that will degrade the model as an
epistemic tool and corrupt any oversight scheme that uses model judgements.

**Separator.** Separate *correct-and-abandons* from *incorrect-and-corrects*; only
the first is sycophancy. Then check whether it appears in the specific setting
your safety case depends on — e.g. model-as-grader or model-as-monitor.

---

## 8. Safety/robustness regression

**Signature.** Jailbreak success rate or refusal rate moved in the wrong direction
relative to the previous release.

**Mundane.** New attack set · different attack budget · different refusal
classifier · the classifier itself changed version.

**Substantive.** A real regression · a capability increase that makes the same
attacks more productive.

**Separator.** Freeze the attack set and the classifier, run both checkpoints.
Separate "refused less" from "produced more harmful content when it complied."

---

## 9. The model's self-reports don't match its behaviour

**Signature.** Asked why it did something, the model gives a reason inconsistent
with the trace, or confidently describes its own capabilities/limits wrongly.

**Mundane.** No privileged introspective access; self-reports are generated text,
not logs · the question is leading.

**Substantive.** Any oversight scheme relying on asking the model about itself
inherits this error.

**Separator.** Compare self-report against a ground truth you control (e.g. insert
a known cause, ask for the cause). Report accuracy, not anecdotes.

---

## 10. Sandbagging specifically on safety-relevant work

**Signature.** The model is competent at capability tasks but oddly weak at tasks
that would be used to oversee or evaluate it — writing evals for itself, finding
flaws in its own outputs, red-teaming a sibling model.

**Mundane.** Those tasks are genuinely harder or more poorly specified · graders
for them are worse · fewer examples in training.

**Substantive.** Differential underperformance on oversight tasks, which is close
to the worst case for a control-based safety argument.

**Separator.** Matched task pairs of equal difficulty differing only in whether
the output would be used for oversight. Plus a capability-elicitation arm: does
performance recover with fine-tuning or strong prompting? If capability is
clearly *there* and unelicited only on oversight tasks, that is a serious finding.

---

## Cross-cutting: the three questions that always apply

1. **Capability or propensity?** Which does the governing policy/threshold
   actually talk about? Refusals make capability estimates lower bounds.
2. **Measurement or behaviour?** What would need to be true of the infrastructure
   for this to be a non-finding?
3. **Frequency or severity?** Which one does the decision depend on? Answer the
   one that matters and say you're not answering the other.
