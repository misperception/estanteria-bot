from asyncio import sleep
from lib.checks import *
import views.config



class Config(commands.Cog):
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
    async def get_conf(self, ctx: commands.Context):
        server = Server.read_from_json(ctx.guild)
        embed = self._list_config(server, ctx)
        await ctx.reply(embed=embed)

    # Qué asco me da este comando
    @commands.hybrid_command(name="configurar", description="Configura los datos del servidor")
    @owner_only()
    async def config(self, ctx: commands.Context):
        configs = [views.config.SelectRoleView("Selecciona los roles de administrador", 25),
                   views.config.SelectChannelView("Selecciona el canal de tienda"), views.config.SelectChannelView("Selecciona el canal bancario"),
                   views.config.SalarioView("Selecciona los salarios de los miembros"), views.config.SelectRoleView("Selecciona el rol de senador honorario"),
                   views.config.SelectRoleView("Selecciona el rol de esclavo"), views.config.SelectRoleView("Selecciona el rol de artista")]
        message = await ctx.reply("Iniciando configuración...")
        await sleep(0.5)

        for cfg in configs: # Paso de configuración
            await message.edit(content=f"{cfg.label}:\n", view=cfg)
            await cfg.wait()
            if cfg.abort:
                await message.delete()
                return

        # Creación del objeto servidor con la configuración dada
        server = Server(ctx.guild.id)
        server.configurado = True
        server.roles_admin = [val.id for val in configs[0].selection.values]
        server.canal_tienda = configs[1].selection.values[0].id
        server.canal_bancario = configs[2].selection.values[0].id
        server.sueldos = configs[3].d
        server.rol_senador = configs[4].selection.values[0].id
        server.rol_esclavo = configs[5].selection.values[0].id
        server.rol_artista = configs[6].selection.values[0].id

        confirm = views.config.ViewObj()
        # Embed con los cambios realizados
        embed = self._list_config(server, ctx)
        await message.edit(content="¿Continuar?", embed=embed, view=confirm)
        await confirm.wait()
        if confirm.abort:
            await message.delete()
            return

        # Finalización
        server.write_to_json()
        await message.delete()
        await ctx.reply("Hecho.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Config(bot))