from lib.checks import *
from views.persistent_view import namespace as view_namespace

# Carga de secretos
TOKEN = os.getenv('TOKEN')
PREFIX = '!'

# Setup de intents (permisos disponibles al bot)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Sobreescritura de la clase de Bot (para recargar Views viejas)
class Mensajero(commands.Bot):
    def __init__(self, prefix, intents):
        super().__init__(command_prefix=prefix, intents=intents)

    async def setup_hook(self):
        print("Inicializando archivos de datos...")
        os.makedirs("data", exist_ok=True)
        init_file("data/members.json")
        init_file("data/server.json")
        init_file("data/comisiones.json")
        init_file("data/views.json")

    def refresh_views(self):
        data = read_json("data/views.json")
        for view_id, view_dict in data.items():
            cls = view_namespace[view_dict["name"]]
            view = cls.read_from_dict(d=view_dict, id=view_id, bot=self)
            self.add_view(view)

    # Logging del bot
    async def on_ready(self):
        print("Cargándo módulos...")
        cogs = (f"cogs.{name[:-3]}" for name in os.listdir("cogs") if ".py" in name)

        # Carga de módulos del bot
        for cog in cogs:
            try:
                await self.load_extension(cog)
                print(f"Módulo {cog} cargado con éxito.")
            except commands.ExtensionFailed:
                print(f"No se ha podido cargar el módulo {cog}")
        print("Cargando comandos...")
        await self.tree.sync()
        print("Recargando menús...")
        self.refresh_views()
        print("Bot Online")

    async def on_resumed(self):
        self.refresh_views()


# Setup del cliente del bot
bot = Mensajero(prefix=PREFIX, intents=intents)

# Inicialización
bot.run(TOKEN)