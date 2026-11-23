from datetime import datetime
from typing import Any, Dict
from uuid import UUID

from src.domain.entities.produto import Produto
from src.domain.enums.status_produto import StatusProduto


class ProdutoMapper:
    @staticmethod
    def to_entity(row: Dict[str, Any]) -> Produto:
        imagens = [
            row.get("imagem_url"),
            row.get("imagem_url_2"),
            row.get("imagem_url_3"),
        ]
        imagens_validas = [img for img in imagens if img]

        created_at = (
            datetime.fromisoformat(row["created_at"])
            if row.get("created_at")
            else None
        )

        return Produto(
            id=UUID(str(row["id"])),
            loja_id=UUID(str(row["loja_id"])),
            nome=row["nome"],
            preco=float(row["preco"]),
            categoria=row["categoria"],
            descricao=row.get("descricao"),
            imagens_url=imagens_validas,
            status=StatusProduto(row.get("status", StatusProduto.DISPONIVEL.value)),
            created_at=created_at,
        )

    @staticmethod
    def to_persistence(produto: Produto) -> Dict[str, Any]:
        imgs = produto.imagens_url
        dados: Dict[str, Any] = {
            "loja_id": str(produto.loja_id),
            "nome": produto.nome,
            "preco": produto.preco,
            "categoria": produto.categoria,
            "descricao": produto.descricao,
            "imagem_url": imgs[0] if len(imgs) > 0 else None,
            "imagem_url_2": imgs[1] if len(imgs) > 1 else None,
            "imagem_url_3": imgs[2] if len(imgs) > 2 else None,
            "status": produto.status.value,
        }
        if produto.id:
            dados["id"] = str(produto.id)
        return dados