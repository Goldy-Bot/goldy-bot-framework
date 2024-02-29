import sys; sys.path.insert(0, '.')

import os
from goldy_bot import __version__

os.system(
    f"docker build -t devgoldy/goldybot:{__version__} --build-arg ARCH=amd64 ."
)

os.system(
    "docker build -t devgoldy/goldybot:latest --build-arg ARCH=amd64 ."
)