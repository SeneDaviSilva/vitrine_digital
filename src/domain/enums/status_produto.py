from enum import Enum


class StatusProduto(str, Enum):
    DISPONIVEL = "disponivel"
    ESGOTADO = "esgotado"
    OCULTO = "oculto"