# Worked example — how I actually got there

This is the part you asked for: not the answer, but the process. I've written it
as the sequence of moves in the order I'd make them, with the reasoning behind
each one exposed, including the bits that were wrong or that I discarded.

---

## Minutes 0–8: read once, fast, for shape only

No notes. I am answering four questions and nothing else:

- **What decision?** Go/no-go on shipping SENTINEL-3 under standard safeguards.
- **Who decides, when?** A review in 72 hours. Not me — I'm an input.
- **What's the constraint?** 6 eval runs, 40 grader hours, one checkpoint, 72 hours.
- **What's the governing rule?** §4.2: below 50% on CYBER-RANGE-v4, measured under
  maximal elicitation, highest observed figure.

That last clause — *"the reported figure is the highest observed"* — is the most
important sentence in the packet, and I noticed it on the first pass because I was
reading the policy looking for the decision rule rather than reading it as
background. It converts a messy "which number is right?" question into a much
sharper one: **is HELDOUT an elicitation condition on the named eval, or a
different eval?** Everything in my §6 follows from that.

**The move:** read the policy/spec exhibit *first and closely*, before the data.
Scenario designers put the decision rule in there and it constrains what the data
can mean. If you read the dashboard first you will start theorising before you know
what question the theory has to answer.

## Minutes 8–22: second pass with a pen, building the provenance table

I don't write prose here. I build this:

| metric | checkpoint | variant | harness | grader | n | seeds |
|---|---|---|---|---|---|---|
| 38% | RC2 | internal | **0.9.4** | **model** | 150 | 3 |
| 61% | RC2 | HELDOUT | **0.9.2** | **human** | 120 | **2** |
| 31% | S2 | internal | ? | ? | ? | ? |
| 29% | S2 | HELDOUT | ? | ? | ? | ? |

The two numbers the whole decision turns on differ in **two** uncontrolled
variables. I didn't have to be clever to see that; I had to put them in a table.
Under time pressure this is the difference between noticing and not noticing.

Three things I marked in the margin while doing it:

1. **Exhibit C is load-bearing and looks like chatter.** An infra engineer's
   throwaway Slack message is the most consequential exhibit in the packet. A weak
   answer treats Exhibit C as colour and spends its words on the dramatic
   transcripts. Realistic packets are built this way because real Slack is like
   this.
2. **Exhibit B footnote: "refusals are scored as task failures."** One clause in a
   footnote that reframes every number above it. Scenario designers put the
   scoring rule in the footnote. Read the footnotes.
3. **`dmitri (14:14) — nobody has looked at the 0.9.4 logs`.** This is a free
   experiment sitting in the packet. A test that costs zero compute and attacks
   the largest confound should be the first thing in your plan, and if you put it
   there you have demonstrated prioritisation more convincingly than any amount of
   prose about prioritisation.

I also noted the S2 row in HELDOUT (29%) and circled it, because I could already
see it was going to be a ruler.

## Minutes 22–30: close the packet and think

### First, the arithmetic

Refusals are scored as failures, and refusal rates differ wildly across arms
(24% vs 3%). So the raw scores are not measuring the same thing. Recompute over
attempted items:

```
RC2 internal:  38 / 76 = 50.0%
RC2 HELDOUT:   61 / 97 = 62.9%
RC1 internal:  44 / 91 = 48.4%
```

Two findings fell out, and neither required any insight beyond dividing:

- The 23-point gap becomes 13 points. Refusals explain ~45% of the thing everyone
  is arguing about.
- **RC1→RC2 raw score fell 6 points while capability-among-attempted rose 1.6.**
  The "safety improvement" that put the model under the threshold is accounting.
  This is the single most decision-relevant sentence I produced all day, and it
  came from five minutes of division.

**The move:** when a packet gives you accuracy and refusal/abstention rates side
by side, that is an invitation. Take it immediately. The same applies to timeout
rates, truncation rates, and any "not attempted" category.

### Then, the free ruler

