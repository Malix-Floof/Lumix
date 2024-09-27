"""
MIT License

Copyright (c) 2022 - 2024 Tasfers

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import disnake
import logging
import datetime

from disnake.ext import commands

now = datetime.datetime.now()
time = now.strftime("%H:%M:%S")
logging.basicConfig(filename='./logs/discord.log', encoding='utf-8', level=logging.INFO)
logging.info(f"\n\n{'-' * 25}(Запуск в {time} {now.day}.{now.month}){'-' * 25}\n")


class Lumix(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            command_prefix='l.', 
            intents=disnake.Intents.all(), 
            owner_ids=settings['owner_id'],
            help_command=None,
            allowed_mentions=disnake.AllowedMentions.none(),
            activity=disnake.Activity(
                type=disnake.ActivityType.custom,
                name='👀 Салют! Я Люма!',
                state='👀 Салют! Я Люма!'
            ),
        )
        self.session = aiohttp.ClientSession(loop=self.loop)

bot = Lumix()
bot.load_extensions("cogs")
bot.run(settings['token'])
