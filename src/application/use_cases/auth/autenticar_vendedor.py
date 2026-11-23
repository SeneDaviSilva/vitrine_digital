from typing import Protocol

from src.domain.entities.vendedor import Vendedor
from src.domain.exceptions import CredenciaisInvalidasError, DadosInvalidosError
from src.domain.repositories.vendedor_repository import VendedorRepository


class PasswordHasherProtocol(Protocol):
    def hash(self, senha: str) -> str: ...
    def verificar(self, senha: str, senha_hash: str) -> bool: ...


class AutenticarVendedorUseCase:
    def __init__(
        self,
        vendedor_repo: VendedorRepository,
        password_hasher: PasswordHasherProtocol,
    ) -> None:
        self._vendedor_repo = vendedor_repo
        self._password_hasher = password_hasher

    def executar(self, email: str, senha: str) -> Vendedor:
        if not email or not senha:
            raise DadosInvalidosError("Informe e-mail e senha para entrar.")

        vendedor = self._vendedor_repo.buscar_por_email(email.strip().lower())
        if not vendedor:
            raise CredenciaisInvalidasError("E-mail ou senha incorretos.")

        if not self._password_hasher.verificar(senha, vendedor.senha_hash):
            raise CredenciaisInvalidasError("E-mail ou senha incorretos.")

        return vendedor