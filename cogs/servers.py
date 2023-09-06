import disnake
from disnake.ext import commands
from config import settings

class ServerInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        channel = self.bot.get_channel(1116457410672996362)
        owner = guild.owner
        embed = disnake.Embed(title="Бот добавлен на сервер",
                              description=f"Информация о сервере:\n"
                                          f"> Владелец: {owner.mention} ({owner.name}#{owner.discriminator}) ({owner.id})\n"
                                          f"> Шард: {guild.shard_id}\n"
                                          f"> Количество участников: {guild.member_count}\n"
                                          f"> Название сервера: {guild.name}\n"
                                          f"> ID сервера: {guild.id}",
                              color=0x2b2d31)
        embed.set_thumbnail(url=guild.icon)
        await channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        channel = self.bot.get_channel(1116457410672996362)
        owner = guild.owner
        embed = disnake.Embed(title="Бот удалён с сервера",
                              description=f"Информация о сервере:\n"
                                          f"> Владелец: {owner.mention} ({owner.name}#{owner.discriminator}) ({owner.id})\n"
                                          f"> Шард: {guild.shard_id}\n"
                                          f"> Количество участников: {guild.member_count}\n"
                                          f"> Название сервера: {guild.name}\n"
                                          f"> ID сервера: {guild.id}",
                              color=0x2b2d31)
        embed.set_thumbnail(url=guild.icon)
        await channel.send(embed=embed)

def setup(bot):
    bot.add_cog(ServerInfoCog(bot))