from asyncio import sleep
import discord.ui as ui
from lib.checks import *

# Desplegable de selección de rol
class SelectRole(ui.RoleSelect):
    def __init__(self, label, maxvals):
        super().__init__(placeholder=label, max_values=maxvals, min_values=1)
        self.default_values = []

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

# Desplegable de selección de canal
class SelectChannel(ui.ChannelSelect):
    def __init__(self, label, maxvals):
        super().__init__(placeholder=label, max_values=maxvals, min_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

# Modal de selección de salario
class SalarioModal(ui.Modal, title="Salario"):
    def __init__(self, role_name):
        super().__init__()
        self.salario.label = f"Salario de {role_name}:"
        self.abort = False

    salario = ui.TextInput(label="WIP", style=discord.TextStyle.short, placeholder="1", default="1")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

    async def on_error(self, interaction: discord.Interaction, error):
        self.abort = True
        await interaction.response.defer(ephemeral=True)

# Objeto genérico con botones de continuar y de cancelar
class ViewObj(ui.View):
    def __init__(self):
        super().__init__()
        self.abort = False

    async def disable(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(content=interaction.message.content, view=self)

    @ui.button(label="Cancelar", style=discord.ButtonStyle.red, row=2)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Cancelando configuración...", ephemeral=True, delete_after=2)
        self.abort = True
        await self.disable(interaction)
        self.stop()

    # Función auxiliar presente para overriding
    async def _cont(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        await self.disable(interaction)
        self.stop()

    @ui.button(label="Continuar", style=discord.ButtonStyle.green, row=2)
    async def cont(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self._cont(interaction)

# Menú de selección de rol
class SelectRoleView(ViewObj):
    def __init__(self, label, maxvals=1):
        super().__init__()
        self.label = label
        self.selection = SelectRole(label, maxvals)
        self.add_item(self.selection)

    async def _cont(self, interaction: discord.Interaction):
        if not self.selection.values:
            await interaction.response.send_message(InvalidSelection().response(), ephemeral=True)
            return
        await super()._cont(interaction)

# Menú de selección de canal
class SelectChannelView(ViewObj):
    def __init__(self, label, maxvals=1):
        super().__init__()
        self.label = label
        self.selection = SelectChannel(label, maxvals)
        self.add_item(self.selection)

    async def _cont(self, interaction: discord.Interaction):
        if not self.selection.values:
            await interaction.response.send_message(InvalidSelection().response(), ephemeral=True)
            return
        await super()._cont(interaction)

# Menú de configuración de salarios
class SalarioView(ViewObj):
    # Función auxiliar que inicializa el campo de selección de rol
    def _init_field(self):
        if hasattr(self, "rol"): self.remove_item(self.rol)
        self.rol = SelectRole("Selecciona un rol", maxvals=1)
        self.add_item(self.rol)

    def __init__(self, label):
        super().__init__()
        self._init_field()
        self.d = {}
        self.label = label

    # Función que añade un diccionario {id_rol: salario} al diccionario del menú y devuelve la selección
    async def _add_to_d(self, interaction: discord.Interaction):
        if not self.rol.values: raise InvalidSelection
        rol = self.rol.values[0]
        id = rol.id
        modal = SalarioModal(rol.name)

        await interaction.response.send_modal(modal)
        await modal.wait()

        d = {id: int(modal.salario.value)}
        self._init_field() # Reinicia el campo de selección
        self.d.update(d)
        return rol, modal.salario.value # Devuelve el rol y el salario para estilizar el mensaje

    # Botón que implementa la función anterior y actualiza el mensaje
    @ui.button(label="Añadir salario", style=discord.ButtonStyle.blurple, row=2)
    async def add_to_d(self, interaction: discord.Interaction, button: ui.Button):
        try: rol, n = await self._add_to_d(interaction)
        except InvalidSelection as e:
            await interaction.response.send_message(e.response(), ephemeral=True)
            return
        x = lambda i: f"{rol.mention}: {i} Guydocup{"ón" if i==1 else "ones"}."
        msg = interaction.message.content + "\n" + x(n)
        await interaction.message.edit(content=msg, view=self)

    # Sobrescritura de la función del botón continuar para obligar a escoger al menos un rol
    async def _cont(self, interaction):
        if self.d == {}:
            try: await self._add_to_d(interaction)
            except InvalidSelection as e:
                await interaction.response.send_message(e.response(), ephemeral=True)
                return
            await interaction.response.defer(ephemeral=True)
        await super()._cont(interaction)



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
        configs = [SelectRoleView("Selecciona los roles de administrador", 25),
                   SelectChannelView("Selecciona el canal de tienda"), SelectChannelView("Selecciona el canal bancario"),
                   SalarioView("Selecciona los salarios de los miembros"), SelectRoleView("Selecciona el rol de senador honorario"),
                   SelectRoleView("Selecciona el rol de esclavo"), SelectRoleView("Selecciona el rol de artista")]
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

        confirm = ViewObj()
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