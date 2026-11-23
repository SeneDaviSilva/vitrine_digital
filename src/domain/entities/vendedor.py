import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

from src.domain.enums.tipo_usuario import TipoUsuario
from src.domain.exceptions import DadosInvalidosError


@dataclass
class Vendedor:
    nome: str
    email: str
    senha_hash: str
    tipo_usuario: TipoUsuario = TipoUsuario.LOJISTA
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        self.email = self.email.strip().lower()

        if not self.nome:
            raise DadosInvalidosError("O nome do vendedor é obrigatório.")
        if not self.validar_email():
            raise DadosInvalidosError("Formato de e-mail inválido.")
        if not self.senha_hash:
            raise DadosInvalidosError("A senha criptografada é obrigatória.")

    def validar_email(self) -> bool:
        padrao = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return bool(re.match(padrao, self.email))

    def alterar_senha(self, nova_senha_hash: str) -> None:
        if not nova_senha_hash:
            raise DadosInvalidosError("A nova senha não pode ser vazia.")
        self.senha_hash = nova_senha_hash