import discord, json, os, datetime, asyncio

# Clase genérica con métodos de escritura
class Writeable:
    def __init__(self, id):
        self.id = id

    def to_dict(self) -> dict:
        d = vars(self).copy()
        d.pop('id')
        return {str(self.id): d}

    def write_to_json(self, path: str):
        data = read_json(path)
        data.update(self.to_dict())
        write_json(data, path)

    def remove_from_json(self, path):
        data = read_json(path)
        data.pop(str(self.id))
        write_json(data, path)

    @classmethod
    def _read_from_json(cls, obj, path: str):
        id = obj.id
        data = read_json(path)
        if not str(id) in data:
            return None
        d = data[str(id)]
        for key in d:
            setattr(obj, key, d[key])
        return obj

# Clase servidor con la configuración necesaria
class Server(Writeable):
    id: int
    configurado: bool
    roles_admin: list[int]
    canal_tienda: int
    canal_bancario: int
    sueldos: {int: int}
    rol_senador: int
    rol_esclavo: int
    rol_artista: int
    lista_cupones: int
    senadores_honorarios: int
    investigaciones: int

    def __init__(self, id: int):
        super().__init__(id)
        self.configurado = False
        self.roles_admin = []
        self.canal_tienda = 0
        self.canal_bancario = 0
        self.sueldos = None
        self.rol_senador = 0
        self.rol_esclavo = 0
        self.rol_artista = 0
        self.lista_cupones = 0
        self.senadores_honorarios = 0
        self.investigaciones = 0

    def write_to_json(self, path: str = "data/server.json"):
        super().write_to_json(path)

    @classmethod
    def read_from_json(cls, guild: discord.Guild):
        obj = cls(guild.id)
        s = cls._read_from_json(obj=obj, path="data/server.json")
        if s is None:
            s = cls(guild.id)
            s.write_to_json()
        return s

# Clase miembro con los datos requeridos
class Member(Writeable):
    id: int
    cupones: int
    slave: {bool, int}
    senador: {bool, int}
    admin: bool
    salario: int

    def __init__(self, member: discord.Member | None, server: Server | None):
        super().__init__(member.id if member else 0)
        self.cupones = 0
        self.slave = {"status": False, "end": 0}
        self.senador = {
            "status": member.get_role(server.rol_senador) is not None if member and server else False,
            "end": None
        }
        self.admin = (({e.id for e in member.roles} & set(server.roles_admin))!= set()) if member and server else False
        salarios = [salario for id, salario in server.sueldos.items() if int(id) in [rol.id for rol in member.roles]]
        self.salario = max(salarios) if salarios != [] else 0

    def write_to_json(self, path: str = "data/members.json"):
        super().write_to_json(path)

    @classmethod
    def read_from_json(cls, member: discord.Member):
        obj = cls(member, Server.read_from_json(member.guild))
        m = cls._read_from_json(obj=obj, path="data/members.json")
        if m is None:
            s = Server.read_from_json(member.guild)
            m = cls(member, s)
            m.write_to_json()
        return m

    # Método para hacer transacción de cupones
    def modify_coupons(self, amount: int, guild: discord.Guild = None):
        self.cupones += amount
        self.write_to_json()
        if guild:
            self.cancel_member_task("refresh")
            asyncio.create_task(refresh_list(guild), name=f"{self.id}-refresh")

    def change_status(self, tag, mode: bool, end: datetime.datetime | None = None):
        if mode:
            tag["status"] = True
            end = end
            tag["end"] = int(end.timestamp())
            self.write_to_json()
        else:
            tag["status"] = False
            tag["end"] = 0
            self.write_to_json()

    def cancel_member_task(self, tag: str):
        for task in asyncio.all_tasks():
            if task.get_name() == f"{self.id}-{tag}":
                task.cancel()
                break

# Clase comisión con los datos pertinentes
class Commission(Writeable):
    id: int
    prompt: str
    reward: int
    taken: bool
    msg: int
    artist: int

    def __init__(self, id, prompt, reward):
        super().__init__(id)
        self.prompt = prompt
        self.taken = False
        self.reward = reward
        self.msg = 0
        self.artist = 0

    def write_to_json(self, path: str = "data/comisiones.json"):
        super().write_to_json(path)

    @classmethod
    def read_from_json(cls, id: int):
        obj = cls(id, '', 0)
        c = cls._read_from_json(obj=obj, id=id, path="data/comisiones.json")
        return c

    def remove_from_json(self, path: str = "data/comisiones.json"):
        super().remove_from_json(path)


# Función auxiliar para crear un JSON
def init_file(path: str):
    if os.path.isfile(path): return
    write_json({}, path)

# Función auxiliar para escribir al JSON
def write_json(data, path: str):
    s = json.dumps(data, indent=4)
    with open(path, 'w') as file:
        file.write(s)

# Función auxiliar para leer del JSON
def read_json(path: str):
    with open(path, 'r') as file:
        data = json.load(file)
    return data

# Método auxiliar para generar la lista de cupones
def generate_list(guild: discord.Guild):
    embeds = []
    data = read_json("data/members.json")
    items = list(data.items())
    # Inicialización de los embeds
    for i in range(len(items)//25 + 1):
        # Creación del esqueleto del embed
        embeds.append(discord.Embed(
            title="Guydocupones",
            color=discord.Color.green(),
            timestamp=datetime.datetime.now()
        ))
    # Creación de campos por cada usuario
    for i in range(len(items)):
        key, val = items[i]
        embeds[i//25].add_field(name=guild.get_member(int(key)).display_name, value=val["cupones"], inline=False)
    return embeds

# Método auxiliar para refrescar la lista de cupones
async def refresh_list(guild: discord.Guild):
    s = Server.read_from_json(guild)
    if s.lista_cupones == 0: return
    msg = await guild.get_channel(s.canal_bancario).fetch_message(s.lista_cupones)
    await msg.edit(embeds=generate_list(guild))