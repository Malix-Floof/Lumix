"""
MIT License

Авторские права (с) 2022 - 2024 Tasfers
Авторское право (c) 2022 - настоящее время разработка Lumix

Настоящим предоставляется безвозмездное разрешение любому лицу, 
получившему копию этого программного обеспечения и связанных с 
ним файлов документации (далее - "Программное обеспечение"), 
осуществлять операции с Программным обеспечением без ограничений,
включая, но не ограничиваясь, правом использования, копирования,
изменения, слияния, публикации, распространения, но с запретом продажи,
лицензирования и сублицензирования копий Программного обеспечения,
а также лицам, которым предоставляется Программное обеспечение, при соблюдении следующих условий:

Указанное выше уведомление об авторских правах
и это разрешение должны быть включены во все
копии или значимые части программного обеспечения.

ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ "КАК ЕСТЬ",
БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, ЯВНЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ,
ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ, ГАРАНТИИ КОММЕРЧЕСКОЙ ЦЕННОСТИ,
ПРИГОДНОСТИ ДЛЯ КОНКРЕТНОЙ ЦЕЛИ И НЕНАРУШЕНИЯ.

В НИКАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ 
НЕ НЕСУТ ОТВЕТСТВЕННОСТИ ЗА ЛЮБЫЕ ИСКИ,
УБЫТКИ ИЛИ ДРУГИЕ ОТВЕТСТВЕННОСТИ, 
БУДЬ ТО В ДЕЙСТВИИ ДОГОВОРА, ПРАВОНАРУШЕНИЯ ИЛИ ИНАЧЕ,
ВОЗНИКАЮЩИЕ ИЗ, ИЛИ В СВЯЗИ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ
ИЛИ ИСПОЛЬЗОВАНИЕМ ИЛИ ДРУГИМИ ДЕЛАМИ В ПРОГРАММНОМ ОБЕСПЕЧЕНИИ.



MIT License

Copyright (c) 2022 - 2024 Tasfers
Copyright (c) 2022 - present development of Lumix

Permission is hereby granted free of charge to any person
who has received a copy of this software and related
documentation files (hereinafter referred to as the "Software")
to carry out operations with the Software without restrictions,
including, but not limited to, the right to use, copy,
modify, merge, publish, distribute, but with a prohibition of sale,
licensing and sublicensing copies of the Software,
as well as to the persons to whom the Software is provided, subject to the following conditions:

The above copyright notice
and this permission must be included in all
copies or significant parts of the software.

THE SOFTWARE IS PROVIDED "AS IS",
WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
INCLUDING, BUT NOT LIMITED TO, GUARANTEES OF COMMERCIAL VALUE,
SUITABILITY FOR
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


class Lumix(commands.AutoShardedBot):
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
    owner_ids=settings['owner_id'],
    help_command=None,
)

@bot.event
async def on_ready():
    print(f"Запущенно {bot.shard_count} шардов! {round(bot.latency * 1000)}ms")
    
    
list_cogs = [filename[:-3] for filename in listdir("./cogs") if filename.endswith(".py")]
for cog in list_cogs: 
    bot.load_extension(f"cogs.{cog}")


@bot.slash_command(description=f'Загрузить модуль бота', guild_ids=settings['test_servers_id'])
async def load(inter, module: str = commands.Param(description="Название модуля")):
    bot.load_extension(f"cogs.{module}")
    await inter.send(f"Загружен модуль `{module}`", ephemeral=True)


@bot.slash_command(description=f'Выгрузить модуль бота', guild_ids=settings['test_servers_id'])
async def unload(inter, module: str = commands.Param(description="Название модуля")):
    bot.unload_extension(f"cogs.{module}")
    await inter.send(f"Выгружен модуль `{module}`", ephemeral=True)


@bot.slash_command(description=f"Перезагрузить модуль бота", guild_ids=settings['test_servers_id'])
async def reload(inter, module: str = commands.Param(description="Название модуля", choices=list_cogs)):
    bot.reload_extension(f"cogs.{module}")
    await inter.send(f"Перезагружен модуль `{module}`", ephemeral=True)

bot.run(settings['token'])
