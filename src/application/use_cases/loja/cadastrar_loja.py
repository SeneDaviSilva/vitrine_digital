from typing import Optional
from uuid import UUID

from src.domain.entities.loja import Loja
from src.domain.exceptions import DuplicidadeError
from src.domain.repositories.loja_repository import LojaRepository


class CadastrarLojaUseCase:
    def __init__(self, loja_repo: LojaRepository) -> None:
        self._loja_repo = loja_repo

    def executar(
        self,
        vendedor_id: UUID,
        nome_loja: str,
        whatsapp: str,
        descricao: Optional[str] = None,
    ) -> Loja:
        nova_loja = Loja(
            vendedor_id=vendedor_id,
            nome_loja=nome_loja,
            whatsapp=whatsapp,
            descricao=descricao,
        )

        if self._loja_repo.buscar_por_nome(nova_loja.nome_loja):
            raise DuplicidadeError("Já existe uma loja cadastrada com este nome.")

        if self._loja_repo.buscar_por_whatsapp(nova_loja.whatsapp):
            raise DuplicidadeError("Este número de WhatsApp já está vinculado a outra loja.")

        return self._loja_repo.salvar(nova_loja)