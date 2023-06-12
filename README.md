<div align="center">

  # 💛 Goldy Bot V5
  
  <sub>Yet another another rewrite of Goldy Bot, a discord bot framework for my own bots.</sub>

  [![Pypi Badge](https://img.shields.io/pypi/v/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "We're on pypi!")
  [![Python Badge](https://img.shields.io/pypi/pyversions/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "Supported python versions.")
  [![Docs Badge](https://img.shields.io/static/v1?label=docs&message=Available&color=light-green)](https://goldybot.devgoldy.xyz/)
  [![Docker Badge](https://img.shields.io/docker/v/devgoldy/goldybot?label=docker)](https://hub.docker.com/r/devgoldy/goldybot "We're on docker!")
  
</div>

#### ⚠ *Warning: ``GoldyBot`` is in very deep development right now so some utils and code will be incomplete.*

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

  > I'm developing a new Discord bot framework to replace my [previous one](https://github.com/Goldy-Bot/Goldy-Bot-V4), which I found limiting and frustrating. The new framework will be more efficient and user-friendly and will utilize what I believe to be a better API wrapper than discord.py, which prompted the rewrite. Originally, I planned to update [V4](https://github.com/Goldy-Bot/Goldy-Bot-V4) for backwards compatibility, but it would be too difficult, and my extensions would need to be rewritten anyways. Therefore, I'm excited to announce the upcoming release of Goldy Bot Framework V5, which will be a brand-new framework starting fresh. 🍋

</p>

### 🏆 Goal
My goal is to have a functional framework that's fast and lightweight and has the least code possible to maintain. 

### 💛 Is goldy bot for you?
Do note that the whole point of this framework is to make it easier on myself to develop discord bots so you may dislike the way certain things are implemented; if so I highly recommend you not use the framework because more and more things will be implemented that way in the future so it's best to seek an API wrapper like [nextcord](https://github.com/nextcord/nextcord) for your discord bot development needs instead.

On a similar note goldy bot v5 is currently in a ALWAYS changing state, previous code WILL BREAK, non-stable versions especially so you'll find yourself always fixing your extensions after each release.

### ⚡ Nextcore
[Nextcore](https://github.com/nextsnake/nextcore) is the perfect api wrapper for v5, it's fast, low level and can be easily modified. Additionally, Nextcore provides a ton of control, this gives me the freedom to build my framework exactly the way I want it, without any unnecessary overhead like if I stayed with nextcord/discord.py.

## 🛠 *Install/Set Up* - ``Normal``

These instructions assume you have a [MongoDB database](https://www.mongodb.com/), [Git](https://git-scm.com/) and [Python](https://www.python.org/) installed.

> ℹ We recommend a clean mongo database, GoldyBot will connect to your mongoDB database and create stuff the first time you run.

1. ~~**Install package from pypi.**~~ *not on there yet... here's a git install*
```sh
# Windows/Linux

pip install GoldyBot@git+https://github.com/Goldy-Bot/Goldy-Bot-V5
```

2. **Generate a quick template.**
Create a directory of your choice anywhere, then open a terminal in that directory and type the following below.
```sh
# Windows/Linux

goldybot setup normal
```

3. **Run goldy!** ⚡

Make sure to enter your Discord BOT token and mongoDB database url in the ``.env`` file generated in your folder.
```env
DISCORD_TOKEN="DISCORD BOT TOKEN HERE"
MONGODB_URL="MONGO DATABASE URL HERE"
```

### JSON Configuration

Also make sure to add your discord guild to ``allowed_guilds`` in ``goldy.json``.

You may change ``"uwu_hangout_guild"`` to anything you like but just remember this will be the code_name of the guild within goldy bot and you'll use this code_name to reference it later.

You may also want to add your discord member id to ``"bot_dev"``, like so: ``"bot_dev": "332592361307897856"``. If you don't you may not be able to run specific bot admin commands on discord.

```json
{
    "goldy" : {
        "extensions": {
            "ignored_extensions" : [],

            "raise_on_load_error" : true,
            "folder_location" : "./extensions"
        },

        "allowed_guilds" : {
            "{guild_id_here}" : "uwu_hangout_guild"
        }
    },

    "bot_dev": null
}
```

**Now you may run GoldyBot! 🌠✨**
```sh
python run.py
```

<br>

## 🐬 *Install/Set Up* - ``Docker``

These instructions assume you have [Docker](https://www.docker.com/) installed and that you are running on Linux, althought these same steps can be followed on windows too excluding the linux commands.

1. **Clone the [goldybot-docker](https://github.com/Goldy-Bot/goldybot-docker) repo.**
```sh
git clone https://github.com/Goldy-Bot/goldybot-docker
```

2. **Setup enviorment variables.**
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
sudo docker compose up
```

Although you WILL get error an error from goldy bot asking you to configure your ``goldy.json`` file. You may follow the instructions [here](https://github.com/Goldy-Bot/Goldy-Bot-V5#json-configuration) on how to configure that. The ``goldy.json`` file can be found in the goldy directory at root. This goldy directory is an exposed docker folder allowing you to configure and add extensions to goldy bot with ease.

Now run docker compose once again and goldy should be running after the mongodb database has booted.
```sh
sudo docker compose up
```

<br>

<div align="center">

  **© Copyright (C) 2023 Goldy (Under the [GPL-3.0 License](LICENSE))**

</div>
