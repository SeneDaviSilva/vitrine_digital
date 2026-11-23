from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from src.domain.entities.produto import Produto


class ProdutoRepository(ABC):
    @abstractmethod
    def salvar(self, produto: Produto) -> Produto:
        pass

    @abstractmethod
    def salvar_em_lote(self, produtos: List[Produto]) -> List[Produto]:
        pass

    @abstractmethod
    def buscar_por_id(self, produto_id: UUID) -> Optional[Produto]:
        pass

    @abstractmethod
    def listar_por_loja(self, loja_id: UUID, apenas_visiveis: bool = False) -> List[Produto]:
        pass

    @abstractmethod
    def atualizar(self, produto: Produto) -> Produto:
        pass

    @abstractmethod
    def excluir(self, produto_id: UUID) -> None:
        pass