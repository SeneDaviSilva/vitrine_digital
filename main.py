from dataclasses import dataclass
from uuid import UUID

import streamlit as st

from src.application.use_cases.auth.autenticar_vendedor import AutenticarVendedorUseCase
from src.application.use_cases.auth.cadastrar_vendedor import CadastrarVendedorUseCase
from src.application.use_cases.auth.redefinir_senha import RedefinirSenhaUseCase
from src.application.use_cases.loja.atualizar_loja import AtualizarLojaUseCase
from src.application.use_cases.loja.cadastrar_loja import CadastrarLojaUseCase
from src.application.use_cases.produto.alternar_disponibilidade import AlternarDisponibilidadeUseCase
from src.application.use_cases.produto.cadastrar_produto import CadastrarProdutoUseCase
from src.application.use_cases.produto.editar_produto import EditarProdutoUseCase
from src.application.use_cases.produto.excluir_produto import ExcluirProdutoUseCase
from src.application.use_cases.produto.importar_produtos import ImportarProdutosUseCase
from src.frontend.components.header import render_header_auth
from src.frontend.components.sidebar import carregar_estilos
from src.frontend.pages.cadastro import render_aba_cadastro
from src.frontend.pages.login import render_aba_login
from src.frontend.pages.painel_admin import render_painel_admin
from src.frontend.pages.painel_lojista import render_painel_lojista
from src.frontend.pages.vitrine_publica import render_vitrine_publica
from src.infra.database.supabase_client import SupabaseClientFactory
from src.infra.repositories.loja_repository import SupabaseLojaRepository
from src.infra.repositories.produto_repository import SupabaseProdutoRepository
from src.infra.repositories.vendedor_repository import SupabaseVendedorRepository
from src.infra.security.password_hasher import Sha256PasswordHasher
from src.infra.storage.supabase_storage import SupabaseStorageRepository

st.set_page_config(page_title="Vitrine Digital", layout="centered")


@dataclass
class AppContainer:
    vendedor_repo: SupabaseVendedorRepository
    loja_repo: SupabaseLojaRepository
    produto_repo: SupabaseProdutoRepository
    cadastrar_vendedor_uc: CadastrarVendedorUseCase
    autenticar_vendedor_uc: AutenticarVendedorUseCase
    redefinir_senha_uc: RedefinirSenhaUseCase
    cadastrar_loja_uc: CadastrarLojaUseCase
    atualizar_loja_uc: AtualizarLojaUseCase
    cadastrar_produto_uc: CadastrarProdutoUseCase
    editar_produto_uc: EditarProdutoUseCase
    excluir_produto_uc: ExcluirProdutoUseCase
    importar_produtos_uc: ImportarProdutosUseCase
    alternar_disp_uc: AlternarDisponibilidadeUseCase


def montar_dependencias() -> AppContainer:
    client = SupabaseClientFactory.obter_cliente()
    vendedor_repo = SupabaseVendedorRepository(client)
    loja_repo = SupabaseLojaRepository(client)
    produto_repo = SupabaseProdutoRepository(client)
    storage_repo = SupabaseStorageRepository(client, bucket="produtos")
    hasher = Sha256PasswordHasher()

    return AppContainer(
        vendedor_repo=vendedor_repo,
        loja_repo=loja_repo,
        produto_repo=produto_repo,
        cadastrar_vendedor_uc=CadastrarVendedorUseCase(vendedor_repo, hasher),
        autenticar_vendedor_uc=AutenticarVendedorUseCase(vendedor_repo, hasher),
        redefinir_senha_uc=RedefinirSenhaUseCase(vendedor_repo, loja_repo, hasher),
        cadastrar_loja_uc=CadastrarLojaUseCase(loja_repo),
        atualizar_loja_uc=AtualizarLojaUseCase(loja_repo, vendedor_repo, storage_repo),
        cadastrar_produto_uc=CadastrarProdutoUseCase(produto_repo, storage_repo),
        editar_produto_uc=EditarProdutoUseCase(produto_repo, storage_repo),
        excluir_produto_uc=ExcluirProdutoUseCase(produto_repo),
        importar_produtos_uc=ImportarProdutosUseCase(produto_repo),
        alternar_disp_uc=AlternarDisponibilidadeUseCase(produto_repo),
    )


def main() -> None:
    carregar_estilos()
    app = montar_dependencias()

    if "msg_sucesso" in st.session_state:
        st.toast(st.session_state.pop("msg_sucesso"))

    # Rota 1: Vitrine Pública do Cliente
    if "loja" in st.query_params:
        render_vitrine_publica(
            token_loja=st.query_params["loja"],
            loja_repo=app.loja_repo,
            produto_repo=app.produto_repo,
        )
        return

    # Rota 2: Painel do Lojista Autenticado
    if "loja_id" in st.session_state and "vendedor_id" in st.session_state:
        render_painel_lojista(
            loja_id=UUID(st.session_state["loja_id"]),
            vendedor_id=UUID(st.session_state["vendedor_id"]),
            loja_repo=app.loja_repo,
            vendedor_repo=app.vendedor_repo,
            produto_repo=app.produto_repo,
            atualizar_loja_uc=app.atualizar_loja_uc,
            cadastrar_produto_uc=app.cadastrar_produto_uc,
            editar_produto_uc=app.editar_produto_uc,
            excluir_produto_uc=app.excluir_produto_uc,
            importar_produtos_uc=app.importar_produtos_uc,
            alternar_disp_uc=app.alternar_disp_uc,
        )
        return

    # Rota 3: Painel Administrativo Global
    if st.session_state.get("is_admin_master"):
        render_painel_admin(loja_repo=app.loja_repo)
        return

    # Rota 4: Autenticação e Cadastro
    render_header_auth()
    aba_login, aba_cadastro = st.tabs(["Entrar", "Criar Conta"])

    with aba_login:
        render_aba_login(
            autenticar_uc=app.autenticar_vendedor_uc,
            redefinir_senha_uc=app.redefinir_senha_uc,
            loja_repo=app.loja_repo,
            admin_email=st.secrets.get("ADMIN_EMAIL", "admin@vitrinedigital.com"),
            admin_senha=st.secrets.get("ADMIN_PASSWORD", "admin123"),
        )

    with aba_cadastro:
        render_aba_cadastro(
            cadastrar_vendedor_uc=app.cadastrar_vendedor_uc,
            cadastrar_loja_uc=app.cadastrar_loja_uc,
            loja_repo=app.loja_repo,
        )


if __name__ == "__main__":
    main()