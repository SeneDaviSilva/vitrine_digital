from enum import Enum


class TipoUsuario(str, Enum):
    ADMIN_MASTER = "admin_master"
    LOJISTA = "lojista"