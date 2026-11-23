from typing import Optional
from uuid import UUID

from supabase import Client

from src.domain.entities.vendedor import Vendedor
from src.domain.repositories.vendedor_repository import VendedorRepository
from src.infra.mappers.vendedor_mapper import VendedorMapper


class SupabaseVendedorRepository(VendedorRepository):
    def __init__(self, client: Client) -> None:
        self._client = client
        self._tabela = "vendedores"

    def salvar(self, vendedor: Vendedor) -> Vendedor:
        payload = VendedorMapper.to_persistence(vendedor)
        res = self._client.table(self._tabela).insert(payload).execute()
        return VendedorMapper.to_entity(res.data[0])

    def buscar_por_id(self, vendedor_id: UUID) -> Optional[Vendedor]:
        res = (
            self._client.table(self._tabela)
            .select("*")
            .eq("id", str(vendedor_id))
            .execute()
        )
        return VendedorMapper.to_entity(res.data[0]) if res.data else None

    def buscar_por_email(self, email: str) -> Optional[Vendedor]:
        res = (
            self._client.table(self._tabela)
            .select("*")
            .eq("email", email.strip().lower())
            .execute()
        )
        return VendedorMapper.to_entity(res.data[0]) if res.data else None

    def atualizar(self, vendedor: Vendedor) -> Vendedor:
        payload = VendedorMapper.to_persistence(vendedor)
        res = (
            self._client.table(self._tabela)
            .update(payload)
            .eq("id", str(vendedor.id))
            .execute()
        )
        return VendedorMapper.to_entity(res.data[0])