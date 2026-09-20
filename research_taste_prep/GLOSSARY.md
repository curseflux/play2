# Small glossary

These definitions are enough for this pack. No specialized background is assumed.

- **Checkpoint:** a particular saved version of a model.
- **Scaffold / harness:** software around a model that supplies prompts, tool access, retries, and scoring. Changing it can change results without changing model weights.
- **Episode:** one complete trial of a task, potentially containing several tool calls or retries.
- **Task family:** tasks sharing an underlying structure. Many near-duplicates may provide less independent evidence than the same number of unrelated tasks.
- **Confound:** a second factor that changes with the factor you want to study, preventing a clean attribution.
- **Factorial comparison:** testing combinations of factors, such as two labels and two instruction variants, to separate their effects and possible interactions.
- **Held-out task:** a task not used to tune the system being evaluated. "Held out" only helps if the separation was actually maintained.
- **Evaluation leakage / contamination:** test content or solutions becoming available during training, tuning, retrieval, or evaluation in a way that undermines the intended test. These routes are different and should not be assumed interchangeable.
- **Blinded scoring:** reviewers do not know which system or condition produced an output while judging it.
- **Ground truth:** the best available reference for whether an event occurred. In these cases, human labels can also be fallible or disputed.
- **Monitor:** a detector that inspects behavior and raises alerts. Its alerts are measurements, not the behavior itself.
- **Sensitivity:** among actual positive events in a stated population, the fraction detected. **False-positive rate:** among actual negative events, the fraction incorrectly flagged. **Precision:** among flags, the fraction that are true positives.
- **Distribution shift:** the tasks or conditions at deployment differ from those tested.
- **Evaluation awareness:** behavior depending on cues that a task is an evaluation. It need not imply a persistent hidden objective.
- **Strategic concealment:** for these exercises, behavior that selectively hides a relevant action or failure from oversight to achieve another objective. Observing an omission alone does not establish this explanation.
- **Sandbox:** an environment with limited permissions and isolated resources. Its protection depends on the controls actually enforced.
- **Read-only / write access:** permission to inspect information versus permission to modify it or cause an external action.
- **Shadow evaluation:** the system produces proposed actions that are recorded but not executed on real systems.
- **Canary test:** a deliberately constructed check designed to reveal whether a specific failure or control is working.
- **Precommitment / preregistration:** recording the test and decision criteria before seeing its results, to reduce opportunistic reinterpretation.
- **Value of information:** how much obtaining evidence could improve a decision, considering the chance it changes the action and the cost of obtaining it.
