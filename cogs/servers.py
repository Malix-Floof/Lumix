import disnake
from disnake.ext import commands, tasks
from config import settings
from db import SQLITE

db = SQLITE

class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.servers = 0
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.delservers.start()
        print("servers.py is ready!")
    
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.servers += 1
        channel = self.bot.get_channel(1116457410672996362)
        owner = guild.owner
        embed = disnake.Embed(title="🟢 Бот добавлен на сервер",
                              description=f"Информация о сервере:\n"
                                          f"> Владелец: {owner.mention} ({owner.name}#{owner.discriminator}) ({owner.id})\n"
                                          f"> Шард: {guild.shard_id}\n"
                                          f"> Количество участников: {guild.member_count}\n"
                                          f"> Название сервера: {guild.name}\n"
                                          f"> ID сервера: {guild.id}",
                              color=0x2b2d31)
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=f"За день меня добавили на {self.servers} серверов")
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        self.servers -= 1
        channel = self.bot.get_channel(1116457410672996362)
        owner = guild.owner
        embed = disnake.Embed(title="🔴 Бот удалён с сервера",
                              description=f"Информация о сервере:\n"
                                          f"> Владелец: {owner.mention} ({owner.name}#{owner.discriminator}) ({owner.id})\n"
                                          f"> Шард: {guild.shard_id}\n"
                                          f"> Количество участников: {guild.member_count}\n"
                                          f"> Название сервера: {guild.name}\n"
                                          f"> ID сервера: {guild.id}",
                              color=0x2b2d31)
        embed.set_thumbnail(url=guild.icon)
        embed.set_footer(text=f"За день меня добавили на {self.servers} серверов")
        msg = await channel.send(embed=embed)
        # Удаление данных после того как бота выгнали
        try:
            if db.get(f"autorole_{guild.id}") is not None:
                db.delete(f"autorole_{guild.id}")
        except:
            ...
        try:
            if db.get(f"logchannel_{guild.id}") is not None:
                db.delete(f"logchannel_{guild.id}")
        except:
            ...
        try:
            if db.get(f"lang_{guild.id}") is not None:
                db.delete(f"lang_{guild.id}")
        except:
            ...
        embed.set_footer(text=f"За день меня добавили на {self.servers} серверов\nДанные были удалены из базы данных")
        await msg.edit(embed=embed)
            
    
    @tasks.loop(hours=24)
    async def delservers(self):
        self.servers = 0
        
def setup(bot):
    bot.add_cog(ServerInfoCog(bot))
