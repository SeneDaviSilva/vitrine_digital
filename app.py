import urllib.parse
import hashlib
import html
import streamlit as st
import time
import re
import base64
from supabase import create_client, Client

# Configuração da página móvel
st.set_page_config(page_title="Vitrine Digital", layout="centered")

def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# --- ESTILIZAÇÃO MINIMALISTA ---
st.markdown("""
    <style>
    /* Ocultar barra de rolagem para navegadores WebKit (Chrome, Safari, etc) */
    ::-webkit-scrollbar {
        display: none !important;
    }

    /* Ocultar barra de rolagem global, mantendo a funcionalidade do scroll */
    * {
        scrollbar-width: none !important; /* Firefox */
        -ms-overflow-style: none !important; /* IE e Edge */
    }

    /* Configuração global */
    .stApp { 
        max-width: 600px; 
        margin: 0 auto; 
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Títulos limpos */
    h1, h2, h3 {
        letter-spacing: -0.5px;
        font-weight: 600;
    }
    
    .preco-tag { 
        font-size: 1.15rem; 
        font-weight: 600; 
        letter-spacing: -0.5px;
    }

    div[data-testid="stImage"] img {
        object-fit: cover !important;
        aspect-ratio: 1 / 1 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
    }
    
    .stButton button[kind="primary"], div.stButton > button:first-child {
        border-radius: 6px !important;
        font-weight: 500 !important;
        letter-spacing: -0.2px;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODO 1: VITRINE PÚBLICA DO CLIENTE
# ---------------------------------------------------------
query_params = st.query_params
if "loja" in query_params:
    loja_hash = query_params["loja"]
    
    if "carrinho" not in st.session_state:
        st.session_state["carrinho"] = {}
    
    try:
        decodificado = base64.urlsafe_b64decode(loja_hash.encode()).decode()
        loja_id = decodificado.replace("vitrine_", "") 
    except:
        st.error("Link da loja inválido ou corrompido.")
        st.stop()
    
    res_loja = supabase.table("vendedores").select("*").eq("id", loja_id).execute()
    
    if not res_loja.data:
        st.error("Loja não encontrada.")
        st.stop()

    loja = res_loja.data[0]

    def alterar_qtd(pid, delta):
        st.session_state["carrinho"][pid]["qtd"] += delta
        if st.session_state["carrinho"][pid]["qtd"] <= 0:
            del st.session_state["carrinho"][pid]

    def esvaziar_carrinho():
        st.session_state["carrinho"] = {}

    @st.dialog("Seu Pedido")
    def modal_carrinho():
        if not st.session_state["carrinho"]:
            st.warning("Seu carrinho está vazio. Adicione produtos da vitrine.")
            return
        
        total = 0
        for pid, item in list(st.session_state["carrinho"].items()):
            st.markdown(f"<div style='margin-bottom: 4px; font-weight: 600;'>{item['nome']}</div>", unsafe_allow_html=True)
            
            c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
            with c1:
                st.button("-", key=f"dec_{pid}", on_click=alterar_qtd, args=(pid, -1), use_container_width=True)
            with c2:
                st.markdown(f"<div style='text-align:center; padding-top:6px; font-weight:600; font-size:1.1rem;'>{item['qtd']}</div>", unsafe_allow_html=True)
            with c3:
                st.button("+", key=f"inc_{pid}", on_click=alterar_qtd, args=(pid, 1), use_container_width=True)
            with c4:
                st.markdown(f"<div style='text-align:right; padding-top:6px; font-weight:600;'>R$ {(item['preco'] * item['qtd']):.2f}</div>", unsafe_allow_html=True)
            
            total += item['preco'] * item['qtd']
            st.markdown("<hr style='margin: 0.5em 0; border: none; border-top: 1px solid rgba(128,128,128,0.2);'/>", unsafe_allow_html=True)
            
        st.markdown(f"<h3 style='margin-top: 0;'>Total: R$ {total:.2f}</h3>", unsafe_allow_html=True)
        
        texto_msg = "Olá! Gostaria de fazer o seguinte pedido:\n\n"
        for item in st.session_state["carrinho"].values():
            texto_msg += f"- {item['qtd']}x {item['nome']}\n"
        texto_msg += f"\n*Total: R$ {total:.2f}*"
        
        telefone_limpo = "".join(filter(str.isdigit, str(loja["whatsapp"])))
        wa_url = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(texto_msg)}"
        
        st.link_button("Enviar Pedido por WhatsApp", wa_url, type="primary", use_container_width=True)
        st.button("Esvaziar Carrinho", on_click=esvaziar_carrinho, use_container_width=True)

    col_logo, col_info = st.columns([1, 3])
    with col_logo:
        logo = loja.get("logo_url") if loja.get("logo_url") else "https://via.placeholder.com/150?text=Logo"
        st.markdown(f'''
            <img src="{logo}" style="width:100%; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1; border: 1px solid rgba(128, 128, 128, 0.2); box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
        ''', unsafe_allow_html=True)
    with col_info:
        nome_loja_html = html.escape(loja["nome_loja"], quote=True)
        st.markdown(f"<h2 style='margin-bottom: 0; padding-bottom: 0;'>{nome_loja_html}</h2>", unsafe_allow_html=True)
        if loja.get("descricao_loja"):
            descricao_loja_html = html.escape(loja["descricao_loja"], quote=True)
            st.markdown(f"<div style='opacity: 0.7; font-size: 0.95rem; margin-top: 4px; margin-bottom: 12px;'>{descricao_loja_html}</div>", unsafe_allow_html=True)
        
        qtd_itens = sum(item["qtd"] for item in st.session_state["carrinho"].values())
        if st.button(f"Ver Carrinho ({qtd_itens})", type="primary", use_container_width=True):
            modal_carrinho()
            
    st.divider()
    
    res_prod = supabase.table("produtos").select("*").eq("vendedor_id", loja_id).eq("disponivel", True).execute()
    produtos = res_prod.data

    if not produtos:
        st.info("Nenhum produto disponível no momento.")
    else:
        cat_counts = {}
        for p in produtos:
            cat_counts[p['categoria']] = cat_counts.get(p['categoria'], 0) + 1
            
        todas_cats = list(cat_counts.keys())
        ordem_salva = loja.get("categorias_ordem", "")
        
        if ordem_salva:
            ordem_lista = [c.strip() for c in ordem_salva.split(",") if c.strip() in todas_cats]
            for c in todas_cats:
                if c not in ordem_lista:
                    ordem_lista.append(c)
            categorias_ordenadas = ordem_lista
        else:
            categorias_ordenadas = sorted(todas_cats)
            
        st.write("**Filtrar por Categoria**")
        
        try:
            selecionadas = st.pills(
                "Filtro", options=categorias_ordenadas, selection_mode="multi", 
                format_func=lambda x: f"{x} ({cat_counts[x]})", label_visibility="collapsed"
            )
        except AttributeError:
            selecionadas = st.multiselect(
                "Filtro", options=categorias_ordenadas, 
                format_func=lambda x: f"{x} ({cat_counts[x]})",
                placeholder="Selecione as categorias...", label_visibility="collapsed"
            )
            
        if not selecionadas:
            st.info("Selecione um ou mais filtros acima para exibir os itens.")
            cats_para_exibir = []
        else:
            cats_para_exibir = selecionadas
        
        for cat in cats_para_exibir:
            st.markdown(f"### {cat}")
            
            produtos_cat = [p for p in produtos if p["categoria"] == cat]
            produtos_cat = sorted(produtos_cat, key=lambda x: x["nome"].lower())
            
            for p in produtos_cat:
                with st.container():
                    col1, col2 = st.columns([1, 2])
                    
                    with col1:
                        urls_img = [p.get("imagem_url"), p.get("imagem_url_2"), p.get("imagem_url_3")]
                        urls_validas = [u for u in urls_img if u]
                        
                        def render_img_clicavel(url):
                            st.markdown(f'''
                                <a href="{url}" target="_blank">
                                <img src="{url}" style="width:100%; border-radius: 8px; object-fit: cover; aspect-ratio: 1/1; cursor: pointer; border: 1px solid rgba(128, 128, 128, 0.2);">
                                </a>
                            ''', unsafe_allow_html=True)
                        
                        if urls_validas:
                            render_img_clicavel(urls_validas[0])
                            if len(urls_validas) > 1:
                                mini_cols = st.columns(len(urls_validas) - 1)
                                for i, m_col in enumerate(mini_cols):
                                    with m_col:
                                        render_img_clicavel(urls_validas[i+1])
                        else:
                            st.markdown('''
                                <img src="https://via.placeholder.com/150?text=Produto" style="width:100%; border-radius: 8px; object-fit: cover; aspect-ratio: 1/1; border: 1px solid rgba(128, 128, 128, 0.2);">
                            ''', unsafe_allow_html=True)
                            
                    with col2:
                        st.markdown(f"**{p['nome']}**")
                        if p.get("descricao"):
                            st.caption(p.get("descricao"))
                        st.markdown(f"<span class='preco-tag'>R$ {p['preco']:.2f}</span>", unsafe_allow_html=True)
                        
                        if st.button("Adicionar", key=f"add_{p['id']}", use_container_width=True):
                            pid_str = str(p['id'])
                            if pid_str in st.session_state["carrinho"]:
                                st.session_state["carrinho"][pid_str]["qtd"] += 1
                            else:
                                st.session_state["carrinho"][pid_str] = {
                                    "nome": p['nome'], "preco": float(p['preco']), "qtd": 1
                                }
                            st.toast(f"{p['nome']} adicionado.")
                            st.rerun()
                st.markdown("<hr style='margin: 1em 0; border: none; border-top: 1px solid rgba(128,128,128,0.2);'/>", unsafe_allow_html=True)
    
    # --- Rodapé da Vitrine Pública ---
    st.markdown("""
        <div style="text-align: center; margin-top: 50px; margin-bottom: 20px; opacity: 0.3;">
            <span style="font-size: 0.75rem; font-weight: 600; letter-spacing: 0.5px;">POWERED BY VITRINE DIGITAL</span>
        </div>
    """, unsafe_allow_html=True)

    st.stop()

# ---------------------------------------------------------
# MODO 2: ÁREA ADMINISTRATIVA
# ---------------------------------------------------------

if "vendedor_id" not in st.session_state and "is_admin_master" not in st.session_state:
    # --- Tela Inicial de Login Profissional ---
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0 1.5rem 0;">
            <h1 style="font-size: 3rem; font-weight: 700; letter-spacing: -1px; margin-bottom: 0;">Vitrine Digital</h1>
            <p style="opacity: 0.6; font-size: 1.05rem; margin-top: 5px;">Plataforma de gestão para o seu negócio.</p>
        </div>
    """, unsafe_allow_html=True)
    
    aba_login, aba_cadastro = st.tabs(["Entrar", "Criar Conta"])
    
    with aba_login:
        with st.form("form_login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Acessar Painel", type="primary"):
                if email_login.lower() == "admin@vitrinedigital.com" and senha_login == "admin123":
                    st.session_state["is_admin_master"] = True
                    st.rerun()
                
                res = supabase.table("vendedores").select("*").eq("email", email_login.lower()).execute()
                
                if not res.data:
                    st.error("E-mail não encontrado.")
                elif res.data[0]["senha"] != hash_senha(senha_login):
                    st.error("Senha incorreta.")
                else:
                    st.session_state["vendedor_id"] = res.data[0]["id"]
                    st.session_state["nome_loja"] = res.data[0]["nome_loja"]
                    st.rerun()

    with aba_cadastro:
        with st.form("form_nova_loja"):
            novo_nome = st.text_input("Nome da Loja *")
            novo_email = st.text_input("E-mail *")
            novo_whats = st.text_input(
                "WhatsApp (Apenas números com DDD) *",
                max_chars=13, placeholder="5511999998888"
            )
            nova_senha = st.text_input("Senha *", type="password")

            if st.form_submit_button("Cadastrar"):
                if not (novo_nome and novo_email and novo_whats and nova_senha):
                    st.warning("Preencha todos os campos.")
                elif not novo_whats.isdigit():
                    st.error("O WhatsApp deve conter apenas números.")
                elif len(novo_whats) < 10:
                    st.error("Número de telefone incompleto.")
                else:
                    res_nome = supabase.table("vendedores").select("id").eq("nome_loja", novo_nome).execute()
                    res_email = supabase.table("vendedores").select("id").eq("email", novo_email.lower()).execute()
                    res_whats = supabase.table("vendedores").select("id").eq("whatsapp", novo_whats).execute()

                    if res_nome.data:
                        st.error("Já existe uma loja com este nome.")
                    elif res_email.data:
                        st.error("E-mail já cadastrado.")
                    elif res_whats.data:
                        st.error("WhatsApp já cadastrado.")
                    else:
                        try:
                            novo_vendedor = {
                                "nome_loja": novo_nome, "email": novo_email.lower(),
                                "whatsapp": novo_whats, "senha": hash_senha(nova_senha)
                            }
                            supabase.table("vendedores").insert(novo_vendedor).execute()
                            st.success("Conta criada. Vá para a aba 'Entrar'.")
                        except Exception as e:
                            st.error(f"Erro: {e}")

