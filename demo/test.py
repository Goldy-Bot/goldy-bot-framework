import sys; sys.path.insert(0, '..')
import os

import GoldyBot
import time
from javascript import require, eval_js, globalThis

GoldyBot.Goldy()

globalThis.__setattr__("GoldyBot", GoldyBot) # SUCCESS

bruh = require("./bruh.mjs")

print(">>", bruh().constructor.name)