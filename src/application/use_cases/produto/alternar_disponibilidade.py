from uuid import UUID

from src.domain.entities.produto import Produto
from src.domain.enums.status_produto import StatusProduto
from src.domain.exceptions import EntidadeNaoEncontradaError
from src.domain.repositories.produto_repository import ProdutoRepository


class AlternarDisponibilidadeUseCase:
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self._produto_repo = produto_repo

    def executar(self, produto_id: UUID, disponivel: bool) -> Produto:
        produto = self._produto_repo.buscar_por_id(produto_id)
        if not produto:
            raise EntidadeNaoEncontradaError("Produto não encontrado.")

        novo_status = StatusProduto.DISPONIVEL if disponivel else StatusProduto.ESGOTADO
        produto.alternar_status(novo_status)

        return self._produto_repo.atualizar(produto)