elif "is_admin_master" in st.session_state and "vendedor_id" not in st.session_state:
    st.markdown("""
        <div style="padding: 1rem 0;">
            <h2 style="margin-bottom: 0;">Vitrine Digital</h2>
            <p style="opacity: 0.6;">Administração Global do Sistema</p>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Sair"):
        del st.session_state["is_admin_master"]
        st.rerun()
        
    st.subheader("Gerenciamento de Lojas")
    res_todas = supabase.table("vendedores").select("*").execute()
    todas_lojas = res_todas.data
    
    if not todas_lojas:
        st.warning("Nenhuma loja cadastrada.")
    else:
        lojas_dict = {f"{l['nome_loja']} ({l['email']})": l for l in todas_lojas}
        loja_escolhida = st.selectbox("Selecione a loja:", list(lojas_dict.keys()))
        
        if st.button("Gerenciar Loja", type="primary"):
            loja_alvo = lojas_dict[loja_escolhida]
            st.session_state["vendedor_id"] = loja_alvo["id"]
            st.session_state["nome_loja"] = loja_alvo["nome_loja"]
            st.rerun()
            
        st.divider()
        st.markdown(f"**Total de Lojas:** {len(todas_lojas)}")
        for l in todas_lojas:
            st.text(f"{l['nome_loja']} — {l['email']}")

else:
    vid = st.session_state["vendedor_id"]

    if "msg_sucesso" in st.session_state:
        st.toast(st.session_state["msg_sucesso"])
        del st.session_state["msg_sucesso"]

    # --- Cabeçalho com Logo do Lojista ---
    res_header_loja = supabase.table("vendedores").select("logo_url").eq("id", vid).execute()
    logo_admin = res_header_loja.data[0].get("logo_url") if res_header_loja.data else None
    img_src = logo_admin if logo_admin else "https://via.placeholder.com/150?text=Loja"
    img_src_html = html.escape(img_src, quote=True)
    nome_loja_html = html.escape(st.session_state["nome_loja"], quote=True)

    c_logo, c_titulo, c_sair = st.columns([1, 2.5, 1.5])
    with c_logo:
        st.markdown(f'''
            <img src="{img_src_html}" style="width: 100%; max-width: 75px; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1; border: 1px solid rgba(128, 128, 128, 0.2); margin-top: 5px;">
        ''', unsafe_allow_html=True)

    with c_titulo:
        st.markdown(f"<h2 style='margin-bottom: 0; padding-bottom: 0; margin-top: 0;'>{nome_loja_html}</h2>", unsafe_allow_html=True)
        st.markdown("<div style='opacity: 0.6; font-size: 0.95rem; margin-bottom: 12px;'>Painel de Gestão</div>", unsafe_allow_html=True)
    
    with c_sair:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True) # Espaçamento para alinhar o botão
        if "is_admin_master" in st.session_state:
            if st.button("Sair (Admin)", use_container_width=True):
                del st.session_state["vendedor_id"]
                del st.session_state["nome_loja"]
                st.rerun()
        else:
            if st.button("Sair", use_container_width=True):
                del st.session_state["vendedor_id"]
                del st.session_state["nome_loja"]
                st.rerun()

    URL_BASE = "https://vitrine-digital.streamlit.app"
    id_string = f"vitrine_{vid}"
    id_criptografado = base64.urlsafe_b64encode(id_string.encode()).decode()
    link_vitrine = f"{URL_BASE}/?loja={id_criptografado}"

    # --- Exibição do Link Público mais moderno e integrada ---
    link_vitrine_html = html.escape(link_vitrine, quote=True)
    st.markdown(f"""
        <div style="background-color: rgba(128,128,128,0.05); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(128,128,128,0.1); margin-bottom: 24px;">
            <span style="font-size: 0.85rem; opacity: 0.7;">Compartilhe este link com seus clientes:</span><br>
            <a href="{link_vitrine_html}" target="_blank" style="font-weight: 500; text-decoration: none; color: #2e7d32;">{link_vitrine_html}</a>
        </div>
    """, unsafe_allow_html=True)

    @st.dialog("Editar Produto")
    def modal_editar_produto(item):
        res_cats = supabase.table("produtos").select("categoria").eq("vendedor_id", vid).execute()
        categorias_existentes = sorted(list(set(c["categoria"] for c in res_cats.data)))
        opcoes_categoria = categorias_existentes + ["+ Criar nova categoria"]
        
        idx_padrao = opcoes_categoria.index(item['categoria']) if item['categoria'] in opcoes_categoria else 0

        with st.form(f"form_edit_{item['id']}", clear_on_submit=False):
            edit_nome = st.text_input("Nome", value=item['nome'])
            edit_desc = st.text_area("Descrição", value=item.get('descricao', ''))
            edit_preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f", value=float(item['preco']))
            
            cat_selecionada = st.selectbox("Categoria", options=opcoes_categoria, index=idx_padrao)
            if cat_selecionada == "+ Criar nova categoria":
                edit_cat = st.text_input("Nova Categoria")
            else:
                edit_cat = cat_selecionada
            
            edit_imagens = st.file_uploader(
                "Substituir Fotos (Máximo 3)", type=["png", "jpg", "jpeg", "webp"], 
                accept_multiple_files=True, key=f"up_{item['id']}"
            )
            
            if st.form_submit_button("Salvar"):
                if not edit_nome or not edit_cat or edit_preco <= 0:
                    st.error("Preencha os campos obrigatórios.")
                elif len(edit_imagens) > 3:
                    st.error("Máximo de 3 fotos permitidas.")
                else:
                    update_data = {
                        "nome": edit_nome, "descricao": edit_desc,
                        "preco": edit_preco, "categoria": edit_cat
                    }
                    
                    if edit_imagens:
                        urls_geradas = [None, None, None]
                        upload_succeeded = True
                        for idx, img_file in enumerate(edit_imagens):
                            try:
                                ext = img_file.name.split(".")[-1]
                                nome_arquivo = f"{vid}_edit_{int(time.time())}_{idx}.{ext}"
                                supabase.storage.from_("produtos").upload(
                                    path=nome_arquivo, file=img_file.getvalue(), 
                                    file_options={"content-type": img_file.type}
                                )
                                urls_geradas[idx] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                            except Exception as err:
                                st.error(f"Erro no upload: {err}")
                                upload_succeeded = False
                                break
                                
                        if upload_succeeded:
                            update_data["imagem_url"] = urls_geradas[0]
                            update_data["imagem_url_2"] = urls_geradas[1]
                            update_data["imagem_url_3"] = urls_geradas[2]
                    
                    supabase.table("produtos").update(update_data).eq("id", item['id']).execute()
                    st.session_state["msg_sucesso"] = "Produto atualizado."
                    st.rerun()

    @st.dialog("Novo Produto")
    def modal_novo_produto():
        res_cats = supabase.table("produtos").select("categoria").eq("vendedor_id", vid).execute()
        categorias_existentes = sorted(list(set(c["categoria"] for c in res_cats.data)))
        opcoes_categoria = categorias_existentes + ["+ Criar nova categoria"]

        with st.form("form_produto", clear_on_submit=True):
            nome = st.text_input("Nome *")
            descricao = st.text_area("Descrição")
            preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f", value=None)
            
            cat_selecionada = st.selectbox("Categoria *", options=opcoes_categoria)
            if cat_selecionada == "+ Criar nova categoria":
                categoria = st.text_input("Nova Categoria *")
            else:
                categoria = cat_selecionada

            imagens_arquivo = st.file_uploader("Fotos (Máximo 3)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

            if st.form_submit_button("Adicionar"):
                if not nome or not categoria or preco is None or preco <= 0:
                    st.error("Preencha os campos obrigatórios.")
                elif len(imagens_arquivo) > 3:
                    st.error("Máximo de 3 fotos permitidas.")
                else:
                    urls_geradas = [None, None, None]
                    upload_succeeded = True

                    if imagens_arquivo:
                        for idx, img_file in enumerate(imagens_arquivo):
                            try:
                                ext = img_file.name.split(".")[-1]
                                nome_arquivo = f"{vid}_{int(time.time())}_{idx}.{ext}"
                                supabase.storage.from_("produtos").upload(
                                    path=nome_arquivo, file=img_file.getvalue(),
                                    file_options={"content-type": img_file.type}
                                )
                                urls_geradas[idx] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                            except Exception as err:
                                st.error(f"Erro no upload: {err}")
                                upload_succeeded = False
                                break

                    if upload_succeeded:
                        supabase.table("produtos").insert({
                            "vendedor_id": vid, "nome": nome, "descricao": descricao,
                            "preco": preco, "categoria": categoria,
                            "imagem_url": urls_geradas[0], "imagem_url_2": urls_geradas[1],
                            "imagem_url_3": urls_geradas[2], "disponivel": True
                        }).execute()

                        st.session_state["msg_sucesso"] = "Produto cadastrado."
                        st.rerun()

    @st.dialog("Cadastro em Massa")
    def modal_cadastro_massa():
        st.markdown("Cole seus produtos separando-os por uma linha em branco.")
        st.code("Café Especial\nPreço: 24.90\nCategoria: Bebidas\nDescrição: 250g torra média", language="text")
        
        texto_importacao = st.text_area("Bloco de texto:", height=250)
        
        if st.button("Importar", type="primary"):
            if not texto_importacao.strip():
                st.error("Campo vazio.")
                return
                
            produtos_para_inserir = []
            blocos = re.split(r'\n\s*\n', texto_importacao.strip())
            
            for bloco in blocos:
                linhas = bloco.strip().split('\n')
                if not linhas or not linhas[0]: continue
                
                nome = linhas[0].strip()
                preco = 0.0
                categoria = "Geral"
                descricao = ""
                
                for linha in linhas[1:]:
                    l_lower = linha.lower()
                    if l_lower.startswith('preço:') or l_lower.startswith('preco:'):
                        try:
                            p_str = linha.split(':', 1)[1].strip().replace('R$', '').replace(',', '.')
                            preco = float(p_str)
                        except:
                            pass
                    elif l_lower.startswith('categoria:'):
                        categoria = linha.split(':', 1)[1].strip()
                    elif l_lower.startswith('descrição:') or l_lower.startswith('descricao:'):
                        descricao = linha.split(':', 1)[1].strip()
                        
                if nome and preco > 0:
                    produtos_para_inserir.append({
                        "vendedor_id": vid, "nome": nome[:255], "preco": preco,
                        "categoria": categoria, "descricao": descricao, "disponivel": True
                    })
            
            if produtos_para_inserir:
                supabase.table("produtos").insert(produtos_para_inserir).execute()
                st.session_state["msg_sucesso"] = f"{len(produtos_para_inserir)} produtos importados."
                st.rerun()
            else:
                st.error("Nenhum produto válido encontrado.")

    tab_gerenciamento, tab_config = st.tabs(["Produtos", "Configurações"])

    with tab_gerenciamento:
        c_add1, c_add2 = st.columns(2)
        with c_add1:
            if st.button("Novo Produto", type="primary", use_container_width=True):
                modal_novo_produto()
        with c_add2:
            if st.button("Importar em Massa", use_container_width=True):
                modal_cadastro_massa()
            
        st.divider()

        res_meus_prod = supabase.table("produtos").select("*").eq("vendedor_id", vid).execute()
        meus_produtos = res_meus_prod.data

        if not meus_produtos:
            st.info("Nenhum produto cadastrado.")
        else:
            categorias_admin = sorted(list(set(p["categoria"] for p in meus_produtos)))
            
            for cat in categorias_admin:
                st.markdown(f"#### {cat}") 
                produtos_cat_admin = [p for p in meus_produtos if p["categoria"] == cat]
                produtos_cat_admin = sorted(produtos_cat_admin, key=lambda x: x["nome"].lower())
                
                for item in produtos_cat_admin:
                    c1, c2, c3, c4 = st.columns([3.5, 1.5, 1, 1])
                    with c1:
                        img_url = item.get("imagem_url") or "https://via.placeholder.com/150?text=Sem+Foto"
                        st.markdown(f"""
                            <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 8px;'>
                                <img src="{img_url}" style="width: 44px; height: 44px; object-fit: cover; border-radius: 8px; border: 1px solid rgba(128, 128, 128, 0.2);">
                                <div style="line-height: 1.2;">
                                    <div style="font-weight: 600;">{item['nome']}</div>
                                    <div style="opacity: 0.7; font-size: 0.9rem;">R$ {item['preco']:.2f}</div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c2:
                        novo_status = st.toggle("Ativo", value=item["disponivel"], key=f"status_{item['id']}")
                        if novo_status != item["disponivel"]:
                            supabase.table("produtos").update({"disponivel": novo_status}).eq("id", item["id"]).execute()
                            st.rerun()
                    with c3:
                        if st.button("Editar", key=f"btn_edit_{item['id']}"):
                            modal_editar_produto(item)
                    with c4:
                        if st.button("Excluir", key=f"del_{item['id']}"):
                            supabase.table("produtos").delete().eq("id", item["id"]).execute()
                            st.rerun()
                    st.divider()

    with tab_config:
        res_minha_loja = supabase.table("vendedores").select("*").eq("id", vid).execute()
        dados_loja = res_minha_loja.data[0]

        with st.form("form_config_loja"):
            st.subheader("Perfil e Ajustes")
            edit_nome_loja = st.text_input("Nome da Loja", value=dados_loja['nome_loja'])
            edit_email = st.text_input("E-mail", value=dados_loja['email'])
            edit_whats = st.text_input("WhatsApp", value=dados_loja['whatsapp'], max_chars=13)
            
            edit_desc_loja = st.text_area(
                "Apresentação",
                value=dados_loja.get('descricao_loja', '')
            )
            
            st.divider()
            st.subheader("Ordem das Categorias")
            
            res_cats = supabase.table("produtos").select("categoria").eq("vendedor_id", vid).execute()
            minhas_cats_unicas = list(set(p['categoria'] for p in res_cats.data))
            
            ordem_atual_str = dados_loja.get("categorias_ordem") or ""
            if ordem_atual_str:
                ordem_atual_lista = [c.strip() for c in ordem_atual_str.split(",") if c.strip() in minhas_cats_unicas]
            else:
                ordem_atual_lista = []
                
            for c in minhas_cats_unicas:
                if c not in ordem_atual_lista:
                    ordem_atual_lista.append(c)
                    
            nova_ordem_cats = st.multiselect(
                "Arraste ou selecione a prioridade", 
                options=minhas_cats_unicas, 
                default=ordem_atual_lista,
            )

            st.divider()
            edit_logo = st.file_uploader("Logo da Loja", type=["png", "jpg", "jpeg", "webp"])

            if st.form_submit_button("Salvar Alterações"):
                if not edit_nome_loja or not edit_email or not edit_whats:
                    st.error("Preencha os campos obrigatórios.")
                elif not edit_whats.isdigit():
                    st.error("O WhatsApp deve conter apenas números.")
                elif len(edit_whats) < 10:
                    st.error("Telefone incompleto.")
                else:
                    res_nome_check = supabase.table("vendedores").select("id").eq("nome_loja", edit_nome_loja).neq("id", vid).execute()
                    res_email_check = supabase.table("vendedores").select("id").eq("email", edit_email.lower()).neq("id", vid).execute()
                    res_whats_check = supabase.table("vendedores").select("id").eq("whatsapp", edit_whats).neq("id", vid).execute()
                    
                    if res_nome_check.data:
                        st.error("Nome de loja já em uso.")
                    elif res_email_check.data:
                        st.error("E-mail já em uso.")
                    elif res_whats_check.data:
                        st.error("WhatsApp já vinculado a outra conta.")
                    else:
                        update_loja = {
                            "nome_loja": edit_nome_loja,
                            "email": edit_email.lower(),
                            "whatsapp": edit_whats,
                            "descricao_loja": edit_desc_loja,
                            "categorias_ordem": ",".join(nova_ordem_cats)
                        }
                        upload_succeeded = True

                        if edit_logo:
                            try:
                                ext = edit_logo.name.split(".")[-1]
                                nome_arquivo = f"logo_{vid}_{int(time.time())}.{ext}"
                                supabase.storage.from_("produtos").upload(
                                    path=nome_arquivo, file=edit_logo.getvalue(),
                                    file_options={"content-type": edit_logo.type}
                                )
                                update_loja["logo_url"] = supabase.storage.from_("produtos").get_public_url(nome_arquivo)
                            except Exception as e:
                                st.error(f"Erro no upload da logo: {e}")
                                upload_succeeded = False

                        if upload_succeeded:
                            try:
                                supabase.table("vendedores").update(update_loja).eq("id", vid).execute()
                                st.session_state["nome_loja"] = edit_nome_loja
                                st.session_state["msg_sucesso"] = "Configurações salvas."
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro no banco de dados: {e}")