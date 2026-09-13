# Research Taste Assessment — how to prepare

## Epistemic status, up front

I have not seen this test. Everything below is inferred from the assessment
blurb, the reasoning-transparency essay they point you at, and what AI safety
pre-deployment work actually looks like. Treat the **structure and habits** as
high confidence (they follow almost directly from what the blurb says it scores)
and the **specific scenario content** as a guess. The pattern library in
`02-pattern-library.md` is a bet that the scenario is drawn from a small space of
recognisable anomaly types; if it isn't, the generic moves still apply.

They say "there is nothing to study in advance." That is true about *facts*. It
is false about *process*. You cannot study the scenario, but you can absolutely
arrive with a reading procedure, a hypothesis-generation checklist, a prose
register, and a time plan already loaded. That is what this is.

## What the test is actually measuring

Read the blurb closely. It tells you the rubric almost explicitly:

> "how you build hypotheses from scattered pieces of information, how you
> prioritize when there are real tradeoffs, and how clearly you can explain your
> thinking" … "We are not scoring which hypothesis you land on. We care about
> clear, careful, well-prioritized reasoning, and about how openly you lay out
> your assumptions and uncertainties."

Four scored skills, then:

1. **Synthesis.** Can you fuse scattered, partly contradictory exhibits into a
   small number of candidate explanations — rather than summarising each exhibit
   in turn?
2. **Prioritisation under a real constraint.** Given limited time, compute, and
   human hours, what do you do *first*, and what do you deliberately drop?
3. **Calibration and transparency.** Do you say how confident you are and why,
   separate what you observed from what you inferred, and name what would change
   your mind?
4. **Writing.** Can a busy reader get your conclusion in 60 seconds and your
   reasoning in 10 minutes?

Note the two explicit anti-goals. They are not grading which hypothesis you
pick, so do not agonise over landing on the "right" one — agonise over the
*quality of the comparison between candidates*. And the situation is
deliberately ambiguous, so an answer that sounds certain is answering a
different, easier question than the one asked.

## The one-paragraph theory of the whole thing

You are being asked to simulate a competent safety researcher who has been
handed a messy folder and has 72 hours before a decision gets made without them.
The deliverable is not "what is going on." It is **"here is what I think is
going on, here is how confident I am, here is the cheapest thing that would tell
us, here is what I recommend given we may not find out in time, and here is
where I could be wrong."** Everything in the sections below is in service of
producing that document fast.

## The five habits that do most of the work

### 1. Find the decision before you form an opinion

Before analysing anything, answer on scratch paper: **What decision is this
feeding? Who makes it? By when? What are the options?** Analysis that does not
bear on a live decision is the most common way strong writers waste 80 minutes.
If the scenario has a go/no-go meeting in 72 hours, every sentence you write
should be traceable to "this changes the go/no-go" or "this is why I deprioritised
it."

### 2. Build a provenance table before you build a theory

This is the single highest-leverage mechanical move, and almost nobody does it
under time pressure. Take every number in the packet and tabulate it by:

| metric | checkpoint | eval variant | harness/scaffold version | grader | n | seeds | date |
|---|---|---|---|---|---|---|---|

Anomalies in realistic packets are *planted in this table*. Two numbers that are
being compared will differ in a column nobody mentioned. Doing this takes six
minutes and routinely finds the thing the scenario is really testing. It also
protects you from the failure mode of comparing two numbers that were never
comparable.

### 3. Run the boring-explanations checklist before the interesting one

See `01-boring-first.md`. The discriminating feature of a strong answer is that
it takes the alarming hypothesis seriously *and* rules out the mundane ones
first, by name, with a test for each. The two symmetric ways to fail:

