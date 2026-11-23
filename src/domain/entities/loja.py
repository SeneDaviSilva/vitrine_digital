import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.exceptions import DadosInvalidosError


@dataclass
class Loja:
    vendedor_id: UUID
    nome_loja: str
    whatsapp: str
    descricao: Optional[str] = None
    logo_url: Optional[str] = None
    categorias_ordem: List[str] = field(default_factory=list)
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        self.nome_loja = self.nome_loja.strip()
        self.whatsapp = "".join(filter(str.isdigit, str(self.whatsapp)))

        if not self.nome_loja:
            raise DadosInvalidosError("O nome da loja é obrigatório.")
        if not self.validar_whatsapp():
            raise DadosInvalidosError("O WhatsApp deve conter entre 10 e 13 dígitos numéricos.")

    def validar_whatsapp(self) -> bool:
        return self.whatsapp.isdigit() and 10 <= len(self.whatsapp) <= 13

    def gerar_link_whatsapp(self, mensagem: str) -> str:
        texto_codificado = urllib.parse.quote(mensagem)
        return f"https://wa.me/{self.whatsapp}?text={texto_codificado}"

    def reordenar_categorias(self, nova_ordem: List[str]) -> None:
        self.categorias_ordem = [cat.strip() for cat in nova_ordem if cat.strip()]