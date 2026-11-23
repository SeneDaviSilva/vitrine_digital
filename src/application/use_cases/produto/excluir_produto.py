from uuid import UUID

from src.domain.exceptions import EntidadeNaoEncontradaError
from src.domain.repositories.produto_repository import ProdutoRepository


class ExcluirProdutoUseCase:
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self._produto_repo = produto_repo

    def executar(self, produto_id: UUID) -> None:
        produto = self._produto_repo.buscar_por_id(produto_id)
        if not produto:
            raise EntidadeNaoEncontradaError("Produto não encontrado para exclusão.")

        self._produto_repo.excluir(produto_id)