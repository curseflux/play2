"""One worked solution for COURIER. ENCODED ON PURPOSE.

Do not read this until you have spent real time on practice/courier_policy.py
and run the grader. Reading a solution before you have failed at the problem
feels like learning and is not.

    python spoilers/courier_reference.py            # print it
    python grade.py courier --policy spoilers/courier_reference.py

It is one good answer, not the answer. It scores 16/16. Compare it to yours
and ask where the two differ in STRUCTURE, not in constants.
"""

import base64
import zlib

_B = (
    "eNqVVtuO2zYQffdXTNUXyStvvCm2RYP1AkY3bRZBsoAf8tCFYVASZQm1JZWiLuzXd2aoq530QsCWODxz5kLOUOm5yJWG"
    "s9DJYrE9/Lrb/uLDdrd7/vLehw8vu+ffXz778Gm7++0Zn9svL89Ph48+PL3fPsEG1rc/rX38v7/34e72Rx/e3q7pjYU/"
    "3C8WkYzhELmi9UEYHwJ8BsZ7twAcSupKZWz6NjFFrt2ghRUIxtCL8SxBkZ/S0Lh5UHaa4oi2cfrqiKPMtLNnKeqhiRof"
    "tcF1cXx1Wmfv84vpX+pBVJtOL415Xuoqy2Tk7OER1tbOxEsnjU7SYalOfIiUOOK/7v3QiapKTdQ8peVx0jtYn0WLCjqB"
    "N0zAwqMSgQ+7noimh7KQ5EinX6ThH1VxUCJKqxKpWO17WOEAWgMBWqij1Cz6X6OPn+2EQimTZug4pCVkuYbPeSbHTGjM"
    "rDa9o4VQoTyhP68XynsKPy/yOO7CRtSEJZAlZY2oB1mcKyggzS6YR6XOzYJ2SWiJHn63AacRqSaTcxyNMM9wpZKzhQL9"
    "L8j/os9p52A/ohYRkekg8yBGZnYfz7Q9bpbUgxsS2Yk/EHmXAXDwmFyKHjBoZntg8et6fx1HlyyXcIOtxTcI5+rX55bG"
    "wR+3kXRnhymSZapkBLU85WGKGJ03QkV4YOV/OWELm0OKnE451bI1tQJj11KOZlLwFm0jEodA8Wrr3skV9hLbjWCJ9i2i"
    "1HnRIdbUYphvRe0HQbsOQ6VDoDRzqd58a678U2nXtX0NwVRlHiyX8BY3DnsWitj8km14Xl8XbOERyJ8xuw2SNhRi1FIh"
    "E2Rp7XLoc9FXKqChJsAEGMVsA0otpQLRCAOxys+QiL8w/yU0EoTCX5BXGjcFzvKrW2HT2B5ETe3P2CfZ6GssGWqsY57W"
    "mMKwFHmVcN+0u5dw6xx2kEaF4qrD1RZYW2RtofUEWyGuajEZ+HdDavg2LmvrH2UakQ+U5585WeMe0z4O19DKVQOXslwe"
    "5ruqvLEoQvQlJPcUWyS85sA683pERvPDaDVHplLE0oapMK6byYUz9GKU2qtxWpPI+8DK84KsFN1aLrOuEESe0+SyR6D6"
    "5Ynrh93b1QaDRGUELon1GmZ6mPkWbH4ir/jvukNDVyPL8PAw66iTzZPHMN+CvOlRv9l0FG9QZdl/QeAbVecINAw0/wo8"
    "z83aWpy1xDOmj1Tm4Q1F21Dqzh0ty8bprBipRYsWe2uBNRkrcZbvoJSqltAkaZjIGsW4GlcK+6MCvCrgqhglWpCdVVsm"
    "jRkrJJKCjiB/S1GXw79ID3kPSle2Hh4lhokssiLTi/7pE2Wi/7jp9a4VVHpMtENo2dJXj6095yRj7Uw/0Ry8KhllJqgo"
    "bzJn8TcQdq6L"
)

SOURCE = zlib.decompress(base64.b64decode(_B)).decode()
exec(compile(SOURCE, "courier_reference", "exec"))

if __name__ == "__main__":
    print(SOURCE)
