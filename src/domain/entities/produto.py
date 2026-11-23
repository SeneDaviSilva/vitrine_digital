from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from src.domain.enums.status_produto import StatusProduto
from src.domain.exceptions import DadosInvalidosError


@dataclass
class Produto:
    loja_id: UUID
    nome: str
    preco: float
    categoria: str
    descricao: Optional[str] = None
    imagens_url: List[str] = field(default_factory=list)
    status: StatusProduto = StatusProduto.DISPONIVEL
    id: Optional[UUID] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        self.nome = self.nome.strip()
        self.categoria = self.categoria.strip()
        self.preco = float(self.preco)
        self.imagens_url = [url for url in self.imagens_url if url]

        if not self.nome:
            raise DadosInvalidosError("O nome do produto é obrigatório.")
        if not self.categoria:
            raise DadosInvalidosError("A categoria do produto é obrigatória.")
        if not self.validar_preco():
            raise DadosInvalidosError("O preço do produto deve ser maior que zero.")
        if len(self.imagens_url) > 3:
            raise DadosInvalidosError("Um produto pode ter no máximo 3 imagens.")

    def validar_preco(self) -> bool:
        return self.preco > 0

    def alternar_status(self, novo_status: StatusProduto) -> None:
        self.status = novo_status

    def esta_visivel(self) -> bool:
        return self.status == StatusProduto.DISPONIVEL