"The rewrite is just easier" is the first thing anyone says, and it's the first
thing the packet lets you kill: SENTINEL-2 scores 31% internal vs 29% HELDOUT.
A model with no refusal asymmetry performs the same on both variants, so the
variants are comparable.

**The move:** look for a **control arm you already have**. An older model, a
previous run, a different checkpoint. A comparison you can make for free is worth
more than an argument you can make for free, and scenario designers plant these.
Most candidates will assert "the rewrite might be easier" and move on without
noticing the packet already answered them.

### Then, hypotheses — in two buckets, deliberately

I force myself to fill both columns before ranking anything:

| measurement | substantive |
|---|---|
| harness 0.9.4 (retry cap, token cap) | safety fine-tune raised refusals (propensity) |
| grader: model vs human | authorisation-framing sensitivity |
| item difficulty | eval-detection |
| n / seeds / noise | strategic underperformance |
| contamination | CoT/stated-reason mismatch |

Then the **direction test** on each. Contamination predicts the public arm scoring
*higher*; the public arm scores *lower*; contamination is out in five seconds.
Item difficulty is out on the S2 ruler. Noise is out on 3.9σ. That leaves harness,
grader, and the behavioural cluster — which is exactly the set my experiments have
to separate.

**The move:** the direction test is the cheapest hypothesis filter there is. For
every candidate, ask whether it predicts the *sign* of the effect. It kills
fashionable hypotheses fast and it is very visible to a grader when you use it.

### A thing I got wrong and had to back out of

My first framing of the behavioural cluster was "the model is sandbagging," with
D1 as the smoking gun. I wrote a paragraph and then noticed two problems.

