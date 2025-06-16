from lib.checks import *

class Handling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        if issubclass(type(error), ShelfError):
            await ctx.reply(error.response(), ephemeral=True)

    # Revisa si el bot está sin configurar y no deja utilizar ningún otro comando que no sea "configurar"
    def bot_check(self, ctx: commands.Context):
        if ctx.command.name == "configurar": return True
        s = Server.read_from_json(ctx.guild)
        if not s.configurado: raise NoConfig
        return True

async def setup(bot):
    await bot.add_cog(Handling(bot))