from uuid import UUID

import streamlit as st

from src.application.use_cases.loja.atualizar_loja import ArquivoUpload, AtualizarLojaUseCase
from src.application.use_cases.produto.alternar_disponibilidade import AlternarDisponibilidadeUseCase
from src.application.use_cases.produto.cadastrar_produto import CadastrarProdutoUseCase
from src.application.use_cases.produto.editar_produto import EditarProdutoUseCase
from src.application.use_cases.produto.excluir_produto import ExcluirProdutoUseCase
from src.application.use_cases.produto.importar_produtos import ImportarProdutosUseCase
from src.domain.exceptions import DomainError
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.domain.repositories.vendedor_repository import VendedorRepository
from src.frontend.components.card_loja import render_banner_link_vitrine
from src.frontend.components.header import render_header_lojista
from src.frontend.pages.gerenciamento_produtos import render_gerenciamento_produtos
from src.infra.security.auth.autenticacao import TokenVitrineEncoder

URL_BASE_VITRINE = "https://vitrine-digital.streamlit.app"


def render_painel_lojista(
    loja_id: UUID,
    vendedor_id: UUID,
    loja_repo: LojaRepository,
    vendedor_repo: VendedorRepository,
    produto_repo: ProdutoRepository,
    atualizar_loja_uc: AtualizarLojaUseCase,
    cadastrar_produto_uc: CadastrarProdutoUseCase,
    editar_produto_uc: EditarProdutoUseCase,
    excluir_produto_uc: ExcluirProdutoUseCase,
    importar_produtos_uc: ImportarProdutosUseCase,
    alternar_disp_uc: AlternarDisponibilidadeUseCase,
) -> None:
    loja = loja_repo.buscar_por_id(loja_id)
    vendedor = vendedor_repo.buscar_por_id(vendedor_id)

    if not loja or not vendedor:
        st.error("Erro ao carregar dados da loja.")
        return

    def _sair() -> None:
        st.session_state.pop("vendedor_id", None)
        st.session_state.pop("loja_id", None)
        st.rerun()

    render_header_lojista(
        loja=loja,
        is_admin_master=bool(st.session_state.get("is_admin_master")),
        on_sair=_sair,
    )

    token_publico = TokenVitrineEncoder.codificar_loja_id(loja_id)
    link_vitrine = f"{URL_BASE_VITRINE}/?loja={token_publico}"
    render_banner_link_vitrine(link_vitrine)

    tab_gerenciamento, tab_config = st.tabs(["Produtos", "Configurações"])

    with tab_gerenciamento:
        render_gerenciamento_produtos(
            loja_id=loja_id,
            produto_repo=produto_repo,
            cadastrar_uc=cadastrar_produto_uc,
            editar_uc=editar_produto_uc,
            excluir_uc=excluir_produto_uc,
            importar_uc=importar_produtos_uc,
            alternar_disp_uc=alternar_disp_uc,
        )

    with tab_config:
        produtos_loja = produto_repo.listar_por_loja(loja_id=loja_id, apenas_visiveis=False)
        cats_unicas = sorted(list({p.categoria for p in produtos_loja}))

        ordem_default = [c for c in loja.categorias_ordem if c in cats_unicas]
        for c in cats_unicas:
            if c not in ordem_default:
                ordem_default.append(c)

        with st.form("form_config_loja"):
            st.subheader("Perfil e Ajustes")
            edit_nome_loja = st.text_input("Nome da Loja", value=loja.nome_loja)
            edit_email = st.text_input("E-mail", value=vendedor.email)
            edit_whats = st.text_input("WhatsApp", value=loja.whatsapp, max_chars=13)
            edit_desc_loja = st.text_area("Apresentação", value=loja.descricao or "")

            st.divider()
            st.subheader("Ordem das Categorias")
            nova_ordem_cats = st.multiselect(
                "Arraste ou selecione a prioridade",
                options=cats_unicas,
                default=ordem_default,
            )

            st.divider()
            edit_logo = st.file_uploader("Logo da Loja", type=["png", "jpg", "jpeg", "webp"])

            if st.form_submit_button("Salvar Alterações", type="primary"):
                logo_upload = (
                    ArquivoUpload(
                        nome=edit_logo.name,
                        conteudo=edit_logo.getvalue(),
                        content_type=edit_logo.type,
                    )
                    if edit_logo
                    else None
                )
                try:
                    atualizar_loja_uc.executar(
                        loja_id=loja_id,
                        nome_loja=edit_nome_loja,
                        email=edit_email,
                        whatsapp=edit_whats,
                        descricao=edit_desc_loja,
                        categorias_ordem=nova_ordem_cats,
                        nova_logo=logo_upload,
                    )
                    st.session_state["msg_sucesso"] = "Configurações salvas."
                    st.rerun()
                except DomainError as err:
                    st.error(str(err))