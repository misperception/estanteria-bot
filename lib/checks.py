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
class NotArtist(ShelfError):
    def response(self):
        return "Afortunadamente, no eres un artista."
class InvalidPrice(ShelfError):
    def response(self):
        return "Basta ya de robarle a la gente, ponte a trabajar anda."
class InvestigationExists(ShelfError):
    def response(self):
        return "El DIC está ya muy ocupado, ve a dar por culo a otra parte."

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

## Check de comando sin terminar
def wip():
    def err(ctx):
        raise WIP
    return commands.check(err)

def investigation_not_available():
    def err(ctx: commands.Context):
        s = Server.read_from_json(ctx.guild)
        if s.investigaciones > 0: raise InvestigationExists
        return True
    return commands.check(err)
