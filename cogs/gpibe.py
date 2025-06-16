import discord, time, random
from discord.ext import commands

def init():
    funny = 0
    i = random.randint(1, 1000)
    return funny, i

class GPibe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.funny, self.i = init()
        self.gpibes = ('https://tenor.com/view/gman-half-life-alyx-creepy-gif-16000932',
                       'https://tenor.com/view/gman-half-life-speech-bubble-reaction-mona-lisa-gif-26331942',
                       'https://tenor.com/view/half-life-half-life-2-g-man-gif-13054231949960000677',
                       'https://tenor.com/view/half-life-2-g-man-smirk-smile-smug-gif-7973971944599751538',
                       'https://tenor.com/view/amethyst-steven-universe-sparkling-water-get-in-gif-7061753751255146882')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author != self.bot.user:
            self.funny +=1
        if self.funny == self.i:
            self.funny, self.i = init()
            await message.channel.send(self.gpibes[random.randint(0,len(self.gpibes)-1)], delete_after=2)


async def setup(bot):
    await bot.add_cog(GPibe(bot))