from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from src.domain.entities.vendedor import Vendedor


class VendedorRepository(ABC):
    @abstractmethod
    def salvar(self, vendedor: Vendedor) -> Vendedor:
        pass

    @abstractmethod
    def buscar_por_id(self, vendedor_id: UUID) -> Optional[Vendedor]:
        pass

    @abstractmethod
    def buscar_por_email(self, email: str) -> Optional[Vendedor]:
        pass

    @abstractmethod
    def atualizar(self, vendedor: Vendedor) -> Vendedor:
        pass