from asyncio import sleep

from lib.checks import *
import views.config

class Abort(Exception):
    pass


# Clase con métodos de configuración
class _ConfigHelper:
    server: Server
    message: discord.Message
    def __init__(self, server: Server, message: discord.Message):
        self.server = server
        self.message = message

    # Método para el manejo de configuraciones
    async def __handle(self, config):
        await self.message.edit(content=f"{config.label}:\n", view=config)
        await config.wait()
        if config.abort:
            raise Abort
    # Método para la configuración de salario
    async def salario(self):
        config = views.config.SalarioView("Selecciona los salarios de los miembros")
        await self.__handle(config)
        self.server.sueldos = config.d
    # Método para la configuración de roles de admin
    async def admin(self):
        config = views.config.SelectRoleView("Selecciona los roles de administrador", 25)
        await self.__handle(config)
        self.server.roles_admin = [val.id for val in config.selection.values]
    # Método para la configuración del canal de tienda
    async def tienda(self):
        config = views.config.SelectChannelView("Selecciona el canal de tienda")
        await self.__handle(config)
        self.server.canal_tienda = config.selection.values[0].id
    # Método para la configuración del canal bancario
    async def bancario(self):
        config = views.config.SelectChannelView("Selecciona el canal bancario")
        await self.__handle(config)
        self.server.canal_bancario = config.selection.values[0].id
    # Método para la configuración del rol de senador honorario
    async def senador(self):
        config = views.config.SelectRoleView("Selecciona el rol de senador honorario")
        await self.__handle(config)
        self.server.rol_senador = config.selection.values[0].id
    # Método para la configuración del rol de esclavo
    async def esclavo(self):
        config = views.config.SelectRoleView("Selecciona el rol de esclavo")
        await self.__handle(config)
        self.server.rol_esclavo = config.selection.values[0].id
    # Método para la configuración del rol de artista
    async def artista(self):
        config = views.config.SelectRoleView("Selecciona el rol de artista")
        await self.__handle(config)
        self.server.rol_artista = config.selection.values[0].id
    # Método de clase que envuelve una configuración para crear un nuevo comando de configuración
    @classmethod
    async def wrap(cls, ctx: commands.Context, fn):
        server = Server.read_from_json(ctx.guild)
        message = await ctx.reply("Iniciando configuración...")
        cfg = cls(server, message)
        await sleep(0.5)
        try: await fn(self=cfg)
        except Abort:
            await message.delete()
            return
        await message.delete()
        server.write_to_json()
        await ctx.reply("Cambios realizados.")


class Configuracion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _list_config(self, server: Server, ctx: commands.Context) -> discord.Embed:
        guild = ctx.guild
        embed = discord.Embed(
            title = "Configuración",
            color = discord.Color.green()
        )
        embed.add_field(name="Roles de administrador",
                        value='\n'.join([guild.get_role(rol).mention for rol in server.roles_admin]))
        embed.add_field(name="Canal de tienda", value=guild.get_channel(server.canal_tienda).mention)
        embed.add_field(name="Canal bancario", value=guild.get_channel(server.canal_bancario).mention)
        embed.add_field(name="Sueldos:", value=
        "\n".join([f"**{guild.get_role(int(rol)).name}**: {n} Guydocup{"ón" if n == 1 else "ones"}." for rol, n in server.sueldos.items()]))
        embed.add_field(name="Rol de senador honorario", value=guild.get_role(server.rol_senador).mention)
        embed.add_field(name="Rol de esclavo", value=guild.get_role(server.rol_esclavo).mention)
        embed.add_field(name="Rol de artista", value=guild.get_role(server.rol_artista).mention)
        return embed

    @commands.hybrid_command(name="configuracion", description="Devuelve la configuración actual del servidor")
    @owner_only()
    async def list_conf(self, ctx: commands.Context):
        server = Server.read_from_json(ctx.guild)
        embed = self._list_config(server, ctx)
        await ctx.reply(embed=embed)

    @commands.hybrid_group(name="configurar", fallback="servidor", description="Configura los datos del servidor")
    @owner_only()
    async def config(self, ctx: commands.Context):
        message = await ctx.reply("Iniciando configuración...")
        await sleep(0.5)
        # Creación del objeto servidor con la configuración dada
        server = Server(ctx.guild.id)
        config = _ConfigHelper(server, message)
        await config.admin()
        await config.tienda()
        await config.bancario()
        await config.salario()
        await config.senador()
        await config.esclavo()
        await config.artista()

        # Embed con los cambios realizados
        confirm = views.config.ViewObj()
        embed = self._list_config(server, ctx)
        await message.edit(content="¿Continuar con la configuración actual?", embed=embed, view=confirm)
        await confirm.wait()
        if confirm.abort:
            await message.delete()
            return

        # Finalización
        server.configurado = True
        server.write_to_json()
        await message.delete()
        await ctx.reply("Configuración completada", ephemeral=True)

    @config.command(name="salario", description="Configura los salarios")
    @owner_only()
    async def salario(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.salario)

    @config.command(name="admin", description="Configura los roles de admin")
    @owner_only()
    async def admin(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.admin)

    @config.command(name="canal_tienda", description="Configura el canal de tienda")
    @owner_only()
    async def tienda(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.tienda)

    @config.command(name="canal_bancario", description="Configura el canal bancario")
    @owner_only()
    async def bancario(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.bancario)

    @config.command(name="senador_honorario", description="Configura el rol de senador honorario")
    @owner_only()
    async def senador(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.senador)

    @config.command(name="esclavo", description="Configura el rol de esclavo")
    @owner_only()
    async def esclavo(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.esclavo)

    @config.command(name="artista", description="Configura el rol de artista")
    @owner_only()
    async def artista(self, ctx: commands.Context):
        await _ConfigHelper.wrap(ctx=ctx, fn=_ConfigHelper.artista)


async def setup(bot):
    await bot.add_cog(Configuracion(bot))