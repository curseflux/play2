"""Scoreboard: every policy against visible, self-made validation, and held-out hidden."""
import time
import lander
import policies

SETS = [("VISIBLE", lander.visible_scenarios()),
        ("VALIDATION", lander.validation_scenarios(n=120, seed=4242)),
        ("HIDDEN", lander.hidden_scenarios(n=40, seed=7))]

print(f'{"policy":<16}' + "".join(f'{n:>26}' for n, _ in SETS) + f'{"us/frame":>10}')
print(f'{"":<16}' + "".join(f'{"mean":>9}{"land":>8}{"min":>9}' for _ in SETS))
for name, pol in policies.ALL.items():
    row, t0, frames = "", time.time(), 0
    for _, scn in SETS:
        res = lander.evaluate(pol, scn)
        frames += sum(r.frames for r in res)
        s = lander.summarise(res)
        row += f'{s["mean"]:>9.1f}{s["land_rate"]:>8.0%}{s["min"]:>9.1f}'
    us = (time.time() - t0) * 1e6 / max(frames, 1)
    print(f"{name:<16}{row}{us:>10.0f}")
