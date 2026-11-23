from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from src.domain.entities.vendedor import Vendedor
from src.domain.enums.tipo_usuario import TipoUsuario


class VendedorMapper:
    @staticmethod
    def to_entity(row: Dict[str, Any]) -> Vendedor:
        created_at = (
            datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else None
        )
        return Vendedor(
            id=UUID(str(row["id"])),
            nome=row["nome"],
            email=row["email"],
            senha_hash=row["senha_hash"],
            tipo_usuario=TipoUsuario(row.get("tipo_usuario", TipoUsuario.LOJISTA.value)),
            created_at=created_at,
        )

    @staticmethod
    def to_persistence(vendedor: Vendedor) -> Dict[str, Any]:
        dados: Dict[str, Any] = {
            "nome": vendedor.nome,
            "email": vendedor.email,
            "senha_hash": vendedor.senha_hash,
            "tipo_usuario": vendedor.tipo_usuario.value,
        }
        if vendedor.id:
            dados["id"] = str(vendedor.id)
        return dados