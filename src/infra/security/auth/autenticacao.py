import base64
from typing import Optional
from uuid import UUID

from src.domain.exceptions import DadosInvalidosError


class TokenVitrineEncoder:
    """Codifica e decodifica o identificador público da loja na URL (?loja=...)."""

    _PREFIXO = "vitrine_"

    @classmethod
    def codificar_loja_id(cls, loja_id: UUID) -> str:
        raw = f"{cls._PREFIXO}{loja_id}"
        return base64.urlsafe_b64encode(raw.encode("utf-8")).decode("utf-8")

    @classmethod
    def decodificar_loja_id(cls, token: str) -> UUID:
        try:
            decodificado = base64.urlsafe_b64decode(token.encode("utf-8")).decode("utf-8")
            if not decodificado.startswith(cls._PREFIXO):
                raise DadosInvalidosError("Link da loja inválido.")
            id_str = decodificado.replace(cls._PREFIXO, "", 1)
            return UUID(id_str)
        except Exception as exc:
            raise DadosInvalidosError("Link da loja inválido ou corrompido.") from exc

    @staticmethod
    def validar_admin_master(email: str, senha: str, admin_email: Optional[str], admin_senha: Optional[str]) -> bool:
        if not admin_email or not admin_senha:
            return False
        return email.strip().lower() == admin_email.strip().lower() and senha == admin_senha