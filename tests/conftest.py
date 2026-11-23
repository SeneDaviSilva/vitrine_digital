from copy import deepcopy
from datetime import datetime, timezone
from typing import Dict, List, Optional
from uuid import UUID, uuid4

import pytest

from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.entities.vendedor import Vendedor
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.repositories.vendedor_repository import VendedorRepository
from src.infra.security.password_hasher import Sha256PasswordHasher


class InMemoryVendedorRepository(VendedorRepository):
    def __init__(self) -> None:
        self._dados: Dict[UUID, Vendedor] = {}

    def salvar(self, vendedor: Vendedor) -> Vendedor:
        registro = deepcopy(vendedor)
        registro.id = registro.id or uuid4()
        registro.created_at = registro.created_at or datetime.now(timezone.utc)
        self._dados[registro.id] = registro
        return deepcopy(registro)

    def buscar_por_id(self, vendedor_id: UUID) -> Optional[Vendedor]:
        item = self._dados.get(vendedor_id)
        return deepcopy(item) if item else None

    def buscar_por_email(self, email: str) -> Optional[Vendedor]:
        email_norm = email.strip().lower()
        for item in self._dados.values():
            if item.email == email_norm:
                return deepcopy(item)
        return None

    def atualizar(self, vendedor: Vendedor) -> Vendedor:
        if not vendedor.id or vendedor.id not in self._dados:
            raise KeyError("Vendedor não encontrado na memória.")
        registro = deepcopy(vendedor)
        self._dados[registro.id] = registro
        return deepcopy(registro)


class InMemoryLojaRepository(LojaRepository):
    def __init__(self) -> None:
        self._dados: Dict[UUID, Loja] = {}

    def salvar(self, loja: Loja) -> Loja:
        registro = deepcopy(loja)
        registro.id = registro.id or uuid4()
        registro.created_at = registro.created_at or datetime.now(timezone.utc)
        self._dados[registro.id] = registro
        return deepcopy(registro)

    def buscar_por_id(self, loja_id: UUID) -> Optional[Loja]:
        item = self._dados.get(loja_id)
        return deepcopy(item) if item else None

    def buscar_por_vendedor_id(self, vendedor_id: UUID) -> Optional[Loja]:
        for item in self._dados.values():
            if item.vendedor_id == vendedor_id:
                return deepcopy(item)
        return None

    def buscar_por_nome(self, nome_loja: str) -> Optional[Loja]:
        alvo = nome_loja.strip().lower()
        for item in self._dados.values():
            if item.nome_loja.lower() == alvo:
                return deepcopy(item)
        return None

    def buscar_por_whatsapp(self, whatsapp: str) -> Optional[Loja]:
        for item in self._dados.values():
            if item.whatsapp == whatsapp:
                return deepcopy(item)
        return None

    def listar_todas(self) -> List[Loja]:
        return sorted(
            [deepcopy(item) for item in self._dados.values()],
            key=lambda x: x.nome_loja.lower(),
        )

    def atualizar(self, loja: Loja) -> Loja:
        if not loja.id or loja.id not in self._dados:
            raise KeyError("Loja não encontrada na memória.")
        registro = deepcopy(loja)
        self._dados[registro.id] = registro
        return deepcopy(registro)


class InMemoryProdutoRepository(ProdutoRepository):
    def __init__(self) -> None:
        self._dados: Dict[UUID, Produto] = {}

    def salvar(self, produto: Produto) -> Produto:
        registro = deepcopy(produto)
        registro.id = registro.id or uuid4()
        registro.created_at = registro.created_at or datetime.now(timezone.utc)
        self._dados[registro.id] = registro
        return deepcopy(registro)

    def salvar_em_lote(self, produtos: List[Produto]) -> List[Produto]:
        return [self.salvar(p) for p in produtos]

    def buscar_por_id(self, produto_id: UUID) -> Optional[Produto]:
        item = self._dados.get(produto_id)
        return deepcopy(item) if item else None

    def listar_por_loja(self, loja_id: UUID, apenas_visiveis: bool = False) -> List[Produto]:
        resultado = []
        for item in self._dados.values():
            if item.loja_id != loja_id:
                continue
            if apenas_visiveis and not item.esta_visivel():
                continue
            resultado.append(deepcopy(item))
        return resultado

    def atualizar(self, produto: Produto) -> Produto:
        if not produto.id or produto.id not in self._dados:
            raise KeyError("Produto não encontrado na memória.")
        registro = deepcopy(produto)
        self._dados[registro.id] = registro
        return deepcopy(registro)

    def excluir(self, produto_id: UUID) -> None:
        self._dados.pop(produto_id, None)


class FakeStorageRepository:
    def __init__(self) -> None:
        self.arquivos_salvos: Dict[str, bytes] = {}

    def upload(self, caminho: str, conteudo: bytes, content_type: str) -> str:
        self.arquivos_salvos[caminho] = conteudo
        return f"https://storage.fake.local/produtos/{caminho}"


@pytest.fixture
def vendedor_repo() -> InMemoryVendedorRepository:
    return InMemoryVendedorRepository()


@pytest.fixture
def loja_repo() -> InMemoryLojaRepository:
    return InMemoryLojaRepository()


@pytest.fixture
def produto_repo() -> InMemoryProdutoRepository:
    return InMemoryProdutoRepository()


@pytest.fixture
def storage_repo() -> FakeStorageRepository:
    return FakeStorageRepository()


@pytest.fixture
def hasher() -> Sha256PasswordHasher:
    return Sha256PasswordHasher()