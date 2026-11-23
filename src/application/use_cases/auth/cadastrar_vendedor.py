from typing import Protocol

from src.domain.entities.vendedor import Vendedor
from src.domain.enums.tipo_usuario import TipoUsuario
from src.domain.exceptions import DadosInvalidosError, DuplicidadeError
from src.domain.repositories.vendedor_repository import VendedorRepository


class PasswordHasherProtocol(Protocol):
    def hash(self, senha: str) -> str: ...
    def verificar(self, senha: str, senha_hash: str) -> bool: ...


class CadastrarVendedorUseCase:
    def __init__(
        self,
        vendedor_repo: VendedorRepository,
        password_hasher: PasswordHasherProtocol,
    ) -> None:
        self._vendedor_repo = vendedor_repo
        self._password_hasher = password_hasher

    def executar(self, nome: str, email: str, senha: str) -> Vendedor:
        if not senha or len(senha) < 4:
            raise DadosInvalidosError("A senha deve ter pelo menos 4 caracteres.")

        email_normalizado = email.strip().lower()
        if self._vendedor_repo.buscar_por_email(email_normalizado):
            raise DuplicidadeError("Este e-mail já está cadastrado.")

        senha_hash = self._password_hasher.hash(senha)
        novo_vendedor = Vendedor(
            nome=nome,
            email=email_normalizado,
            senha_hash=senha_hash,
            tipo_usuario=TipoUsuario.LOJISTA,
        )

        return self._vendedor_repo.salvar(novo_vendedor)