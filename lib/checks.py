from discord.ext import commands
from lib.shelflib import *


# Errores
class ShelfError(commands.CheckFailure):
    def response(self):
        return "Error genérico número 90219032."
class InsufficientCoupons(ShelfError):
    def response(self):
        return "Te faltan Guydocupones, puto pobre."
class NotAdmin(ShelfError):
    def response(self):
        return "No tienes derechos suficientes para hacer esto."
class InappropriateChannel(ShelfError):
    def response(self):
        return "¿¡DELANTE DE UN MENOR!?"
class NotOwner(ShelfError):
    def response(self):
        return "\"No tienes mis derechos.\" - Guydo"
class InvalidSelection(ShelfError):
    def response(self):
        return "Selecciona algo, burro."
class NoConfig(ShelfError):
    def response(self):
        return "Espera que el viejo tiene que trabajar."
class WIP(ShelfError):
    def response(self):
        return "OYE QUE ESTO NO ESTÁ ACABADO, TIRA POR AHÍ."
class ExistentCommission(ShelfError):
    def response(self):
        return "Ya está bien de explotar artistas, ve a tocar hierba anda."
class NotArtist(ShelfError):
    def response(self):
        return "Afortunadamente, no eres un artista."
class InvalidPrice(ShelfError):
    def response(self):
        return "Basta ya de robarle a la gente, ponte a trabajar anda."

# Checks
## Check de propietario
def owner_only():
    def is_owner(ctx: commands.Context):
        if ctx.author == ctx.guild.owner: return True
        raise NotOwner
    return commands.check(is_owner)

## Check de permisos de admin
def admin_only():
    def is_admin(ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator: raise NotAdmin
        return True

    return commands.check(is_admin)

## Check de coste
def has_coupons(cost):
    def coupons(ctx: commands.Context):
        m = Member.read_from_json(ctx.author)
        c = m.cupones
        if cost > c: raise InsufficientCoupons
        return True

    return commands.check(coupons)

def has_commission():
    def com_exists(ctx: commands.Context):
        user = Member.read_from_json(ctx.author)
        if Commission.read_from_json(user.id) is not None: raise ExistentCommission
        return True
    return commands.check(com_exists)

## Check de comando sin terminar
def wip():
    def err(ctx: commands.Context):
        raise WIP
    return commands.check(err)

