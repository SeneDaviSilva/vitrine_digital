from typing import List
from uuid import UUID

import streamlit as st

from src.application.use_cases.loja.atualizar_loja import ArquivoUpload
from src.application.use_cases.produto.alternar_disponibilidade import AlternarDisponibilidadeUseCase
from src.application.use_cases.produto.cadastrar_produto import CadastrarProdutoUseCase
from src.application.use_cases.produto.editar_produto import EditarProdutoUseCase
from src.application.use_cases.produto.excluir_produto import ExcluirProdutoUseCase
from src.application.use_cases.produto.importar_produtos import ImportarProdutosUseCase
from src.domain.entities.produto import Produto
from src.domain.exceptions import DomainError
from src.domain.repositories.produto_repository import ProdutoRepository
from src.frontend.components.card_produto import render_card_produto_admin


def _converter_uploads(arquivos_st) -> List[ArquivoUpload]:
    if not arquivos_st:
        return []
    return [
        ArquivoUpload(nome=arq.name, conteudo=arq.getvalue(), content_type=arq.type)
        for arq in arquivos_st
    ]


@st.dialog("Novo Produto")
def _modal_novo_produto(
    loja_id: UUID,
    categorias_existentes: List[str],
    cadastrar_uc: CadastrarProdutoUseCase,
    seq: int,
) -> None:
    opcoes_categoria = [*categorias_existentes, "+ Criar nova categoria"]

    nome = st.text_input("Nome *", key=f"novo_nome_{seq}")
    descricao = st.text_area("Descrição", key=f"novo_desc_{seq}")
    preco = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        step=0.50,
        format="%.2f",
        value=None,
        key=f"novo_preco_{seq}",
    )

    cat_selecionada = st.selectbox(
        "Categoria *",
        options=opcoes_categoria,
        index=0,
        key=f"novo_cat_sel_{seq}",
    )
    if cat_selecionada == "+ Criar nova categoria":
        categoria = st.text_input("Nova Categoria *", key=f"novo_cat_txt_{seq}")
    else:
        categoria = cat_selecionada

    imagens_arquivo = st.file_uploader(
        "Fotos (Máximo 3)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"novo_imgs_{seq}",
    )

    if st.button("Adicionar", type="primary", use_container_width=True, key=f"novo_btn_{seq}"):
        try:
            cadastrar_uc.executar(
                loja_id=loja_id,
                nome=nome,
                preco=preco or 0.0,
                categoria=categoria,
                descricao=descricao,
                imagens=_converter_uploads(imagens_arquivo),
            )
            st.session_state["msg_sucesso"] = "Produto cadastrado."
            st.rerun()
        except DomainError as err:
            st.error(str(err))


@st.dialog("Editar Produto")
def _modal_editar_produto(
    produto: Produto,
    categorias_existentes: List[str],
    editar_uc: EditarProdutoUseCase,
    seq: int,
) -> None:
    opcoes_categoria = [*categorias_existentes, "+ Criar nova categoria"]
    idx_padrao = opcoes_categoria.index(produto.categoria) if produto.categoria in opcoes_categoria else 0

    edit_nome = st.text_input("Nome", value=produto.nome, key=f"edit_nome_{produto.id}_{seq}")
    edit_desc = st.text_area("Descrição", value=produto.descricao or "", key=f"edit_desc_{produto.id}_{seq}")
    edit_preco = st.number_input(
        "Preço (R$)",
        min_value=0.0,
        step=0.50,
        format="%.2f",
        value=float(produto.preco),
        key=f"edit_preco_{produto.id}_{seq}",
    )

    cat_selecionada = st.selectbox(
        "Categoria",
        options=opcoes_categoria,
        index=idx_padrao,
        key=f"edit_cat_sel_{produto.id}_{seq}",
    )
    if cat_selecionada == "+ Criar nova categoria":
        edit_cat = st.text_input("Nova Categoria", key=f"edit_cat_txt_{produto.id}_{seq}")
    else:
        edit_cat = cat_selecionada

    edit_imagens = st.file_uploader(
        "Substituir Fotos (Máximo 3)",
        type=["png", "jpg", "jpeg", "webp"],
        accept_multiple_files=True,
        key=f"edit_up_{produto.id}_{seq}",
    )

    if st.button("Salvar", type="primary", use_container_width=True, key=f"edit_btn_{produto.id}_{seq}"):
        if not produto.id:
            st.error("Produto inválido.")
            return
        try:
            editar_uc.executar(
                produto_id=produto.id,
                nome=edit_nome,
                preco=edit_preco,
                categoria=edit_cat,
                descricao=edit_desc,
                novas_imagens=_converter_uploads(edit_imagens),
            )
            st.session_state["msg_sucesso"] = "Produto atualizado."
            st.rerun()
        except DomainError as err:
            st.error(str(err))


