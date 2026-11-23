import time
from typing import List, Optional
from uuid import UUID

from src.application.use_cases.loja.atualizar_loja import (
    ArquivoUpload,
    StorageGatewayProtocol,
)
from src.domain.entities.produto import Produto
from src.domain.exceptions import DadosInvalidosError, EntidadeNaoEncontradaError
from src.domain.repositories.produto_repository import ProdutoRepository


class EditarProdutoUseCase:
    def __init__(
        self,
        produto_repo: ProdutoRepository,
        storage: StorageGatewayProtocol,
    ) -> None:
        self._produto_repo = produto_repo
        self._storage = storage

    def executar(
        self,
        produto_id: UUID,
        nome: str,
        preco: float,
        categoria: str,
        descricao: Optional[str] = None,
        novas_imagens: Optional[List[ArquivoUpload]] = None,
    ) -> Produto:
        produto_atual = self._produto_repo.buscar_por_id(produto_id)
        if not produto_atual:
            raise EntidadeNaoEncontradaError("Produto não encontrado.")

        arquivos = novas_imagens or []
        if len(arquivos) > 3:
            raise DadosInvalidosError("Máximo de 3 fotos permitidas por produto.")

        urls_finais = produto_atual.imagens_url
        if arquivos:
            urls_finais = []
            timestamp = int(time.time())
            for idx, arquivo in enumerate(arquivos):
                extensao = arquivo.nome.split(".")[-1]
                caminho = f"{produto_atual.loja_id}_edit_{timestamp}_{idx}.{extensao}"
                url = self._storage.upload(
                    caminho=caminho,
                    conteudo=arquivo.conteudo,
                    content_type=arquivo.content_type,
                )
                urls_finais.append(url)

        produto_atualizado = Produto(
            id=produto_atual.id,
            loja_id=produto_atual.loja_id,
            nome=nome,
            preco=preco,
            categoria=categoria,
            descricao=descricao,
            imagens_url=urls_finais,
            status=produto_atual.status,
            created_at=produto_atual.created_at,
        )

        return self._produto_repo.atualizar(produto_atualizado)