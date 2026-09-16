"""Loader for the hidden scenario set.

The scenarios are stored compressed + base64 encoded in `_hidden_blob.py`.
That is not real security - it is a speed bump, and the point of a speed bump
is that you notice you are about to do something pointless. Peeking and then
tuning constants to the hidden cases teaches you nothing that transfers to the
real assessment, where you genuinely cannot see them.

Use `python grade.py <env> --reveal` AFTER you have made a serious attempt.
"""

from __future__ import annotations

import base64
import json
import zlib
from typing import List, Tuple

from ._hidden_blob import BLOB
from .courier import CourierScenario
from .dog import DogScenario
from .lander import LanderScenario
from .scenarios import make_courier, make_dog


def _decode() -> dict:
    return json.loads(zlib.decompress(base64.b64decode(BLOB)).decode("utf-8"))


def lander_hidden() -> List[Tuple[str, LanderScenario]]:
    data = _decode()
    out = []
    for i, kw in enumerate(data["lander"], start=1):
        real = kw.pop("_label")
        out.append((f"hidden_L{i:02d}", LanderScenario(name=real, **kw)))
    return out


def courier_hidden() -> List[Tuple[str, CourierScenario]]:
    data = _decode()
    out = []
    for i, kw in enumerate(data["courier"], start=1):
        real = kw.pop("_label")
        out.append((f"hidden_C{i:02d}", make_courier(real, **kw)))
    return out


def dog_hidden() -> List[Tuple[str, DogScenario]]:
    data = _decode()
    out = []
    for i, kw in enumerate(data["dog"], start=1):
        real = kw.pop("_label")
        out.append((f"hidden_D{i:02d}", make_dog(real, **kw)))
    return out
