<div align="center">

  # 💛 Goldy Bot V5
  
  <sub>Yet another another rewrite of Goldy Bot, a discord bot framework for my own bots.</sub>
  
  [![Codacy Badge](https://app.codacy.com/project/badge/Grade/ba2409ee9b524e99a01344f208a74a7e)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=Goldy-Bot/Goldy-Bot-V5&amp;utm_campaign=Badge_Grade)
  [![Pypi Badge](https://img.shields.io/pypi/v/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "We're on pypi!")
  [![Python Badge](https://img.shields.io/pypi/pyversions/GoldyBot?style=flat)](https://pypi.org/project/GoldyBot/ "Supported python versions.")
  [![Docs Badge](https://img.shields.io/static/v1?label=docs&message=Available&color=light-green)](https://goldybot.devgoldy.me/)
  
</div>

#### ⚠ *Warning: ``GoldyBot`` is in very deep development right now so some utils and code will be incomplete.*

<p align="right">


  <h2>Why Version 5?</h2>

  
  <img align="left" src="https://raw.githubusercontent.com/Goldy-Bot/Goldy-Bot-V5/master/assets/goldy_art/1.png" width="180"/>

  > I'm developing a new Discord bot framework to replace my [previous one](https://github.com/Goldy-Bot/Goldy-Bot-V4), which I found limiting and frustrating. The new framework will be more efficient and user-friendly and will utilize what I believe to be a better API wrapper than discord.py, which prompted the rewrite. Originally, I planned to update [V4](https://github.com/Goldy-Bot/Goldy-Bot-V4) for backwards compatibility, but it would be too difficult, and my extensions would need to be rewritten anyways. Therefore, I'm excited to announce the upcoming release of Goldy Bot Framework V5, which will be a brand-new framework starting fresh. 🍋

</p>

<br>

## *Install/Set Up* - ``Normal``

These instructions assume you have a [MongoDB database](https://www.mongodb.com/), [Git](https://git-scm.com/) and [Python](https://www.python.org/) installed.

> ℹ GoldyBot will connect to your mongoDB database and create stuff.

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

Make sure to enter your Discord BOT token and mongoDB database token in the ``.env`` file generated in your folder.
```env
DISCORD_TOKEN="DISCORD BOT TOKEN HERE"
MONGODB_TOKEN="MONGO DATABASE TOKEN HERE"
```

Also make sure to add your discord guild to ``allowed_guilds`` in ``goldy.json``.

You may change ``"uwu_hangout_guild"`` to anything you like but just remember this will be the code_name of the guild within goldy bot and you'll use this code_name to reference it.

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
    }
}
```

**Now you may run GoldyBot! 🌠✨**
```sh
python run.py
```



<br>

<div align="center">

  **© Copyright (C) 2023 Goldy (Under the [GPL-3.0 License](LICENSE))**

</div>