- **Credulous**: "The model is scheming." (Skipped the harness diff.)
- **Dismissive**: "This is probably just an eval bug." (Didn't check, and didn't
  notice the bug wouldn't explain the direction of the effect.)

The move that scores is: *these are the mundane candidates, here is the cheapest
test that separates them from the substantive ones, here is what I'd conclude
under each outcome.*

### 4. Do the arithmetic the packet invites

Realistic packets contain numbers that are meant to be combined. Refusal rates
next to accuracy. A previous model's score on both eval variants. Two
checkpoints with both metrics. **Five minutes with the numbers usually beats
forty minutes of prose.** Specifically, always check:

- Are refusals / abstentions / timeouts being scored as failures? Recompute the
  metric over *attempted* items only. This one transformation reframes a large
  fraction of apparent capability changes.
- Is there a control arm you can use as a ruler? If an *older* model scores the
  same on both eval variants, the variants are comparable and the gap is about
  the new model — a much stronger inference than anything you can argue in prose.
- Is the gap bigger than sampling noise? Binomial SE is `sqrt(p(1-p)/n)`; at
  p≈0.5, n=150 that's ~4 points, so a 95% CI is roughly ±8. A 23-point gap is
  real; a 5-point gap is not.

### 5. Separate capability from propensity, and measurement from behaviour

Most frontier-model anomalies decompose along these two axes, and most confused
analyses are confused because they collapsed one:

- **Capability** = what the model *can* do with maximal elicitation.
  **Propensity** = what it *does* by default.
  A threshold written about capability is not satisfied by a drop in propensity.
  Refusals make a capability estimate a *lower bound*.
- **Measurement artifact** = the number moved. **Behavioural change** = the model
  moved. Never report a behavioural claim without saying how you excluded the
  measurement one.

## The answer structure

They give you a template and you should follow theirs. But almost any sensible
template is a permutation of this, so practise writing these seven blocks:

1. **Summary of key takeaways** — 5–7 bullets, each one a claim with a
   confidence attached, each one pointing at the section that argues it. *Write
   this last, put it first.*
2. **What I think is going on** — 3–5 ranked hypotheses with explicit credences,
   each with the evidence for it, the evidence against, and what it predicts that
   the others don't. Include at least one measurement-artifact hypothesis and one
   substantive one.
3. **What I'd do next, prioritised** — numbered, each with a cost in the
   scenario's own units (eval runs, grader hours, days), each with "what outcome
   would change what conclusion." State the total and show it fits the budget.
4. **What I'm deliberately not doing** — and why. Usually because it can't change
   the decision (low value of information), or can't finish in time, or is owned
   by someone else. This section is short and scores disproportionately.
5. **Recommendation** — an actual call, conditional if need be: "recommend X;
   if test A comes back > 55%, switch to Y." Name the asymmetry of the two error
   directions.
6. **Assumptions** — facts you needed that the packet didn't give you, stated as
   assumptions rather than smuggled in as premises.
7. **What would change my mind** — per hypothesis, the concrete observation that
   would move you, ideally with the direction and rough magnitude.

## The 100-minute plan

Pre-commit to this. The blurb warns that most people feel the clock, and the
failure mode is a beautiful section 2 with sections 4–7 empty.

| time | minutes | what |
|---|---|---|
| 0–08 | 8 | Read fast, no notes. Get the shape. Find the decision, the deadline, the budget. |
| 08–22 | 14 | Second pass with a pen. Build the provenance table. Note every number. Mark confounders. |
| 22–30 | 8 | Close the packet. Brain-dump hypotheses — measurement bucket and substantive bucket. Do the arithmetic. |
| 30–38 | 8 | **Skeleton pass.** Write one or two sentences into *every* required section, including the recommendation. You now have a complete, gradeable answer. |
| 38–75 | 37 | Deepen in priority order: hypotheses → plan → recommendation. |
| 75–88 | 13 | Write the summary. Write assumptions and what-would-change-my-mind. |
| 88–96 | 8 | Re-read for calibration words and unsupported claims. Add confidence markers. Cut padding. |
| 96–100 | 4 | Buffer. Something will go wrong. |

The skeleton pass at minute 30 is the single most important line in this table.
It converts "ran out of time" from a catastrophe into a quality ceiling.

## Register: how the prose should sound

From the reasoning-transparency essay, compressed into things you can actually
do while typing:

- **Attach a confidence to every substantive claim.** Use a consistent ladder
  and say what it means once: *almost certain (>95%) / likely (~75%) / plausible
  (~40–60%) / unlikely (~15%) / very unlikely (<5%)*. Use a number when the claim
  is load-bearing; use a word when it isn't.
- **Say what kind of support you have.** The essay's list is long but the useful
  compression for a timed test is four labels: *stated in the packet* /
  *arithmetic I did on packet numbers* / *inference from the packet* / *my prior
  from outside the packet*. Tag the load-bearing claims.
- **Flag what is load-bearing.** "My recommendation rests almost entirely on the
  refusal-adjusted arithmetic in §2.1; if that is wrong, everything downstream
  changes." Graders are explicitly looking for this.
- **Say when you haven't checked.** "Supposedly (I haven't verified from the
  packet)…" is a phrase the essay singles out as good practice and which
  essentially never appears in weak answers.
- **Name your priors and any bias.** "I came in expecting eval-awareness because
  it's the failure mode I've read most about, which probably inflates my credence
  here." This costs one sentence and is exactly the transparency being scored.
- **Distinguish observation from inference in the sentence itself.** "Refusals
  rose from 9% to 24% (observed). I read this as the safety fine-tune
  over-generalising (inference, ~60%)."

Two anti-patterns:

- **False precision.** "I am 37% confident" invites the reader to ask where the
  7 came from. Round to something you can defend: 10/15/25/40/60/75/90.
- **Hedging as a substitute for a view.** "More research is needed" is not a
  finding. Every uncertainty should come with either a test that would resolve
  it or a decision that is robust to it.

## How to practise in the time you have

Do not read more AI safety papers. Do these, in this order.

1. **Read the worked example in `03-worked-example.md` in two sittings.** First
   read only the scenario, set a 100-minute timer, and actually write an answer.
   Only then read the model answer and the commentary. Reading the answer first
   destroys most of the value.
2. **Then do the three extra scenarios in `04-practice-scenarios.md` as
   40-minute drills**, answering only sections 2, 3 and 5 (hypotheses, plan,
   recommendation). You are drilling hypothesis generation and prioritisation,
   which is where the marks are.
3. **Grade yourself against `05-rubric.md`.** Be harsh, particularly on "did I
   cost the plan" and "did I name what would change my mind."
4. **Re-read the reasoning-transparency essay once, the day before**, with one
   question in mind: *which of these moves can I do in one sentence under time
   pressure?* Build a short list and keep it next to you during the test.
5. **Write out your confidence ladder on paper before the test starts** so you
   are not inventing vocabulary at minute 70.

## Things to do in the first two minutes of the real test

- Find and read the template in full. Count the required sections. Note any
  word limits.
- Find the glossary and check it's searchable. Note that it exists so you don't
  waste time on a term you can look up.
- Write the section headers into your answer document immediately, so the
  skeleton pass is just filling gaps.
- Write the deadline and the budget at the top of your scratch notes.
