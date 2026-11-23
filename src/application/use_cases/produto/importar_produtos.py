from typing import List
from uuid import UUID

from src.application.parsers.texto_bloco_parser import TextoBlocoParser
from src.domain.entities.produto import Produto
from src.domain.repositories.produto_repository import ProdutoRepository


class ImportarProdutosUseCase:
    def __init__(self, produto_repo: ProdutoRepository) -> None:
        self._produto_repo = produto_repo

    def executar(self, loja_id: UUID, texto_bruto: str) -> List[Produto]:
        produtos = TextoBlocoParser.parse(texto_bruto=texto_bruto, loja_id=loja_id)
        return self._produto_repo.salvar_em_lote(produtos)