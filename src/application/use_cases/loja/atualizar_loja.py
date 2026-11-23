import time
from dataclasses import dataclass
from typing import List, Optional, Protocol
from uuid import UUID

from src.domain.entities.loja import Loja
from src.domain.exceptions import DuplicidadeError, EntidadeNaoEncontradaError
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.vendedor_repository import VendedorRepository


@dataclass
class ArquivoUpload:
    nome: str
    conteudo: bytes
    content_type: str


class StorageGatewayProtocol(Protocol):
    def upload(self, caminho: str, conteudo: bytes, content_type: str) -> str: ...


class AtualizarLojaUseCase:
    def __init__(
        self,
        loja_repo: LojaRepository,
        vendedor_repo: VendedorRepository,
        storage: StorageGatewayProtocol,
    ) -> None:
        self._loja_repo = loja_repo
        self._vendedor_repo = vendedor_repo
        self._storage = storage

    def executar(
        self,
        loja_id: UUID,
        nome_loja: str,
        email: str,
        whatsapp: str,
        descricao: Optional[str],
        categorias_ordem: List[str],
        nova_logo: Optional[ArquivoUpload] = None,
    ) -> Loja:
        loja_atual = self._loja_repo.buscar_por_id(loja_id)
        if not loja_atual:
            raise EntidadeNaoEncontradaError("Loja não encontrada.")

        vendedor = self._vendedor_repo.buscar_por_id(loja_atual.vendedor_id)
        if not vendedor:
            raise EntidadeNaoEncontradaError("Vendedor proprietário não encontrado.")

        # Instancia entidade temporária para validar regras de formato (nome e whatsapp)
        loja_validada = Loja(
            id=loja_atual.id,
            vendedor_id=loja_atual.vendedor_id,
            nome_loja=nome_loja,
            whatsapp=whatsapp,
            descricao=descricao,
            logo_url=loja_atual.logo_url,
            categorias_ordem=categorias_ordem,
            created_at=loja_atual.created_at,
        )

        # Verifica duplicidade ignorando os próprios registros
        loja_mesmo_nome = self._loja_repo.buscar_por_nome(loja_validada.nome_loja)
        if loja_mesmo_nome and loja_mesmo_nome.id != loja_atual.id:
            raise DuplicidadeError("Este nome de loja já está em uso.")

        loja_mesmo_whats = self._loja_repo.buscar_por_whatsapp(loja_validada.whatsapp)
        if loja_mesmo_whats and loja_mesmo_whats.id != loja_atual.id:
            raise DuplicidadeError("Este WhatsApp já está vinculado a outra conta.")

        email_normalizado = email.strip().lower()
        vendedor_mesmo_email = self._vendedor_repo.buscar_por_email(email_normalizado)
        if vendedor_mesmo_email and vendedor_mesmo_email.id != vendedor.id:
            raise DuplicidadeError("Este e-mail já está em uso.")

        if nova_logo:
            extensao = nova_logo.nome.split(".")[-1]
            caminho = f"logo_{loja_atual.id}_{int(time.time())}.{extensao}"
            loja_validada.logo_url = self._storage.upload(
                caminho=caminho,
                conteudo=nova_logo.conteudo,
                content_type=nova_logo.content_type,
            )

        vendedor.email = email_normalizado
        if not vendedor.validar_email():
            raise DuplicidadeError("Formato de e-mail inválido.")

        self._vendedor_repo.atualizar(vendedor)
        return self._loja_repo.atualizar(loja_validada)