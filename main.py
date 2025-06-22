from lib.checks import *

# Carga de secretos
TOKEN = os.getenv('TOKEN')
PREFIX = '!'
VERSION = "1.01-bugfix"

# Setup de intents (permisos disponibles al bot)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Setup del cliente del bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

@bot.command(name="version", description="Devuelve la versión del bot.")
async def version(ctx: commands.Context):
    await ctx.reply(f"Mensajero - versión {VERSION}", ephemeral=True)

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
    print("Bot Online")

# Inicialización
bot.run(TOKEN)