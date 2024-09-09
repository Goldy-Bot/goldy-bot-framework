<div align="center">

  # 💛 Goldy Bot Framework
  
  <sub>The latest and greatest framework powering the Goldy Bot family.</sub>

  [![Pypi Badge](https://img.shields.io/pypi/v/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "We're on pypi!")
  [![Python Badge](https://img.shields.io/pypi/pyversions/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "Supported python versions.")
  [![Docs Badge](https://img.shields.io/static/v1?label=docs&message=Available&color=light-green)](https://goldybot.devgoldy.xyz/)
  [![Docker Badge](https://img.shields.io/docker/v/devgoldy/goldybot?label=docker)](https://hub.docker.com/r/devgoldy/goldybot "We're on docker!")
  
</div>

> [!WARNING]
> 
> *GoldyBot is in very deep development right now so some utils and code will be incomplete and breaking changes will occur.*

# ⚠️ This version is DEPRECATED!
This version of the codebase has seized development since December 20th of 2023, so it's insanely out of date.
I advise you to only look at the [pancake rewrite](https://github.com/Goldy-Bot/goldy-bot-framework/tree/v5.1dev1) if you wanna view the project.

**v5.1 Rewrite (pancake):** https://github.com/Goldy-Bot/goldy-bot-framework/tree/v5.1dev1

## Table of Contents

1. [Why Version 5?](#why-version-5)
   - [🏆 Goal](#-goal)
   - [💛 Is goldy bot for you?](#-is-goldy-bot-for-you)
   - [⚡ Nextcore](#-nextcore)
2. [Install/Set Up](#-installset-up---normal)
   - [🛠 Normal](#-installset-up---normal)
   - [🐬 Docker](#-installset-up---docker)

<p align="right">


  ## Why Version 5?

  
  <img align="left" src="./assets/goldy_art/1.png" width="180"/>

  > I'm developing a new Discord bot framework to replace my [previous one](https://github.com/Goldy-Bot/Goldy-Bot-V4), which I found limiting and frustrating. The new framework will be more efficient and user-friendly and will utilize what I believe to be a better API wrapper than discord.py, which prompted the rewrite. Originally, I planned to update [V4](https://github.com/Goldy-Bot/Goldy-Bot-V4) for backward compatibility, but it would be too difficult, and my extensions would need to be rewritten anyways. Therefore, I'm excited to announce the upcoming release of Goldy Bot Framework V5, which will be a brand-new framework starting fresh. 🍋

</p>

### 🏆 Goal
My goal is to have a functional framework that's fast and lightweight and has the least code possible to maintain. 

### 💛 Is goldy bot for you?
Do note that the whole point of this framework is to make it easier for myself to develop discord bots so you may dislike the way certain things are implemented; if so I highly recommend you not use the framework because more and more things will be implemented that way in the future so it's best to seek an API wrapper like [nextcord](https://github.com/nextcord/nextcord) for your discord bot development needs instead.

On a similar note goldy bot v5 is currently in an ALWAYS changing state, previous code WILL BREAK, non-stable versions especially so you'll find yourself always fixing your extensions after each release.

### ⚡ Nextcore
[Nextcore](https://github.com/nextsnake/nextcore) is the perfect API wrapper for v5, it's fast, low-level, and can be easily modified. Additionally, Nextcore provides a ton of control, this gives me the freedom to build my framework exactly the way I want it, without any unnecessary overhead like if I stayed with nextcord/discord.py.

## 🛠 *Install/Set Up* - ``Normal``

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

goldybot setup
```

3. **Run goldy!** ⚡

Make sure to enter your Discord BOT token and MongoDB database URL in the ``.env`` file generated in your folder.
```env
DISCORD_TOKEN="DISCORD BOT TOKEN HERE"
MONGODB_URL="MONGO DATABASE URL HERE"
```

### JSON Configuration

Also, make sure to add your discord guild to ``allowed_guilds`` in ``goldy.json``.

You may change ``"test_server"`` BUT **ONLY** if it's not a server you're going to be developing and testing on. The code name ``test_server`` is already reserved for you to use as a development environment to test your commands. Slash Commands will reload/update quicker in the ``test_server`` as they will be registered as guild commands instead of global commands. Check out [discord's explanation](https://discord.com/developers/docs/interactions/application-commands#registering-a-command) of global and guild commands for more clarification. 

If your guild/server is not a testing server you may name it whatever you like but just remember this will be the code_name of the guild within goldy bot and you'll use this code_name to reference it later.

You may also want to add your discord member id to ``"bot_dev"``, like so: ``"bot_dev": "332592361307897856"``. If you don't you may be unable to run specific bot administration commands within Discord.
```json
{
    "version": 1,
    "goldy" : {
        "branding": {
            "name": "💛 Goldy Bot"
        },
        "extensions": {
            "include": [],

            "ignored_extensions" : [],
            "late_load_extensions": [],

            "raise_on_load_error" : true,
            "folder_location" : "./extensions"
        },
        "allowed_guilds" : {
            "{guild_id_here}" : "test_server"
        },

        "bot_dev": null,
        "ding_on_exit": false
    }
}
```

**Now you may run GoldyBot! 🌠✨**
```sh
python run.py
```
and you're done ✨

### Pulling Extensions
As of Goldy Bot ``v5.0dev12``, extensions are no longer pre-included due to this [issue](https://github.com/Goldy-Bot/Goldy-Bot-Framework/issues/105).

So now if you would like to include them you would need to specify it in the config with ``include`` like so:
```json
{
    "goldy" : {
        "extensions": {
            "include": ["mal_cord"]
        }
    }
}
```
and you can find the extension code names at the [goldybot.repo](https://github.com/Goldy-Bot/goldybot.repo) github repository.

<br>

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

<br>

<div align="center">

  **© Copyright (C) 2023 Goldy (Under the [GPL-3.0 License](LICENSE))**

</div>
