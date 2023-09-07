import disnake
from disnake.ext import commands
from datetime import datetime

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        channel = self.bot.get_channel(1149329202777170022)
        timestamp = int(datetime.timestamp(datetime.now()))
        embed = disnake.Embed(description=f"`💔` <t:{timestamp}:f> (<t:{timestamp}:R>) Последний вызов вызвал исключение:\n```cmd\n{error}\n```", color=disnake.Colour.red())
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Errors(bot))
