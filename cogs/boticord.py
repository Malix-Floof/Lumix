import disnake
from disnake.ext import commands
from boticordpy import BoticordClient


class BoticordAPI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.boticord_client = BoticordClient("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjkyODM2MTM2OTY1MTI2NTUzNiIsInRva2VuIjoiNGlia0dqTldhREx6K0lrQTFkdk9Td1g0dG92QXJZRTRmMFhzQ3duVjRFb1g2VVVZWTI2QVJtd2pIWW5Wc2JpMyIsInJlZGlyZWN0Ijoi0YLRiyDQtNGD0LzQsNC7INGC0YPRgiDRh9GC0L4t0YLQviDQsdGD0LTQtdGCPyIsInBlcm1pc3Npb25zIjowLCJ0eXBlIjoiYm90IiwiaWF0IjoxNjkyMjc5MTk4fQ.e8GCgv4epPm_BFPEJfmCgXINfY-20YpjY30kzp8KJ3E", version=3)
        self.autopost = (
            self.boticord_client.autopost()
            .init_stats(self.get_stats)
            .on_success(self.on_success_posting)
            .start("1006946815050006539")
        )

    def cog_unload(self):
        self.autopost.stop()

    @commands.Cog.listener()
    async def on_success_posting(self):
        print("Boticord Stats Send!")

    def get_stats(self):
        return {"servers": len(self.bot.users), "shards": self.bot.shard_count, "members": len(self.bot.users)}

    @commands.Cog.listener()
    async def on_ready(self):
        print("Bot is ready!")

    @commands.Cog.listener()
    async def on_success_posting(self):
        print("Boticord Stats Send!")


def setup(bot):
    bot.add_cog(BoticordAPI(bot))
