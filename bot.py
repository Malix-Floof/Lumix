from disnake.ext import commands
from os import listdir
import disnake
import wavelink
from config import settings, lavalink
import lumix.print
import logging
from boticordpy import BoticordClient
import datetime

now = datetime.datetime.now()
time = now.strftime("%H:%M:%S")

logging.basicConfig(filename=f'./logs/log-{now.day}.{now.month}', encoding='utf-8', level=logging.INFO)
logging.info(f"\n\n-------------------------(Запуск в {time} {now.day}.{now.month})-------------------------\n")

class Lumix(commands.InteractionBot):
    def __init__(self, *args,  **kwargs):
        super().__init__(*args, **kwargs)
        self.node = None
        self.loop.create_task(self.start_nodes())

    async def start_nodes(self) -> None:
        await self.wait_until_ready()
        nodes = {
            "bot": self,
            "host": lavalink['host'],
            "port": lavalink['port'],
            "password": lavalink['password'],
            "identifier": lavalink['identifier']
        }
        node: wavelink.Node = await wavelink.NodePool.create_node(**nodes)
        self.node = node
        await lumix.print.log(f"Музыкальная нода {node.identifier} запущена")


intents = disnake.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.guilds = True
bot = Lumix(intents=intents, owner_ids=settings['owner_id'])

async def get_stats():
    return {"servers": len(bot.guilds), "shards": bot.shard_count, "members": len(set(bot.get_all_members()))}

boticord_client = BoticordClient(
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjkyODM2MTM2OTY1MTI2NTUzNiIsInRva2VuIjoiNGlia0dqTldhREx6K0lrQTFkdk9Td1g0dG92QXJZRTRmMFhzQ3duVjRFb1g2VVVZWTI2QVJtd2pIWW5Wc2JpMyIsInJlZGlyZWN0Ijoi0YLRiyDQtNGD0LzQsNC7INGC0YPRgiDRh9GC0L4t0YLQviDQsdGD0LTQtdGCPyIsInBlcm1pc3Npb25zIjowLCJ0eXBlIjoiYm90IiwiaWF0IjoxNjkyMjc5MTk4fQ.e8GCgv4epPm_BFPEJfmCgXINfY-20YpjY30kzp8KJ3E",
    version=3
)
autopost = (
    boticord_client.autopost()
    .init_stats(get_stats)
    .start("1006946815050006539")
)

@bot.event
async def on_ready():
    await lumix.print.log(f"Запущенно {bot.shard_count} шардов! {round(bot.latency * 1000)}ms")

list_cogs = [filename[:-3] for filename in listdir("./cogs") if filename.endswith(".py")]
for cog in list_cogs: bot.load_extension(f"cogs.{cog}")


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
