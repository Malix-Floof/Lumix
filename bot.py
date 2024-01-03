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
import mafic
import logging
import datetime

from disnake.ext import commands
from os import listdir
from config import settings, lavalink


now = datetime.datetime.now()
time = now.strftime("%H:%M:%S")
logging.basicConfig(filename=f'./logs/log-{now.day}.{now.month}', encoding='utf-8', level=logging.INFO)
logging.info(f"\n\n-------------------------(Запуск в {time} {now.day}.{now.month})-------------------------\n")


class Lumix(commands.Bot):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.pool = mafic.NodePool(self)
        self.loop.create_task(self.add_nodes())

    async def add_nodes(self):
        await self.wait_until_ready()
        await self.pool.create_node(
            host=lavalink['host'],
            port=lavalink['port'],
            label=lavalink['identifier'],
            password=lavalink['password'],
        )

bot = Lumix(
    command_prefix="l.", 
    intents=disnake.Intents.all(), 
    help_command=None,
)

@bot.event
async def on_ready():
    print("Ready!")
    
bot.load_extensions("cogs")
bot.run(settings['token'])
