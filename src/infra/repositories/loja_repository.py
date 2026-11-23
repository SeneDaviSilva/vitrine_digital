from typing import List, Optional
from uuid import UUID

from supabase import Client

from src.domain.entities.loja import Loja
from src.domain.repositories.loja_repository import LojaRepository
from src.infra.mappers.loja_mapper import LojaMapper


class SupabaseLojaRepository(LojaRepository):
    def __init__(self, client: Client) -> None:
        self._client = client
        self._tabela = "lojas"

    def salvar(self, loja: Loja) -> Loja:
        payload = LojaMapper.to_persistence(loja)
        res = self._client.table(self._tabela).insert(payload).execute()
        return LojaMapper.to_entity(res.data[0])

    def buscar_por_id(self, loja_id: UUID) -> Optional[Loja]:
        res = (
            self._client.table(self._tabela)
            .select("*")
            .eq("id", str(loja_id))
            .execute()
        )
        return LojaMapper.to_entity(res.data[0]) if res.data else None

    def buscar_por_vendedor_id(self, vendedor_id: UUID) -> Optional[Loja]:
        res = (
            self._client.table(self._tabela)
            .select("*")
            .eq("vendedor_id", str(vendedor_id))
            .execute()
        )
        return LojaMapper.to_entity(res.data[0]) if res.data else None

    def buscar_por_nome(self, nome_loja: str) -> Optional[Loja]:
        # ilike evita duplicidade por diferença de maiúsculas/minúsculas
        res = (
            self._client.table(self._tabela)
            .select("*")
            .ilike("nome_loja", nome_loja.strip())
            .execute()
        )
        return LojaMapper.to_entity(res.data[0]) if res.data else None

    def buscar_por_whatsapp(self, whatsapp: str) -> Optional[Loja]:
        res = (
            self._client.table(self._tabela)
            .select("*")
            .eq("whatsapp", whatsapp)
            .execute()
        )
        return LojaMapper.to_entity(res.data[0]) if res.data else None

    def listar_todas(self) -> List[Loja]:
        res = self._client.table(self._tabela).select("*").order("nome_loja").execute()
        return [LojaMapper.to_entity(row) for row in res.data]

    def atualizar(self, loja: Loja) -> Loja:
        payload = LojaMapper.to_persistence(loja)
        res = (
            self._client.table(self._tabela)
            .update(payload)
            .eq("id", str(loja.id))
            .execute()
        )
        return LojaMapper.to_entity(res.data[0])