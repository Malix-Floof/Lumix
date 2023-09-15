import disnake
from disnake.ext import commands
from datetime import datetime

class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_slash_command_error(self, inter, error):
        if isinstance(error, commands.Cooldown):
            return
        channel = self.bot.get_channel(1149329202777170022)
        timestamp = int(datetime.timestamp(datetime.now()))
        command = inter.permissions.value
        if command == 562949953421311:
            command = "562949953421311 - Все права"
        if command == 8:
            command = "8 - Администратор"
        name = inter.application_command.name
        embed = disnake.Embed(description=f"`💔` <t:{timestamp}:f> (<t:{timestamp}:R>) Последний вызов вызвал исключение:\n```cmd\n{error}\n```"
                                          f"\nКод разрешений: \n```\n{command}\n```\nСервер: {inter.guild.name}\nПользователь: {inter.author.name}\nID сервера: {inter.guild.id}\nID участника: {inter.author.id}"
                                          f"\n Команда: </{name}:{inter.data.id}>",
                              color=disnake.Colour.red())
        await channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Errors(bot))
