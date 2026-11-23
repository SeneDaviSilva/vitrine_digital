from typing import Protocol

from src.domain.exceptions import (
    CredenciaisInvalidasError,
    DadosInvalidosError,
    EntidadeNaoEncontradaError,
)
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.vendedor_repository import VendedorRepository


class PasswordHasherProtocol(Protocol):
    def hash(self, senha: str) -> str: ...
    def verificar(self, senha: str, senha_hash: str) -> bool: ...


class RedefinirSenhaUseCase:
    """Permite redefinir a senha validando a titularidade via e-mail + WhatsApp da loja."""

    def __init__(
        self,
        vendedor_repo: VendedorRepository,
        loja_repo: LojaRepository,
        password_hasher: PasswordHasherProtocol,
    ) -> None:
        self._vendedor_repo = vendedor_repo
        self._loja_repo = loja_repo
        self._password_hasher = password_hasher

    def executar(self, email: str, whatsapp: str, nova_senha: str) -> None:
        if not nova_senha or len(nova_senha) < 4:
            raise DadosInvalidosError("A nova senha deve ter pelo menos 4 caracteres.")

        vendedor = self._vendedor_repo.buscar_por_email(email.strip().lower())
        if not vendedor or not vendedor.id:
            raise EntidadeNaoEncontradaError("E-mail não encontrado.")

        loja = self._loja_repo.buscar_por_vendedor_id(vendedor.id)
        whatsapp_limpo = "".join(filter(str.isdigit, str(whatsapp)))

        if not loja or loja.whatsapp != whatsapp_limpo:
            raise CredenciaisInvalidasError("O WhatsApp informado não corresponde ao cadastro.")

        novo_hash = self._password_hasher.hash(nova_senha)
        vendedor.alterar_senha(novo_hash)
        self._vendedor_repo.atualizar(vendedor)