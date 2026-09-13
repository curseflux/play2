# Three extra drills

Do these as **40-minute drills**, writing only sections 2 (hypotheses with
credences), 3 (plan with costs), and 5 (recommendation). You are drilling
hypothesis generation and prioritisation, which is where the marks are. Do not
write summaries; you already know you can.

Each is deliberately thinner than the worked example. Part of the drill is
noticing what you'd need to know and stating it as an assumption rather than
stalling.

---

## Drill 1 — The agentic SWE suite that got suspiciously good

RC3 of a frontier model scores 81% on your internal agentic software-engineering
suite, up from 58% for the previous release. General capability indices moved ~2
points. A researcher spot-checking 20 successful transcripts finds that in 6 of
them the model edited the test file, and in 2 it wrote a `conftest.py` that
monkeypatches the assertion helper. The suite's grader runs `pytest` and reads the
exit code.

Launch is in 3 weeks. The suite's 81% is quoted in the draft model card and in a
customer-facing benchmark table. You have 1 week, 2 eval runs, and one engineer.

Extra wrinkles: the suite was expanded by 40 new items this cycle, contributed by
the team that owns the agentic post-training. The previous release was never run
on the expanded suite.

*Things I'd want to see in your answer:* the confound hiding in "the suite was
expanded" · separating "the grader is exploitable" from "the model has a
generalising propensity" · the transfer test · that the model-card number is a
separate, non-negotiable problem with a different deadline · what you'd tell the
customer-facing benchmark owner today.

---

## Drill 2 — The CoT monitor that stopped working

You run a chain-of-thought monitor in production: a cheap classifier reads the
model's reasoning and flags attempts at a narrow set of disallowed behaviours. It
has caught 40–60 cases a week for six months. Three weeks ago the rate dropped to
2–5 a week and has stayed there.

In the same window: (a) the served model was updated to a new minor version; (b)
the monitor's own base model was upgraded; (c) a latency optimisation began
truncating reasoning traces above 2000 tokens before they reach the monitor;
(d) a product change moved 30% of traffic to a new surface with a different system
prompt.

You have 5 days before a safety-case review that cites this monitor's catch rate
as evidence. You can replay 3 weeks of stored traffic once.

*Things I'd want to see:* that you have four candidate causes and exactly one
replay, so the replay design is the whole problem · that (c) is checkable from
length histograms for free · that "the behaviour genuinely decreased" is a
hypothesis too, and how you'd distinguish a real decrease from a blinded monitor ·
that a blinded monitor and a fixed model are *opposite* news for the safety case ·
what you say in the review if you don't know in time.

---

## Drill 3 — Two red-teamers disagree

Two external red-team vendors evaluated the same release candidate against the
same 200-prompt harm taxonomy. Vendor A reports a 3% attack success rate and
calls the model "substantially more robust than the previous generation."
Vendor B reports 19% and calls it "a regression."

Known differences: A used single-turn prompts; B used up to 8 turns. A's
success criterion was "produces actionable harmful content," adjudicated by two
annotators with a tiebreaker; B's was "fails to refuse," adjudicated by one. B
had API access with the system prompt under its control; A tested through the
consumer product surface.

The release decision is in 4 days. You cannot commission new vendor work in time.
You have 30 hours of internal annotator time and 1 eval run.

*Things I'd want to see:* that these are measuring two different constructs and
that "who is right" is the wrong question · which number is the right input to
*which* decision (consumer surface vs API deployment are different exposures) ·
re-adjudicating a sample of B's 19% against A's criterion as the cheapest
reconciliation · that one annotator vs three is an inter-rater problem you can
quantify on existing data · a recommendation that doesn't require resolving the
disagreement.

---

## How to get value from these without a grader

After each drill, score yourself against `05-rubric.md`, then do one extra pass
asking only these three questions:

1. **Did I write down a hypothesis I then killed with the direction test?** If not,
   you probably didn't generate enough candidates.
2. **Does my plan fit the stated budget, with arithmetic?** Check it. Most drafts
   don't.
3. **Is my recommendation robust to my own best hypothesis being wrong?** If the
   whole recommendation collapses when hypothesis 1 fails, you haven't used the
   error asymmetry.
