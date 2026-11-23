import time
from typing import List, Optional
from uuid import UUID

from src.application.use_cases.loja.atualizar_loja import (
    ArquivoUpload,
    StorageGatewayProtocol,
)
from src.domain.entities.produto import Produto
from src.domain.exceptions import DadosInvalidosError
from src.domain.repositories.produto_repository import ProdutoRepository


class CadastrarProdutoUseCase:
    def __init__(
        self,
        produto_repo: ProdutoRepository,
        storage: StorageGatewayProtocol,
    ) -> None:
        self._produto_repo = produto_repo
        self._storage = storage

    def executar(
        self,
        loja_id: UUID,
        nome: str,
        preco: float,
        categoria: str,
        descricao: Optional[str] = None,
        imagens: Optional[List[ArquivoUpload]] = None,
    ) -> Produto:
        arquivos = imagens or []
        if len(arquivos) > 3:
            raise DadosInvalidosError("Máximo de 3 fotos permitidas por produto.")

        # Valida as regras de negócio antes de realizar qualquer upload
        produto = Produto(
            loja_id=loja_id,
            nome=nome,
            preco=preco,
            categoria=categoria,
            descricao=descricao,
        )

        urls_geradas: List[str] = []
        timestamp = int(time.time())
        for idx, arquivo in enumerate(arquivos):
            extensao = arquivo.nome.split(".")[-1]
            caminho = f"{loja_id}_{timestamp}_{idx}.{extensao}"
            url = self._storage.upload(
                caminho=caminho,
                conteudo=arquivo.conteudo,
                content_type=arquivo.content_type,
            )
            urls_geradas.append(url)

        produto.imagens_url = urls_geradas
        return self._produto_repo.salvar(produto)