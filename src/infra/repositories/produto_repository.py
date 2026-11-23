from typing import List, Optional
from uuid import UUID

from supabase import Client

from src.domain.entities.produto import Produto
from src.domain.enums.status_produto import StatusProduto
from src.domain.repositories.produto_repository import ProdutoRepository
from src.infra.mappers.produto_mapper import ProdutoMapper


class SupabaseProdutoRepository(ProdutoRepository):
    def __init__(self, client: Client) -> None:
        self._client = client
        self._tabela = "produtos"

    def salvar(self, produto: Produto) -> Produto:
        payload = ProdutoMapper.to_persistence(produto)
        res = self._client.table(self._tabela).insert(payload).execute()
        return ProdutoMapper.to_entity(res.data[0])

    def salvar_em_lote(self, produtos: List[Produto]) -> List[Produto]:
        payloads = [ProdutoMapper.to_persistence(p) for p in produtos]
        res = self._client.table(self._tabela).insert(payloads).execute()
        return [ProdutoMapper.to_entity(row) for row in res.data]

    def buscar_por_id(self, produto_id: UUID) -> Optional[Produto]:
        res = (
            self._client.table(self._tabela)
            .select("*")
            .eq("id", str(produto_id))
            .execute()
        )
        return ProdutoMapper.to_entity(res.data[0]) if res.data else None

    def listar_por_loja(self, loja_id: UUID, apenas_visiveis: bool = False) -> List[Produto]:
        query = (
            self._client.table(self._tabela)
            .select("*")
            .eq("loja_id", str(loja_id))
        )
        if apenas_visiveis:
            query = query.eq("status", StatusProduto.DISPONIVEL.value)

        res = query.execute()
        return [ProdutoMapper.to_entity(row) for row in res.data]

    def atualizar(self, produto: Produto) -> Produto:
        payload = ProdutoMapper.to_persistence(produto)
        res = (
            self._client.table(self._tabela)
            .update(payload)
            .eq("id", str(produto.id))
            .execute()
        )
        return ProdutoMapper.to_entity(res.data[0])

    def excluir(self, produto_id: UUID) -> None:
        self._client.table(self._tabela).delete().eq("id", str(produto_id)).execute()