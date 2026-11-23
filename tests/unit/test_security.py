from uuid import uuid4

import pytest

from src.domain.exceptions import DadosInvalidosError
from src.infra.security.auth.autenticacao import TokenVitrineEncoder
from src.infra.security.password_hasher import Sha256PasswordHasher


def test_hasher_gera_e_valida_senha() -> None:
    hasher = Sha256PasswordHasher()
    senha_hash = hasher.hash("minhasenha123")

    assert senha_hash != "minhasenha123"
    assert hasher.verificar("minhasenha123", senha_hash) is True
    assert hasher.verificar("senhaerrada", senha_hash) is False


def test_token_vitrine_codifica_e_decodifica_uuid() -> None:
    loja_id = uuid4()
    token = TokenVitrineEncoder.codificar_loja_id(loja_id)
    decodificado = TokenVitrineEncoder.decodificar_loja_id(token)

    assert decodificado == loja_id


def test_token_vitrine_rejeita_token_adulterado() -> None:
    with pytest.raises(DadosInvalidosError):
        TokenVitrineEncoder.decodificar_loja_id("token_invalido_123")