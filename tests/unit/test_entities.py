from uuid import uuid4

import pytest

from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.entities.vendedor import Vendedor
from src.domain.enums.status_produto import StatusProduto
from src.domain.exceptions import DadosInvalidosError


def test_vendedor_normaliza_email_e_valida_formato() -> None:
    vendedor = Vendedor(nome="  Davi Silva  ", email="  DAVI@Exemplo.COM ", senha_hash="hash123")
    assert vendedor.nome == "Davi Silva"
    assert vendedor.email == "davi@exemplo.com"


def test_vendedor_rejeita_email_invalido() -> None:
    with pytest.raises(DadosInvalidosError):
        Vendedor(nome="Davi", email="email_sem_arroba.com", senha_hash="hash123")


def test_loja_limpa_mascara_whatsapp_e_gera_link() -> None:
    loja = Loja(
        vendedor_id=uuid4(),
        nome_loja="Café da Esquina",
        whatsapp="(11) 98888-7777",
    )
    assert loja.whatsapp == "11988887777"

    link = loja.gerar_link_whatsapp("Olá, quero 1 café!")
    assert link.startswith("https://wa.me/11988887777?text=")
    assert "Ol%C3%A1" in link


def test_loja_rejeita_whatsapp_curto() -> None:
    with pytest.raises(DadosInvalidosError):
        Loja(vendedor_id=uuid4(), nome_loja="Loja Teste", whatsapp="11999")


def test_produto_rejeita_preco_zero_ou_negativo() -> None:
    with pytest.raises(DadosInvalidosError):
        Produto(loja_id=uuid4(), nome="Bolo", preco=0.0, categoria="Doces")

    with pytest.raises(DadosInvalidosError):
        Produto(loja_id=uuid4(), nome="Bolo", preco=-15.0, categoria="Doces")


def test_produto_rejeita_mais_de_tres_imagens() -> None:
    with pytest.raises(DadosInvalidosError):
        Produto(
            loja_id=uuid4(),
            nome="Tênis",
            preco=199.90,
            categoria="Calçados",
            imagens_url=["1.jpg", "2.jpg", "3.jpg", "4.jpg"],
        )


def test_produto_alterna_disponibilidade() -> None:
    produto = Produto(loja_id=uuid4(), nome="Suco Natural", preco=8.50, categoria="Bebidas")
    assert produto.esta_visivel() is True

    produto.alternar_status(StatusProduto.ESGOTADO)
    assert produto.esta_visivel() is False