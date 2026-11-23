from enum import Enum


class StatusPedido(str, Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    EM_PREPARO = "em_preparo"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"