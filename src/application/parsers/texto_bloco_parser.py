import re
from typing import List
from uuid import UUID

from src.domain.entities.produto import Produto
from src.domain.exceptions import DadosInvalidosError


class TextoBlocoParser:
    """Converte um bloco de texto estruturado em uma lista de entidades Produto."""

    @staticmethod
    def parse(texto_bruto: str, loja_id: UUID) -> List[Produto]:
        if not texto_bruto or not texto_bruto.strip():
            raise DadosInvalidosError("O campo de importação está vazio.")

        produtos_validos: List[Produto] = []
        blocos = re.split(r"\n\s*\n", texto_bruto.strip())

        for bloco in blocos:
            linhas = [linha.strip() for linha in bloco.strip().split("\n") if linha.strip()]
            if not linhas:
                continue

            nome = linhas[0][:255]
            preco = 0.0
            categoria = "Geral"
            descricao = ""

            for linha in linhas[1:]:
                linha_lower = linha.lower()
                if linha_lower.startswith("preço:") or linha_lower.startswith("preco:"):
                    valor_str = linha.split(":", 1)[1].strip().replace("R$", "").replace(",", ".")
                    try:
                        preco = float(valor_str)
                    except ValueError:
                        preco = 0.0
                elif linha_lower.startswith("categoria:"):
                    categoria = linha.split(":", 1)[1].strip() or "Geral"
                elif linha_lower.startswith("descrição:") or linha_lower.startswith("descricao:"):
                    descricao = linha.split(":", 1)[1].strip()

            try:
                produto = Produto(
                    loja_id=loja_id,
                    nome=nome,
                    preco=preco,
                    categoria=categoria,
                    descricao=descricao,
                )
                produtos_validos.append(produto)
            except DadosInvalidosError:
                continue

        if not produtos_validos:
            raise DadosInvalidosError("Nenhum produto válido foi encontrado no texto informado.")

        return produtos_validos