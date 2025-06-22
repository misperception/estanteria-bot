from lib.checks import *
import random, discord

# Menú de acción del artista
class ArtistView(discord.ui.View):
    com_id: int
    channel: discord.TextChannel
    def __init__(self, com_id: int, channel: discord.TextChannel, message: discord.Message):
        super().__init__()
        self.com_id = com_id
        com = Commission.read_from_json(com_id)
        self.channel = channel
        self.add_item(discord.ui.Button(label="Ir a la comisión", style=discord.ButtonStyle.link, url=message.jump_url))

    @discord.ui.button(label="Enviar comisión", style=discord.ButtonStyle.green)
    async def send(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Inicia los datos del artista y la comisión
        com = Commission.read_from_json(self.com_id)
        artist = Member.read_from_json(interaction.user)
        # Desactiva el botón de enviar y espera a que se envíe la comisión
        button.disabled = True
        await interaction.message.edit(content=interaction.message.content, view=self)

        await self.channel.send(f"{interaction.user.mention}, responde a este mensaje con la comisión.", delete_after=10)
        while not (self.channel.last_message is not None and
                   self.channel.last_message.attachments != [] and
                   "image" in self.channel.last_message.attachments[0].content_type and
                   self.channel.last_message.author.id == artist.id):
            await asyncio.sleep(1)

        # Paga al artista el precio de la comisión y modifica el mensaje original de la comisión
        artist.modify_coupons(com.reward, guild=self.channel.guild)
        message = await self.channel.fetch_message(com.msg)
        await message.reply("Comisión completada.", delete_after=2)
        embed = message.embeds[0]
        embed.set_footer(text="Comisión completada")
        await message.edit(content=message.content, embed=embed, view=None)

        # Elimina la comisión del JSON y el menú de acción
        com.remove_from_json()
        await interaction.message.delete()

    @discord.ui.button(label="Abandonar comisión", style=discord.ButtonStyle.red)
    async def abandon(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Elimina los datos del artista y lo guarda en el JSON
        com = Commission.read_from_json(self.com_id)
        com.taken = False
        com.artist = 0
        com.write_to_json()

        # Responde al usuario
        await interaction.response.send_message("Comisión abandonada.", delete_after=2)

        # Elimina el campo de "Artista" y restablece el menú de la comisión
        message = await self.channel.fetch_message(com.msg)
        embed = message.embeds[0]
        embed.remove_field(1)
        view = CommissionView(com.id)
        await message.edit(content=message.content, embed=embed, view=view)
        # Borra el menú de acción del artista
        await interaction.message.delete()
# Menú de acción de la comisión
class CommissionView(discord.ui.View):
    def __init__(self, id):
        super().__init__()
        self.id = id

    # Botón de cancelar comisión
    @discord.ui.button(label="Cancelar comisión", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.id:
            await interaction.response.send_message("Pero a ti qué te pasa, ¡esta comisión no es tuya!")
        com = Commission.read_from_json(self.id)
        user = Member.read_from_json(interaction.guild.get_member(self.id))
        user.modify_coupons(com.reward, interaction.guild)
        com.remove_from_json()
        await interaction.response.send_message("Comisión cancelada.", ephemeral=True, delete_after=2)
        await interaction.message.delete()
        return

    @discord.ui.button(label="Coger comisión", style=discord.ButtonStyle.blurple)
    async def take_commission(self, interaction: discord.Interaction, button: discord.ui.Button):
        server = Server.read_from_json(interaction.guild)
        if not interaction.user.get_role(server.rol_artista):
            await interaction.response.send_message(NotArtist().response(), ephemeral=True)
            return

        com = Commission.read_from_json(self.id)
        com.artist = interaction.user.id
        com.taken = True
        com.write_to_json()

        embed = interaction.message.embeds[0]
        embed.add_field(name="Artista", value=interaction.user.mention)
        button.disabled = True
        await interaction.message.edit(content=interaction.message.content, embed=embed, view=self)

        view = ArtistView(com.id, interaction.channel, interaction.message)
        await interaction.response.send_message("Comisión cogida.", ephemeral=True, delete_after=2)
        await interaction.user.send(f"Menú de acción de la comisión *'{com.prompt}'*:", view=view)



class Cupones(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Check de canal bancario
    async def cog_check(self, ctx: commands.Context):
        s = Server.read_from_json(ctx.guild)
        if not ctx.channel.id == s.canal_bancario: raise InappropriateChannel
        return True

    # Comando que permite añadir cupones
    @commands.hybrid_command(name="cuponizar", description="Añade cupones a un miembro.")
    @discord.app_commands.describe(
        member="Miembro merecedor de los cupones",
        amount="Cantidad de cupones a añadir",
        mostrar="Mostrar o no un mensaje al añadir los cupones"
    )
    @owner_only()
    async def add_coupons(self, ctx: commands.Context, member: discord.Member, amount: int, mostrar: bool = True):
        m = Member.read_from_json(member)
        m.modify_coupons(amount, ctx.guild)
        if mostrar: await ctx.reply(
            f"{"Añadidos" if amount > 0 else "Retirados"} {abs(amount)} cupones {"a" if amount > 0 else "de"} la cuenta de {member.mention}")
        else: await ctx.reply("Hecho.", ephemeral=True, delete_after=2)

    # Comando que permite quitar cupones
    @commands.hybrid_command(name="descuponizar", description="Revoca cupones de los indignos.")
    @discord.app_commands.describe(
        member="Indigno plebeyo",
        amount="Cupones a revocar",
        mostrar="Mostrar o no un mensaje al revocar los cupones"
    )
    @owner_only()
    async def revoke_coupons(self, ctx, member: discord.Member, amount: int, mostrar: bool = True):
        await self.add_coupons(ctx, member=member, amount=-amount, mostrar=mostrar)

    # Comando que permite realizar transacciones
    @commands.hybrid_command(name="transcuponizar", description="Transfiere cupones entre la plebe.")
    @discord.app_commands.describe(member="El otro plebeyo al que regalar tus cupones", amount="Cupones a regalar")
    async def transfer(self, ctx, member: discord.Member, amount: int):
        giver = Member.read_from_json(ctx.author)
        if giver.cupones < amount: raise InsufficientCoupons
        gived = Member.read_from_json(member)
        giver.modify_coupons(-amount)
        gived.modify_coupons(amount, ctx.guild)
        await ctx.reply(f"Transferido{"s" if amount > 1 else ""} {amount} cup{"ones" if amount > 1 else "ón"}"
                        + f" de la cuenta de {ctx.author.mention} a la cuenta de {member.mention}")

    # Comando que lista todos los cupones de los miembros
    @owner_only()
    @commands.hybrid_command(name="listar", description="Lista los cupones de todos los miembros del server.")
    async def create_list(self, ctx: commands.Context):
        s = Server.read_from_json(ctx.guild)
        if s.lista_cupones != 0:
            msg = ctx.guild.get_channel(s.canal_bancario).get_partial_message(s.lista_cupones)
            await msg.delete()

        embeds = generate_list(ctx.guild)
        message = await ctx.reply(embeds=embeds)
        s.lista_cupones = message.id
        s.write_to_json()


class Tienda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Check de canal de tienda
    async def cog_check(self, ctx: commands.Context):
        s = Server.read_from_json(ctx.guild)
        if not ctx.channel.id == s.canal_tienda: raise InappropriateChannel
        return True

    @commands.hybrid_command(name="tienda", description="Muestra los artículos que se pueden comprar.")
    async def shop(self, ctx):
        items = read_json("tienda.json")
        embed = discord.Embed(
            color=discord.Color.green(),
            title="Tienda",
            timestamp=datetime.datetime.now()
        )
        for item in items: embed.add_field(
            name=item["nombre"],
            value=f"{item["descripcion"]}\n{item["precio"]} Guydocup{"ón" if item["precio"] == 1 else "ones"}."
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_group(name="comprar", description="Compra un artículo de la tienda.")
    async def buy(self, ctx):
        await ctx.reply("Pero di qué vas a comprar, cacho burro.", ephemeral=True)

    @buy.command(name="café", description="Cafeína.")
    @has_coupons(1)
    async def cafe(self, ctx: commands.Context):
        fun_val = random.randint(1,100)
        victima = Member.read_from_json(ctx.author)
        victima.modify_coupons(-1, ctx.guild)
        await ctx.send(f"{"En estos momentos la máquina de café está rota, por favor vuelva a intentarlo." 
        if fun_val == 100 else ":coffee:"}", ephemeral=True)

    @buy.command(name="esclavitud", description="Esclaviza a un plebeyo.")
    @discord.app_commands.describe(member="Miembro a esclavizar.")
    @has_coupons(3)
    async def esclavizar(self, ctx: commands.Context, member: discord.Member):
        # No intentes esclavizar a Guydo, mala idea
        if member.top_role > ctx.guild.get_member(ctx.bot.user.id).top_role:
            await ctx.reply("No soy lo suficientemente poderoso como para esclavizar a este respetable individuo.",ephemeral=True)
            return

        m = Member.read_from_json(member)
        s = Server.read_from_json(member.guild)
        # Cobramos la transacción
        user = Member.read_from_json(ctx.author)
        user.modify_coupons(-3, ctx.guild)
        # Iniciamos la fecha de hoy para saber la fecha de final de esclavitud
        time = datetime.datetime.now()
        # Comprobamos si el usuario ya es un esclavo para cargar la fecha de final
        val = m.slave["status"]
        if val:
            time = datetime.datetime.fromtimestamp(m.slave["end"])
            # Cancelamos la tarea de desesclavizar anterior
            m.cancel_member_task('slave')
        # Sumamos un día a la fecha de fin
        time += datetime.timedelta(days=1)

        m.change_status(m.slave, True, end=time)
        await member.add_roles(member.guild.get_role(s.rol_esclavo))
        # Crea una tarea de eliminar el rol de esclavo 1 día después
        asyncio.create_task(
            self._desesclavizar(member, time=(time - datetime.datetime.now()).total_seconds()),
            name=f"{member.id}-slave")
        await ctx.reply(f"Ahora {member.mention} es un esclavo. Qué asco.")

    # Función auxiliar asíncrona para desesclavizar, se puede llamar sola o ejecutar mediante asyncio
    async def _desesclavizar(self, member: discord.Member, time: float = 0):
        await asyncio.sleep(time)
        m = Member.read_from_json(member)
        s = Server.read_from_json(member.guild)

        m.change_status(tag=m.slave, mode=False)
        await member.remove_roles(member.guild.get_role(s.rol_esclavo))
        if time == 0: m.cancel_member_task('slave')

    @buy.command(name="liberación", description="Libera a un maldito esclavo.")
    @discord.app_commands.describe(member="Esclavo asqueroso al que liberar.")
    @has_coupons(3)
    async def desesclavizar(self, ctx, member: discord.Member):
        if member.top_role > ctx.guild.get_member(ctx.bot.user.id).top_role:
            await ctx.reply("Alguien tan poderoso no puede ser un esclavo",ephemeral=True)
            return
        m = Member.read_from_json(member)
        val = m.slave["status"]
        if not val:
            await ctx.reply("Ese ya está liberado, que no te enteras.", ephemeral=True)
            return
        user = Member.read_from_json(ctx.author)
        user.modify_coupons(-3, ctx.guild)
        await self._desesclavizar(member)
        await ctx.reply(f"{member.mention} es libre, qué pena...")

    @buy.command(name="senador", description="Adquiere y saborea derechos durante 1 día (solo 2 senadores a la vez).")
    @has_coupons(8)
    async def privilegiar(self, ctx: commands.Context):
        member = ctx.author
        # No creo que Guydo quiera ser senador honorario la verdad
        if member.top_role > ctx.guild.get_member(ctx.bot.user.id).top_role:
            await ctx.reply("Esta persona ya tiene todos los privilegios del mundo.",ephemeral=True)
            return
        # Leemos los valores necesarios
        m = Member.read_from_json(member)
        s = Server.read_from_json(member.guild)
        # Si hay ya 2 senadores honorarios, no puede haber más
        if not s.senadores_honorarios < 2:
            await ctx.reply("Ya hay más que suficientes plebeyos con síndrome de superioridad, largo de aquí.")
            return
        val = m.senador["status"]
        # Si ya eres senador honorario, conténtate
        if val:
            await ctx.reply("Ya tienes derechos, no quieras comprar más aún.", ephemeral=True)
            return
        # Cobramos al usuario y le hacemos senador
        user = Member.read_from_json(ctx.author)
        user.modify_coupons(-8, ctx.guild)
        s.senadores_honorarios += 1
        s.write_to_json()
        m.change_status(m.senador, True, end=(datetime.datetime.now() + datetime.timedelta(days=1)))
        await member.add_roles(member.guild.get_role(s.rol_senador))
        # Crea una tarea de eliminar el rol de senador honorario 1 día después
        asyncio.create_task(
            self._desprivilegiar(member, time=datetime.timedelta(days=1).total_seconds()),
            name=f"{member.id}-senador")
        await ctx.reply("Felicidades por tus derechos recién adquiridos.")

    # Función auxiliar asíncrona para quitar privilegios de senador, se llama mediante asyncio
    async def _desprivilegiar(self, member: discord.Member, time: float):
        await asyncio.sleep(time)
        m = Member.read_from_json(member)
        s = Server.read_from_json(member.guild)
        m.change_status(m.senador, False)
        s.senadores_honorarios-=1
        s.write_to_json()
        await member.remove_roles(member.guild.get_role(s.rol_senador))

    @buy.command(name="comisión", description="Soborna a un artista para que dibuje por ti. Precio variable.")
    @discord.app_commands.describe(price="Precio de la comisión.", prompt="Detalles de la comisión.")
    @has_commission()
    async def comision(self, ctx: commands.Context, price: int, prompt: str):
        user = Member.read_from_json(ctx.author)
        if user.cupones < price: raise InsufficientCoupons
        if price <= 0: raise InvalidPrice
        # Cobramos la comisión temporalmente
        user.modify_coupons(-price, ctx.guild)
        com = Commission(user.id, prompt, price)

        # Embed de la comisión
        com_embed = discord.Embed(title=f"'{prompt}'", timestamp=datetime.datetime.now())
        com_embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        com_embed.add_field(name="Precio", value=f"{price} Guydocup{"ones" if price > 1 else "ón"}")

        # Creamos el menú de acción de la comisión
        view=CommissionView(user.id)
        message = await ctx.send(embed=com_embed, view=view)
        com.msg = message.id
        com.write_to_json()
        await ctx.reply("Comisión mandada.", ephemeral=True, delete_after=2)

async def setup(bot):
    await bot.add_cog(Cupones(bot))
    await bot.add_cog(Tienda(bot))
