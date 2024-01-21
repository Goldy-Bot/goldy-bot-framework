<div align="center">

  # 💛 Goldy Bot Framework

  <img src="./assets/goldy_art/1.png" width="180"/>
  
  <sub>The latest and greatest framework powering the Goldy Bot family.</sub>

  [![Pypi Badge](https://img.shields.io/pypi/v/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "We're on pypi!")
  [![Python Badge](https://img.shields.io/pypi/pyversions/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "Supported python versions.")
  [![Docs Badge](https://img.shields.io/static/v1?label=docs&message=Available&color=light-green)](https://goldybot.devgoldy.xyz/)
  [![Docker Badge](https://img.shields.io/docker/v/devgoldy/goldybot?label=docker)](https://hub.docker.com/r/devgoldy/goldybot "We're on docker!")

</div>

> [!WARNING]
> 
> GoldyBot is in very deep development right now so code will change and **break**.

### ❓ About
Goldy bot is my custom framework built from the ground up to meet my discord bot development needs. It's built on top of the fast [nextcore](https://github.com/nextsnake/nextcore) API wrapper (a low-level API discord wrapper with a ton of control).

### 🩶 This library is probably not for you!
I implement what I need when I need it as I want to keep things to a minimum. The point of this project is to have a framework/library that's tuned towards my needs, so I can reduce the overhead for myself while developing discord bots. With that said you may dislike the way certain things are implemented, so I highly recommend you seek an API wrapper like [nextcord](https://github.com/nextcord/nextcord) or [discord.py](https://github.com/Rapptz/discord.py) for your discord development needs.

## ⚗️ *Install/Set Up* - ``Normal``

These instructions assume you have a [MongoDB database](https://www.mongodb.com/), [Git](https://git-scm.com/) and [Python](https://www.python.org/) installed.

> [!WARNING]
> 
> As of Goldy Bot ``v5.0dev12`` [Git](https://git-scm.com/) is required or else included extensions will **not** function.

> [!NOTE]
> 
> We recommend a clean Mongo database, GoldyBot will connect to your MongoDB database and create stuff the first time you run.

1. **Install package from PyPI.**
```sh
# Windows/Linux

pip install GoldyBot
```

2. **Generate a quick template.**
Create a directory of your choice anywhere, then open a terminal in that directory and type the following below.
```sh
# Windows/Linux

goldy-bot setup
```

3. **Run goldy!** ⚡
Make sure to enter your Discord BOT token and MongoDB database URL in the ``.env`` file generated in your folder.
```env
DISCORD_TOKEN="DISCORD BOT TOKEN HERE"
MONGODB_URL="MONGO DATABASE URL HERE"
```

### JSON Configuration
Also, make sure to add your discord guild to ``test_guild_id`` in ``goldy.toml`` if you are testing or developing. Slash Commands will update quicker, as they will be registered as guild commands instead of global commands. Check out [discord's explanation](https://discord.com/developers/docs/interactions/application-commands#registering-a-command) of global and guild commands for more clarification. Although during production be sure to remove it.

You may also want to add your discord member ID to ``developer_id``, like so: ``developer_id = "332592361307897856"``. If you don't you will be unable to run framework debug commands.
```toml
version = 2

[branding]
name = "Goldy Bot"
emoticon = "🥞"

[extensions]
repos = []
include = [] # Find extension code names at https://github.com/Goldy-Bot/goldybot.repo
ignore = [] # e.g. ignore = ["music.sharing"] <-- {extension}.{module/command}

[extensions.load]
directory = "./extensions"
raise_on_error = true

# It's extremely recommended you include a test guild id 
# if you are testing/developing, otherwise global commands will be 
# loaded instead of guild commands resulting in commands taking FOREVER to load.

# [development]
# test_guild_id = ""
# developer_id = ""
```

**Now you may run goldy bot! 🌠✨**
```sh
goldy-bot start
```
and you're done ✨

### Pulling Extensions
As of Goldy Bot ``v5.0dev12``, extensions are no longer pre-included due to this [issue](https://github.com/Goldy-Bot/Goldy-Bot-Framework/issues/105).

So now if you would like to include them you would need to specify it in the config with ``include`` like so:
```toml
[extensions]
repos = []
include = ["mal_cord"]
```
and you can find the extension code names at the [goldybot.repo](https://github.com/Goldy-Bot/goldybot.repo) github repository.

## 🐬 *Install/Set Up* - ``Docker``

These instructions assume you have [Docker](https://www.docker.com/) installed and that you are running on Linux, although these same steps can be followed on Windows too excluding the Linux commands.

1. **Clone the [goldybot-docker](https://github.com/Goldy-Bot/goldybot-docker) repo.**
```sh
git clone https://github.com/Goldy-Bot/goldybot-docker
```

2. **Set up environment variables.**
```sh
cd goldybot-docker
cp .env.example .env
nano .env
```

Now enter your Discord BOT token over here.
```env
DISCORD_TOKEN="DISCORD BOT TOKEN HERE"
GOLDY_DIRECTORY="./goldy"
```

3. **🐬Docker compose!**
Now you may run docker compose to create your 📦container.
```sh
docker compose up
```

Although you WILL get an error from goldy bot asking you to configure your ``goldy.json`` file. You may follow the instructions [here](https://github.com/Goldy-Bot/Goldy-Bot-V5#json-configuration) on how to configure that. The ``goldy.json`` file can be found in the goldy directory at root. This goldy directory is an exposed docker folder allowing you to configure and add extensions to goldy bot with ease.

Now run docker compose once again and goldy should be running after the MongoDB database has booted.
```sh
docker compose up
```
