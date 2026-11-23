from uuid import uuid4

import pytest

from src.application.parsers.texto_bloco_parser import TextoBlocoParser
from src.domain.exceptions import DadosInvalidosError


def test_parser_converte_bloco_texto_valido() -> None:
    texto = """
    Café Especial
    Preço: R$ 24,90
    Categoria: Bebidas
    Descrição: 250g torra média

    Pão de Queijo
    Preco: 6.50
    """
    loja_id = uuid4()
    produtos = TextoBlocoParser.parse(texto_bruto=texto, loja_id=loja_id)

    assert len(produtos) == 2
    assert produtos[0].nome == "Café Especial"
    assert produtos[0].preco == 24.90
    assert produtos[0].categoria == "Bebidas"
    assert produtos[0].descricao == "250g torra média"

    assert produtos[1].nome == "Pão de Queijo"
    assert produtos[1].preco == 6.50
    assert produtos[1].categoria == "Geral"


def test_parser_ignora_blocos_sem_preco_valido() -> None:
    texto = """
    Item Inválido Sem Preço
    Categoria: Teste

    Item Válido
    Preço: 10,00
    """
    produtos = TextoBlocoParser.parse(texto_bruto=texto, loja_id=uuid4())
    assert len(produtos) == 1
    assert produtos[0].nome == "Item Válido"


def test_parser_lanca_erro_quando_texto_vazio_ou_totalmente_invalido() -> None:
    with pytest.raises(DadosInvalidosError):
        TextoBlocoParser.parse(texto_bruto="   ", loja_id=uuid4())

    with pytest.raises(DadosInvalidosError):
        TextoBlocoParser.parse(texto_bruto="Produto sem preço\nCategoria: Geral", loja_id=uuid4())