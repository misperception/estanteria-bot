import datetime

from lib.checks import *

# Carga de secretos
TOKEN = os.getenv('TOKEN')
PREFIX = '!'
VERSION = "1.01-bugfix"
UP_DATE: datetime.datetime

# Setup de intents (permisos disponibles al bot)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Setup del cliente del bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.hybrid_command(name="info", description="Devuelve información sobre el bot.")
async def version(ctx: commands.Context):
    global UP_DATE
    embed = discord.Embed(
        title="Información",
        color=discord.Colour.green(),
        timestamp=datetime.datetime.now()
    )
    embed.add_field(name="Versión", value=VERSION, inline=False)
    embed.add_field(name="Ejecutándose desde", value=f"<t:{int(UP_DATE.timestamp())}:R>")

    await ctx.reply(embed=embed, ephemeral=True)

# Logging del bot
@bot.event
async def on_ready():
    cogs = ("cogs.econ", "cogs.gpibe", "cogs.errors", "cogs.config")
    # Carga de módulos del bot
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"Módulo {cog} cargado con éxito.")
        except commands.ExtensionFailed:
            print("No se ha podido cargar el módulo.")

    os.makedirs("data", exist_ok=True)
    init_file("data/members.json")
    init_file("data/server.json")
    init_file("data/comisiones.json")
    await bot.tree.sync()
    global UP_DATE
    UP_DATE = datetime.datetime.now()
    print("Bot Online")

# Inicialización
bot.run(TOKEN)