import streamlit as st

from src.domain.entities.loja import Loja
from src.domain.entities.produto import Produto
from src.domain.exceptions import DadosInvalidosError
from src.domain.repositories.loja_repository import LojaRepository
from src.domain.repositories.produto_repository import ProdutoRepository
from src.frontend.components.card_produto import render_card_produto_vitrine
from src.frontend.components.header import render_header_vitrine
from src.frontend.components.sidebar import render_rodape_vitrine
from src.infra.security.auth.autenticacao import TokenVitrineEncoder


def _alterar_qtd(pid: str, delta: int) -> None:
    st.session_state["carrinho"][pid]["qtd"] += delta
    if st.session_state["carrinho"][pid]["qtd"] <= 0:
        del st.session_state["carrinho"][pid]


def _esvaziar_carrinho() -> None:
    st.session_state["carrinho"] = {}


@st.dialog("Seu Pedido")
def _modal_carrinho(loja: Loja) -> None:
    carrinho = st.session_state.get("carrinho", {})
    if not carrinho:
        st.warning("Seu carrinho está vazio. Adicione produtos da vitrine.")
        return

    total = 0.0
    for pid, item in list(carrinho.items()):
        st.markdown(f"<div style='margin-bottom: 4px; font-weight: 600;'>{item['nome']}</div>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
        with c1:
            st.button("-", key=f"dec_{pid}", on_click=_alterar_qtd, args=(pid, -1), use_container_width=True)
        with c2:
            st.markdown(
                f"<div style='text-align:center; padding-top:6px; font-weight:600; font-size:1.1rem;'>{item['qtd']}</div>",
                unsafe_allow_html=True,
            )
        with c3:
            st.button("+", key=f"inc_{pid}", on_click=_alterar_qtd, args=(pid, 1), use_container_width=True)
        with c4:
            subtotal = item["preco"] * item["qtd"]
            st.markdown(
                f"<div style='text-align:right; padding-top:6px; font-weight:600;'>R$ {subtotal:.2f}</div>",
                unsafe_allow_html=True,
            )

        total += item["preco"] * item["qtd"]
        st.markdown(
            "<hr style='margin: 0.5em 0; border: none; border-top: 1px solid rgba(128,128,128,0.2);'/>",
            unsafe_allow_html=True,
        )

    st.markdown(f"<h3 style='margin-top: 0;'>Total: R$ {total:.2f}</h3>", unsafe_allow_html=True)

    linhas_pedido = [f"- {item['qtd']}x {item['nome']}" for item in carrinho.values()]
    mensagem = "Olá! Gostaria de fazer o seguinte pedido:\n\n" + "\n".join(linhas_pedido) + f"\n\n*Total: R$ {total:.2f}*"
    wa_url = loja.gerar_link_whatsapp(mensagem)

    st.link_button("Enviar Pedido por WhatsApp", wa_url, type="primary", use_container_width=True)
    st.button("Esvaziar Carrinho", on_click=_esvaziar_carrinho, use_container_width=True)


def render_vitrine_publica(
    token_loja: str,
    loja_repo: LojaRepository,
    produto_repo: ProdutoRepository,
) -> None:
    if "carrinho" not in st.session_state:
        st.session_state["carrinho"] = {}

    try:
        loja_id = TokenVitrineEncoder.decodificar_loja_id(token_loja)
    except DadosInvalidosError as err:
        st.error(str(err))
        return

    loja = loja_repo.buscar_por_id(loja_id)
    if not loja:
        st.error("Loja não encontrada.")
        return

    qtd_itens = sum(item["qtd"] for item in st.session_state["carrinho"].values())
    render_header_vitrine(
        loja=loja,
        qtd_itens=qtd_itens,
        on_abrir_carrinho=lambda: _modal_carrinho(loja),
    )

    st.divider()

    produtos = produto_repo.listar_por_loja(loja_id=loja_id, apenas_visiveis=True)
    if not produtos:
        st.info("Nenhum produto disponível no momento.")
        render_rodape_vitrine()
        return

    cat_counts = {}
    for p in produtos:
        cat_counts[p.categoria] = cat_counts.get(p.categoria, 0) + 1

    todas_cats = list(cat_counts.keys())
    if loja.categorias_ordem:
        categorias_ordenadas = [c for c in loja.categorias_ordem if c in todas_cats]
        for c in todas_cats:
            if c not in categorias_ordenadas:
                categorias_ordenadas.append(c)
    else:
        categorias_ordenadas = sorted(todas_cats)

    st.write("**Filtrar por Categoria**")

    try:
        selecionadas = st.pills(
            "Filtro",
            options=categorias_ordenadas,
            selection_mode="multi",
            format_func=lambda x: f"{x} ({cat_counts[x]})",
            label_visibility="collapsed",
        )
    except AttributeError:
        selecionadas = st.multiselect(
            "Filtro",
            options=categorias_ordenadas,
            format_func=lambda x: f"{x} ({cat_counts[x]})",
            placeholder="Selecione as categorias...",
            label_visibility="collapsed",
        )

    if not selecionadas:
        st.info("Selecione um ou mais filtros acima para exibir os itens.")
        render_rodape_vitrine()
        return

    def _adicionar_ao_carrinho(produto: Produto) -> None:
        pid_str = str(produto.id)
        if pid_str in st.session_state["carrinho"]:
            st.session_state["carrinho"][pid_str]["qtd"] += 1
        else:
            st.session_state["carrinho"][pid_str] = {
                "nome": produto.nome,
                "preco": produto.preco,
                "qtd": 1,
            }
        st.toast(f"{produto.nome} adicionado.")
        st.rerun()

    for cat in selecionadas:
        st.markdown(f"### {cat}")
        produtos_cat = sorted(
            [p for p in produtos if p.categoria == cat],
            key=lambda x: x.nome.lower(),
        )
        for produto in produtos_cat:
            render_card_produto_vitrine(produto=produto, on_adicionar=_adicionar_ao_carrinho)

    render_rodape_vitrine()