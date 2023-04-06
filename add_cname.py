"""
Just a script that is ran by GitHub actions to add the CNAME file to the built docs.
"""

CNAME = "goldybot.devgoldy.me"

open("./docs/_build/CNAME", mode="w").write(CNAME)