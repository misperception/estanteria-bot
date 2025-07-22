from lib.checks import *
from views.persistent_view import PersistentView, remove_by_id
# Menú de acción del artista
class ArtistView(PersistentView):
    com_id: int # ID del mensaje de la comisión
    channel: discord.TextChannel # Canal de la comisión
    parent_id: str

    def __init__(self, com_id: int, parent_id: str, channel: discord.TextChannel, id: str = None):
        super().__init__(id)
        self.com_id = com_id
        self.channel = channel
        self.parent_id = parent_id
        message = channel.get_partial_message(com_id)
        self.add_item(discord.ui.Button(label="Ir a la comisión", style=discord.ButtonStyle.link, url=message.jump_url))

    def to_dict(self):
        d = super().to_dict()
        d[self.id].update({
            "com_id": self.com_id,
            "channel": self.channel.id,
            "parent_id": self.parent_id
        })
        return d

    @classmethod
    def read_from_dict(cls, d: dict, id: str, bot: commands.Bot):
        return cls(
            com_id=d["com_id"],
            parent_id=d["parent_id"],
            channel=bot.get_channel(d["channel"]),
            id=id
        )

    @discord.ui.button(label="Enviar comisión", style=discord.ButtonStyle.green, custom_id='artview:send')
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Inicia los datos del artista y la comisión
        com = Commission.read_from_json(self.com_id)
        guild = self.channel.guild
        artist = Member.read_from_json(guild.get_member(interaction.user.id))
        # Desactiva el botón de enviar y espera a que se envíe la comisión
        button.disabled = True
        await interaction.message.edit(content=interaction.message.content, view=self)

        await self.channel.send(f"{interaction.user.mention}, responde al mensaje de la comisión con la comisión completada.", delete_after=10)
        reply = self.channel.last_message
        while (reply is None or
               reply.attachments == [] or
                   "image" not in reply.attachments[0].content_type or
               reply.author.id != artist.id or
               reply.reference is None or
               reply.reference.message_id != com.id):
            await asyncio.sleep(1)
            reply = self.channel.last_message

        # Paga al artista el precio de la comisión y modifica el mensaje original de la comisión
        artist.modify_coupons(com.reward)
        message = await self.channel.fetch_message(com.id)
        await message.reply("Comisión completada.", delete_after=2)
        embed = message.embeds[0]
        embed.set_image(url=reply.attachments[0].url)
        embed.set_footer(text="Comisión completada")
        await message.edit(content=message.content, embed=embed, view=None)

        # Elimina la comisión del JSON y el menú de acción
        com.remove_from_json()
        await interaction.message.delete()
        self.remove_from_json()
        remove_by_id(self.parent_id)

    @discord.ui.button(label="Abandonar comisión", style=discord.ButtonStyle.red, custom_id='artview:abandon')
    async def abandon(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Elimina los datos del artista y lo guarda en el JSON
        com = Commission.read_from_json(self.com_id)
        com.taken = False
        com.artist = 0
        com.write_to_json()

        # Responde al usuario
        await interaction.response.send_message("Comisión abandonada.", delete_after=2)

        # Elimina el campo de "Artista" y restablece el menú de la comisión
        message = await self.channel.fetch_message(com.id)
        embed = message.embeds[0]
        embed.remove_field(1)
        view = CommissionView(com.id, self.parent_id)
        await message.edit(content=message.content, embed=embed, view=view)
        # Borra el menú de acción del artista
        await interaction.message.delete()
        self.remove_from_json()

# Menú de acción de la comisión
class CommissionView(PersistentView):
    msg_id: int # Id del mensaje
    child_id: str | None

    def __init__(self, msg_id, id: str = None):
        super().__init__(id)
        self.msg_id = msg_id
        self.child_id = None

    # Botón de cancelar comisión
    @discord.ui.button(label="Cancelar comisión", style=discord.ButtonStyle.red, custom_id='comview:cancel')
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        com = Commission.read_from_json(self.msg_id)
        if interaction.user.id != com.author:
            await interaction.response.send_message("Pero a ti qué te pasa, ¡esta comisión no es tuya!")
        user = Member.read_from_json(interaction.guild.get_member(com.author))
        user.modify_coupons(com.reward)
        com.remove_from_json()
        self.remove_from_json()
        if self.child_id: remove_by_id(self.child_id)
        await interaction.response.send_message("Comisión cancelada.", ephemeral=True, delete_after=2)
        await interaction.message.delete()
        return

    @discord.ui.button(label="Coger comisión", style=discord.ButtonStyle.blurple, custom_id='comview:accept')
    async def take_commission(self, interaction: discord.Interaction, button: discord.  ui.Button):
        server = Server.read_from_json(interaction.guild)
        if not interaction.user.get_role(server.rol_artista):
            await interaction.response.send_message(NotArtist().response(), ephemeral=True)
            return

        com = Commission.read_from_json(self.msg_id)
        com.artist = interaction.user.id
        com.taken = True
        com.write_to_json()

        embed = interaction.message.embeds[0]
        embed.add_field(name="Artista", value=interaction.user.mention)
        button.disabled = True
        await interaction.message.edit(content=interaction.message.content, embed=embed, view=self)

        view = ArtistView(com_id=self.msg_id, parent_id=self.id, channel=interaction.channel)
        self.child_id = view.id
        view.write_to_json()
        self.write_to_json()

        await interaction.response.send_message("Comisión cogida.", ephemeral=True, delete_after=2)
        await interaction.user.send(f"Menú de acción de la comisión *'{com.prompt}'*:", view=view)

    def to_dict(self):
        d = super().to_dict()
        d[self.id].update({
            "msg_id": self.msg_id,
            "child_id": self.child_id
        })
        return d

    @classmethod
    def read_from_dict(cls, d: dict, id: str, bot: commands.Bot):
        return cls(
            msg_id=d["msg_id"],
            id=id
        )