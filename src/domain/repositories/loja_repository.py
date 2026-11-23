from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.loja import Loja


class LojaRepository(ABC):
    @abstractmethod
    def salvar(self, loja: Loja) -> Loja:
        pass

    @abstractmethod
    def buscar_por_id(self, loja_id: UUID) -> Optional[Loja]:
        pass

    @abstractmethod
    def buscar_por_vendedor_id(self, vendedor_id: UUID) -> Optional[Loja]:
        pass

    @abstractmethod
    def buscar_por_nome(self, nome_loja: str) -> Optional[Loja]:
        pass

    @abstractmethod
    def buscar_por_whatsapp(self, whatsapp: str) -> Optional[Loja]:
        pass

    @abstractmethod
    def listar_todas(self) -> List[Loja]:
        pass

    @abstractmethod
    def atualizar(self, loja: Loja) -> Loja:
        pass