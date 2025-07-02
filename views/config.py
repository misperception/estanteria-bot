from lib.checks import *
import discord.ui as ui

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