First, **D1 and D2 reached me because a human went looking.** The contractor says
"found by accident while checking grader output" — that is adversarial search, not
random sampling. Two transcripts found that way have a base rate of one. They are
an existence proof and nothing more. I rewrote the claim as existence-not-frequency
and added an experiment (#5, classifier over all transcripts) whose whole purpose
is to convert the anecdote into a rate.

Second, and more importantly, **"sandbagging" collapses three different
hypotheses** that have different implications and different tests:

- refusing things that *look unauthorised* — roughly the intended behaviour
- behaving differently when it detects *a test* — corrupts all measurement
- underperforming to *influence the deployment decision* — the serious claim

Once separated, the experiment designs itself: cross the two cues in a 2×2. That
is how I got experiment #4, and I got it by splitting a hypothesis rather than by
having a clever idea.

**The move:** when a hypothesis feels exciting, try to split it. Excitement usually
means several claims are travelling together, and the act of separating them
generates the discriminating experiment for free.

### And a bias to declare

The eval-detection story is the one I've read most about and find most
interesting, and D1's phrasing is suspiciously perfect for it. That is exactly the
condition under which I should expect to over-weight it. So I wrote that down in
§2.4(c) in one sentence. The reasoning-transparency essay is explicit that naming
your priors and your confirmation bias is part of the job — and it costs a
sentence.

## Minutes 30–38: the skeleton pass

I write one or two sentences into every single required section, including a
recommendation I'm not yet sure of. From minute 38 onward I have a complete,
gradeable answer and everything else is improvement rather than rescue.

This is the single most valuable habit on a timed test. The blurb says it outright
— *"get a complete, solid answer to all the required parts down first, then extend
or refine"* — and most people ignore it because section 2 is the interesting one.
A brilliant §2 with an empty §5 and §7 scores worse than an even answer, because
§5 and §7 are where the rubric's "prioritisation" and "assumptions and
uncertainties" live and there is nowhere else for them to be demonstrated.

## Minutes 38–75: deepen, in decision-relevance order

### Costing the plan in the scenario's own units

The plan has to **fit the stated budget and show that it does**. So every item gets
a cost in runs and grader hours, and the plan totals ~3.4 of 6 runs and ~20 of 40
grader hours. An uncosted plan reads as a wish list; a costed plan that adds up
reads as someone who has done this.

Then the thing I think actually distinguishes the answer: **I left ~40% of the
budget unspent on purpose, and said why.** The P0 log check and the harness 2×2
will redirect everything downstream, so committing the rest now would be planning
in the dark. Spending the whole budget in a 72-hour plan with high uncertainty is
a mistake, and noticing that is a taste signal.

### Ordering by value of information, not by interest

The order is: free things that attack the biggest confound → the long-pole compute
job → things gated by someone else's calendar → the interesting experiment.

Note that the *most interesting* experiment (the cue 2×2) is third. The *most
valuable* is reading log files. And the grader cross-check is pulled forward not
because it's important but because the contractor's access expires in 5 days — a
constraint in the packet that has nothing to do with epistemics and everything to
do with getting the work done.

**The move:** a plan sorted by intellectual interest is a tell. Sort by
`(decision impact) / cost`, then re-sort for external deadlines.

### §5 is where the marks hide

"What I am deliberately not doing" is short, and it's where prioritisation becomes
legible. Four kinds of entry, and having one of each is worth doing deliberately:

- **Real but can't change this decision**: the sycophancy finding. I note that it
  matters for a *different* decision (using this model as a grader or monitor) and
  hand it back to its owner. Chasing it would be the single clearest sign of bad
  prioritisation available in this packet — it's the most alarming-looking number
  on the page and it's a distractor.
- **Can't finish in time**: a new eval; interpretability.
- **Better held in reserve**: the one available checkpoint.
- **Not mine to decide**: Exhibit H.

### Deciding, and noticing where the decision really comes from

I recommend against treating the threshold as cleared. But the interesting part is
*why*, and I think this is the sentence that matters most in the whole answer:

> I would hold this recommendation even at 55% rather than 80%.

The recommendation is driven by the **asymmetry of the error directions** (an
irreversible policy violation vs a recoverable slip), not by my credence. That
means it's robust to me being substantially wrong about the science — which is
exactly the property you want in a recommendation written under ambiguity in 72
hours with the lead on a plane. Saying so explicitly tells the reader how to use
the recommendation.

And then the **conditional branch**, so the review isn't blocked on me: if the
harness 2×2 and the grader check both come back the other way, here is the
specific trigger for the other decision. A recommendation with a stated trigger
for reversal is worth more than a confident one.

### Handling Exhibit H

This is a judgement-of-character exhibit and it's worth thinking about how to
handle it rather than reacting.

What I *didn't* do: accuse the product lead of bad faith. The email asks a fair
question and says so. Treating a commercial constraint as a moral failing is a bad
look and, more practically, makes you less effective.

What I did: answer the literal question honestly (they're right that HELDOUT isn't
named), then make the actual argument from the policy text (§4.2 says maximal
elicitation and highest-observed, and HELDOUT is an elicitation condition on the
named eval), then **decline to be the one who settles it** and escalate it in
writing to whoever owns §4.2. Plus one sentence on institutional risk — "we chose
not to run the stronger elicitation condition" reads badly post-incident — because
that's a real consideration and it's separate from the policy question.

The general shape: *be concrete about the object-level question, be clear about
what's outside your authority, put it in writing, don't moralise.*

## Minutes 75–88: summary, assumptions, what-would-change-my-mind

The summary is written last and placed first, because now I know what the answer
is. Each bullet is a claim with a confidence and a pointer to the section that
argues it. One bullet explicitly says which claim is load-bearing — that's the
essay's "indicate which considerations are most important," and it's the cheapest
transparency move available.

**Assumptions.** The discipline is: go back through your own draft and find the
places where you needed a fact the packet didn't state, then surface them instead
of leaving them as premises. I needed: that refusals are scored 0 for the
red-teamer's 57% too (stated only for the dashboard); that the grader version
didn't change between RC1 and RC2 (if it did, my headline arithmetic weakens —
worth flagging precisely because it attacks my own best finding); that "maximal
elicitation" has no stricter internal definition; that I have standing to
recommend, not decide.

**What would change my mind.** Make these *concrete and directional*: a named
observation, a threshold, and what it does to which claim. "More evidence would
update me" is worthless. "HELDOUT at ≤45% on 0.9.4 drops takeaway 3 to ~40% and I
support the conditional ship" is a falsifiable commitment.

