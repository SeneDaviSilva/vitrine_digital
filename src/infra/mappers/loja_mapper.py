from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from src.domain.entities.loja import Loja


class LojaMapper:
    @staticmethod
    def to_entity(row: Dict[str, Any]) -> Loja:
        ordem_raw = row.get("categorias_ordem") or ""
        categorias_ordem = [c.strip() for c in ordem_raw.split(",") if c.strip()]

        created_at = (
            datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else None
        )

        return Loja(
            id=UUID(str(row["id"])),
            vendedor_id=UUID(str(row["vendedor_id"])),
            nome_loja=row["nome_loja"],
            whatsapp=row["whatsapp"],
            descricao=row.get("descricao"),
            logo_url=row.get("logo_url"),
            categorias_ordem=categorias_ordem,
            created_at=created_at,
        )

    @staticmethod
    def to_persistence(loja: Loja) -> Dict[str, Any]:
        dados: Dict[str, Any] = {
            "vendedor_id": str(loja.vendedor_id),
            "nome_loja": loja.nome_loja,
            "whatsapp": loja.whatsapp,
            "descricao": loja.descricao,
            "logo_url": loja.logo_url,
            "categorias_ordem": ",".join(loja.categorias_ordem),
        }
        if loja.id:
            dados["id"] = str(loja.id)
        return dados