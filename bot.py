from disnake.ext import commands
from os import listdir
import disnake
import mafic
from config import settings, lavalink
import logging
import datetime

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
