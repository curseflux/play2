"""One worked solution for DOG. ENCODED ON PURPOSE.

Do not read this until you have spent real time on practice/dog_policy.py and
run the grader.

    python3 spoilers/dog_reference.py                          # print it
    python3 grade.py dog --policy spoilers/dog_reference.py

Originally 18/18 and 87% on the old courses. On the harder suite: 13/25 and
100/200 stress cases (seed 1). See practice/DOG_CHALLENGES.md. This remains a
learning example, not a complete solution to the revised task.
"""

import base64
import zlib

_B = (
    "eNqNVm1v2zYQ/q5fcdMwTGrl1Mm6YgmiAN3abgPWfSg2YEAQCJRES0RkUSFpx9qw/747knqz8mEGnFjHu4d3D587KgzD"
    "L3zHFW8LfgO6lsps8I/4W7agZNPIgwG5g1yaGlhhhGx1ArqQipfADJiaQyc6DoWSWou2ugjDMBD7DnFgz0wdBJ/f/5X9"
    "ksDnX3+nf799fP8BUnj7LoEfEngbfPj4458/30ApCoPmf/4NgqDkO8gMUxU3kcx1fBMAfmgXjS5ouQ/tQ/hgF8QOWmnc"
    "unOlj+LmoFrnXXDRYGrhA7yBKweGQDbgfutAGplALch6H1asyxqJ3q9deCmrTLFSHHDHZHCoBTps1g4WjUqJGokAtYjH"
    "TTHRhreR3TeGO7icsn0a87l8GI0GXqewvfjue3gFURQ9LTJ7mtKwO8SYjImDWel70UZ7dopMgtXFVF48kOsPeMauJ3FO"
    "7orLq+3I3dxvoFB3rHUEnmyG+KNmzS57nog6vUzqImvM2EuFCvDiEa2JLP4biGz4TqpnpspMd5yXiPrKoxqkI8Y9SGbx"
    "WC8JmeIS2AmlkRCnLuTEEeFJQOn+JLue9E665u1RKNnueWu+1XDoSmb4BXyxeWqI9EEdxZGXlKhG6FwesId0bDuA4Erc"
    "oEpADXxRcon7WSl2FKYfn1dsYAclcEQydpjzczlAuD0yXD00mo/h6JftWNMMdHjzGUkWmHohQxVzJSSmrjF0AB/bxIcr"
    "XvE2c56jURuG58IyjPOIpwR6zBW/ltkB7TSGTGUe+3Oc8dl4NCuqkUzH7ZngEtgmwHIdDegkfXugeOCEgXXDI2oGFGsr"
    "Hi0P2av9EVJsrslEH2ZnkJXIaOfI89Lrayhka0R7YDQNb6BoxD4H2TY9PNe8hZw38tknBKwtbWOxRnFW9qAEDckXdu3h"
    "dh5zxGdq/u08Z/KkRW1wepzljrZNCpcLG4KkpKSF0TNLs2Xytp7UevhjAxW2E4l3YwUYj149BaEHrY7GExlJogurWeJj"
    "8ga+8aqzzA+F3FoJrmo5j6a0lKcE8HgxFXy+S52el+F+kjwmcMmvRymNLqSOjtRxdmP4nU4OeZhjm8Uco6RPLpUXB90S"
    "bTZYI1fA3fKCIThXyW06v1jiNc7/KGz4+Jax899OJuqVfmqSxS3hm+NsiPnB2clGFP3smvAKTRf3s12pyTi/V9ydkCMw"
    "fvOclqcx/Ic68NkU9s44LPf4zaul8yeGPbjyti8OF0XDmYrmFjenI+edKqynjIbQK7wGe2+bRhNZjwvzcbCvj8HPrfR8"
    "iPnS0xrHIF4MWZ5S7fZnlWJlayQiHN3ctvawMOD6+jp2Gdnlar5cTcvxcGnrHL5KkbnVZY0Ld2gf/EgCOKU2SLB99eCb"
    "d6sQXL/F9bk6cjLhecyGn2Z7DvhWWMg9vjAa9sjtZVnUnGF7g+xoKgb/AadC7bM="
)

SOURCE = zlib.decompress(base64.b64decode(_B)).decode()
exec(compile(SOURCE, "dog_reference", "exec"))

if __name__ == "__main__":
    print(SOURCE)
