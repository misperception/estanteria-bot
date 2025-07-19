from lib.checks import *

class Info(commands.Cog):
    VERSION = "1.2b"
    UP_DATE: datetime.datetime
    bot: commands.Bot

    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.UP_DATE = datetime.datetime.now()

    @commands.hybrid_group(name="info", fallback="bot", description="Devuelve información sobre el bot.")
    async def info(self, ctx: commands.Context):
        embed = discord.Embed(
            title="Información",
            color=discord.Colour.green(),
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=self.bot.user.name, icon_url=self.bot.user.avatar.url if self.bot.user.avatar else "")
        embed.add_field(name="Versión", value=self.VERSION, inline=False)
        embed.add_field(name="Ejecutándose desde", value=f"<t:{int(self.UP_DATE.timestamp())}:R>", inline=False)
        embed.add_field(name="Latencia", value=f"{round(self.bot.latency * 1000)} ms", inline=False)
        await ctx.reply(embed=embed, ephemeral=True)

    @info.command(name="miembro", description="Devuelve información sobre un usuario.")
    async def member_info(self, ctx: commands.Context, member: discord.Member):
        m = Member.read_from_json(member)

        embed = discord.Embed(
            color=discord.Color.green(),
            title="Información",
            timestamp=datetime.datetime.now()
        )
        embed.set_author(name=member.name, icon_url=member.avatar.url)

        embed.add_field(name="Guydocupones", value=m.cupones, inline=False)
        embed.add_field(name="Salario", value=f"{m.salario} Guydocup{"ones" if m.salario > 1 else "ón"}" if m.salario > 0 else "Nada", inline=False)
        embed.add_field(name="¿Es plebeyo?", value="No" if m.admin is True else "Sí", inline=False)
        embed.add_field(name="¿Es esclavo?", value="No" if not m.slave["status"] else f"Sí, acaba<t:{m.slave["end"]}:R>", inline=False)
        embed.add_field(name="¿Es senador honorario?", value="No" if not m.senador["status"] else f"Sí, acaba<t:{m.senador["end"]}:R>", inline=False)
        await ctx.reply(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Info(bot))