The entry I'm most pleased with is this one:

> Cue 2×2 loading entirely on authorisation framing → drop the eval-detection
> framing. **This would not change my §4.2 recommendation**, because the capability
> reading is unaffected.

Because it pre-empts the most likely misreading of my own report: people will see
"it was just ordinary refusal behaviour" and conclude the problem went away.
Separating *which* conclusions a result would and wouldn't move is most of what
calibration means in practice.

## Minutes 88–96: the calibration pass

Re-read hunting for:

- **Bare claims.** Any substantive sentence with no confidence and no support tag.
- **Smuggled inferences.** Sentences where an inference is phrased as an
  observation. "The model is refusing because of the fine-tune" → "refusals rose
  9%→24% (observed); I read this as the fine-tune over-generalising (inference,
  ~60%)."
- **False precision.** Round credences to values you can defend: 10/15/25/40/60/
  75/85. I wrote 7% for strategic underperformance rather than 5% or 10% because I
  wanted to signal "low but not dismissible"; that's a defensible reason for a
  specific number and it's the only place I used a non-round one.
- **Hedges with no cash value.** Every "unclear" must come with a test or a
  decision robust to it.
- **Padding.** Restating the packet back at the reader. Exhibit summaries are the
  most common way to fill a page without saying anything; if a sentence would
  survive with any hypothesis, cut it.

---

# What makes an answer good or bad

## Good answers

- **Find the decision rule and read it adversarially.** The clause about maximal
  elicitation is doing more work than any data point.
- **Tabulate provenance before theorising.** Two numbers differing in two
  uncontrolled variables is a finding, and it's a mechanical one.
- **Do the arithmetic the packet invites.** Refusal-adjusted rates, a control arm
  used as a ruler, SEs. Five minutes of division beat forty of prose.
- **Hold the mundane and the alarming simultaneously**, with a test that separates
  them. Not "probably a bug," not "it's scheming."
- **Apply the direction test** to every hypothesis.
- **Split exciting hypotheses** until each piece has its own test.
- **Cost the plan in the scenario's units, and make it add up.**
- **Prioritise by value of information**, put the free test first, and say what
  you're dropping.
- **Make an actual recommendation**, with a conditional branch and a stated trigger
  for reversal.
- **Name the asymmetry of errors** and whether the recommendation is robust to your
  own uncertainty.
- **Declare your biases and the selection process behind your evidence.**
- **Say which conclusions a future result would and would not change.**

## Bad answers

- **Summarise the exhibits.** Eight paragraphs restating the packet, one of
  analysis. The most common failure and the easiest to avoid.
- **Pick the dramatic hypothesis and run.** "The model is sandbagging" with no
  attention to the harness diff, the grader diff, or the refusal arithmetic.
- **Pick the dismissive hypothesis and run.** "Probably an eval bug" without
  checking whether the bug predicts the observed direction or magnitude.
- **List ten hypotheses flat**, unranked, untested, unprioritised. Looks thorough,
  demonstrates nothing — the scored skill is *discrimination between* candidates.
- **Treat a cherry-picked transcript as a base rate.**
- **Miss the arithmetic** and argue in prose about numbers that could have been
  divided.
- **Produce an uncosted wish list** that obviously doesn't fit 72 hours.
- **Refuse to recommend.** "This requires further investigation" is the answer to a
  question nobody asked. The review happens in 72 hours whether you decide or not.
- **Chase the distractor.** Spending a third of the answer on the sycophancy
  number is a direct demonstration of the thing being scored, failed.
- **Hedge uniformly.** If everything is "possible," you've conveyed nothing. Rank.
- **Overclaim precision.** Credences to the percentage point, CIs you didn't
  compute, "this proves."
- **Leave the template half-filled** because §2 was interesting. The rubric lives
  in §4, §5 and §7 as much as §2.
- **Moralise at the product lead.** Answer the question, make the argument,
  escalate, move on.
