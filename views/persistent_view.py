import discord.ui
from lib.shelflib import read_json, write_json
from discord.ext import commands
from random import getrandbits

namespace = {}

# Decorador de clase para añadir clases persistentes a un diccionario namespace
def add_namespace(cls):
    class_dict = {cls.__name__: cls}
    namespace.update(class_dict)
    return cls

def remove_by_id(id: int):
    data = read_json("data/views.json")
    data.pop(str(id))
    write_json(data, "data/views.json")

class PersistentView(discord.ui.View):
    name: str
    view_id: int

    def __init__(self, view_id: int | None):
        super().__init__(timeout=None)
        self.name = type(self).__name__
        self.view_id = view_id or getrandbits(32)

    def to_dict(self) -> dict:
        d = {str(self.view_id): {"name": self.name}}
        return d

    def write_to_json(self):
        data = read_json("data/views.json")
        data.update(self.to_dict())
        write_json(data, "data/views.json")

    def remove_from_json(self):
        data = read_json("data/views.json")
        data.pop(str(self.view_id))
        write_json(data, "data/views.json")

    # Función de leer de diccionario de vista (para overriding)
    @classmethod
    def read_from_dict(cls, d: dict, bot: commands.Bot, id: int):
        pass