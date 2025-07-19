import discord, time
from random import getrandbits, choice
from discord.ext import commands

def roll():
    special = getrandbits(12)
    return special

class GPibe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.threshold = roll()
        self.gpibes = ('https://tenor.com/view/gman-half-life-alyx-creepy-gif-16000932',
                       'https://tenor.com/view/gman-half-life-speech-bubble-reaction-mona-lisa-gif-26331942',
                       'https://tenor.com/view/half-life-half-life-2-g-man-gif-13054231949960000677',
                       'https://tenor.com/view/half-life-2-g-man-smirk-smile-smug-gif-7973971944599751538',
                       'https://tenor.com/view/amethyst-steven-universe-sparkling-water-get-in-gif-7061753751255146882')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
            return

        chance = roll()
        if chance == self.threshold:
            self.threshold = roll()
            await message.channel.send(choice(self.gpibes), delete_after=2)


async def setup(bot):
    await bot.add_cog(GPibe(bot))