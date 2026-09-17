"""Rebuild packaged courses. Authoring tool; contains access to witnesses."""
import base64
import json
import pathlib
import sys
import zlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from _exam.factory import PRIVATE, PUBLIC, build


def encode(value):
    return base64.b64encode(zlib.compress(json.dumps(value).encode(), 9)).decode()


def main():
    visible, hidden, witnesses = [], [], {}
    for name, seed, family, description in PUBLIC:
        case, actions = build(name, seed, family)
        case["description"] = description
        visible.append(case)
        witnesses[name] = actions
    for name, seed, family in PRIVATE:
        case, actions = build(name, seed, family)
        hidden.append(case)
        witnesses[name] = actions
    (ROOT / "cases").mkdir(exist_ok=True)
    (ROOT / "cases" / "visible.json").write_text(json.dumps(visible, indent=2) + "\n", encoding="utf-8")
    (ROOT / "_exam" / "hidden.dat").write_text(encode(hidden), encoding="ascii")
    (ROOT / "_exam" / "witnesses.dat").write_text(encode(witnesses), encoding="ascii")
    print(f"Built {len(visible)} visible and {len(hidden)} hidden courses, with verified witnesses.")


if __name__ == "__main__":
    main()
