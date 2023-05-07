"""
Just a script that is ran by GitHub actions to add the CNAME file to the built docs.
"""

CNAME = "goldybot.devgoldy.xyz"

open("./_build/CNAME", mode="w").write(CNAME)