@st.dialog("Cadastro em Massa")
def _modal_cadastro_massa(loja_id: UUID, importar_uc: ImportarProdutosUseCase, seq: int) -> None:
    st.markdown("Cole seus produtos separando-os por uma linha em branco.")
    st.code("Café Especial\nPreço: 24.90\nCategoria: Bebidas\nDescrição: 250g torra média", language="text")

    texto_importacao = st.text_area("Bloco de texto:", height=250, key=f"massa_txt_{seq}")

    if st.button("Importar", type="primary", use_container_width=True, key=f"massa_btn_{seq}"):
        try:
            inseridos = importar_uc.executar(loja_id=loja_id, texto_bruto=texto_importacao)
            st.session_state["msg_sucesso"] = f"{len(inseridos)} produtos importados."
            st.rerun()
        except DomainError as err:
            st.error(str(err))


def render_gerenciamento_produtos(
    loja_id: UUID,
    produto_repo: ProdutoRepository,
    cadastrar_uc: CadastrarProdutoUseCase,
    editar_uc: EditarProdutoUseCase,
    excluir_uc: ExcluirProdutoUseCase,
    importar_uc: ImportarProdutosUseCase,
    alternar_disp_uc: AlternarDisponibilidadeUseCase,
) -> None:
    meus_produtos = produto_repo.listar_por_loja(loja_id=loja_id, apenas_visiveis=False)
    categorias_existentes = sorted({p.categoria for p in meus_produtos if p.categoria})

    c_add1, c_add2 = st.columns(2)
    with c_add1:
        if st.button("Novo Produto", type="primary", use_container_width=True):
            seq = st.session_state.get("modal_prod_seq", 0) + 1
            st.session_state["modal_prod_seq"] = seq
            _modal_novo_produto(loja_id, categorias_existentes, cadastrar_uc, seq)
    with c_add2:
        if st.button("Importar em Massa", use_container_width=True):
            seq = st.session_state.get("modal_prod_seq", 0) + 1
            st.session_state["modal_prod_seq"] = seq
            _modal_cadastro_massa(loja_id, importar_uc, seq)

    st.divider()

    if not meus_produtos:
        st.info("Nenhum produto cadastrado.")
        return

    def _on_toggle(prod: Produto, ativo: bool) -> None:
        if prod.id:
            alternar_disp_uc.executar(produto_id=prod.id, disponivel=ativo)
            st.rerun()

    def _on_excluir(prod: Produto) -> None:
        if prod.id:
            excluir_uc.executar(produto_id=prod.id)
            st.rerun()

    def _on_editar(prod: Produto) -> None:
        seq = st.session_state.get("modal_prod_seq", 0) + 1
        st.session_state["modal_prod_seq"] = seq
        _modal_editar_produto(prod, categorias_existentes, editar_uc, seq)

    for cat in categorias_existentes:
        st.markdown(f"#### {cat}")
        produtos_cat = sorted(
            [p for p in meus_produtos if p.categoria == cat],
            key=lambda x: x.nome.lower(),
        )
        for item in produtos_cat:
            render_card_produto_admin(
                produto=item,
                on_toggle_status=_on_toggle,
                on_editar=_on_editar,
                on_excluir=_on_excluir,
            )