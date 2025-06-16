from discord.ext import commands
from lib.shelflib import *

# Carga de secretos
TOKEN = os.getenv('TOKEN')
PREFIX = '!'

# Setup de intents (permisos disponibles al bot)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Setup del cliente del bot
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

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

    init_file("members.json")
    init_file("server.json")
    init_file("comisiones.json")
    await bot.tree.sync()
    print("Bot Online")

# Inicialización
bot.run(TOKEN)