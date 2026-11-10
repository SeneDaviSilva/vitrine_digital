import urllib.parse
import hashlib
import streamlit as st
import time
import re
import base64
from supabase import create_client, Client

# Configuração da página móvel
st.set_page_config(page_title="Vitrine Digital", page_icon="🍲", layout="centered")

def init_supabase() -> Client:
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_supabase()

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

st.markdown("""
    <style>
    .stApp { max-width: 600px; margin: 0 auto; }
    .card-produto { border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; margin-bottom: 16px; background-color: #ffffff;}
    .preco-tag { color: #2e7d32; font-size: 1.25rem; font-weight: bold; }
    div[data-testid="stImage"] img {
        object-fit: cover !important;
        aspect-ratio: 1 / 1 !important;
        border-radius: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MODO 1: VITRINE PÚBLICA DO CLIENTE (Via parâmetro na URL)
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
        st.error("❌ Link da loja inválido ou corrompido!")
        st.stop()
    
    res_loja = supabase.table("vendedores").select("*").eq("id", loja_id).execute()
    
    if not res_loja.data:
        st.error("Loja não encontrada!")
        st.stop()

    loja = res_loja.data[0]

    @st.dialog("🛒 Seu Pedido")
    def modal_carrinho():
        if not st.session_state["carrinho"]:
            st.warning("Seu carrinho está vazio! Adicione produtos da vitrine.")
            return
        
        total = 0
        for pid, item in list(st.session_state["carrinho"].items()):
            st.markdown(f"**{item['nome']}**")
            c1, c2, c3, c4 = st.columns([1, 1, 1, 2])
            with c1:
                if st.button("➖", key=f"dec_{pid}"):
                    st.session_state["carrinho"][pid]["qtd"] -= 1
                    if st.session_state["carrinho"][pid]["qtd"] <= 0:
                        del st.session_state["carrinho"][pid]
                    st.rerun()
            with c2:
                st.markdown(f"<div style='text-align:center; padding-top:8px;'>**{item['qtd']}**</div>", unsafe_allow_html=True)
            with c3:
                if st.button("➕", key=f"inc_{pid}"):
                    st.session_state["carrinho"][pid]["qtd"] += 1
                    st.rerun()
            with c4:
                st.markdown(f"<div style='text-align:right; padding-top:8px; color:#2e7d32; font-weight:bold;'>R$ {(item['preco'] * item['qtd']):.2f}</div>", unsafe_allow_html=True)
            
            total += item['preco'] * item['qtd']
            st.divider()
            
        st.subheader(f"Total: R$ {total:.2f}")
        
        texto_msg = "Olá! Gostaria de fazer o seguinte pedido:\n\n"
        for item in st.session_state["carrinho"].values():
            texto_msg += f"- {item['qtd']}x {item['nome']}\n"
        texto_msg += f"\n*Total: R$ {total:.2f}*"
        
        telefone_limpo = "".join(filter(str.isdigit, str(loja["whatsapp"])))
        wa_url = f"https://wa.me/{telefone_limpo}?text={urllib.parse.quote(texto_msg)}"
        
        st.link_button("📲 Enviar Pedido por WhatsApp", wa_url, type="primary", use_container_width=True)
        
        if st.button("🗑️ Esvaziar Carrinho", use_container_width=True):
            st.session_state["carrinho"] = {}
            st.rerun()

    col_logo, col_info = st.columns([1, 3])
    with col_logo:
        logo = loja.get("logo_url") if loja.get("logo_url") else "https://via.placeholder.com/150?text=Sua+Logo"
        st.markdown(f'''
            <img src="{logo}" style="width:100%; border-radius: 50%; object-fit: cover; aspect-ratio: 1/1; border: 3px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        ''', unsafe_allow_html=True)
    with col_info:
        st.title(f"🏪 {loja['nome_loja']}")
        if loja.get("descricao_loja"):
            st.write(loja["descricao_loja"])
        
        qtd_itens = sum(item["qtd"] for item in st.session_state["carrinho"].values())
        if st.button(f"🛒 Ver Carrinho ({qtd_itens} itens)", type="primary", use_container_width=True):
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
            
        st.write("🔍 **Buscar por Setor**")
        
        try:
            selecionadas = st.pills(
                "Filtro", options=categorias_ordenadas, selection_mode="multi", 
                format_func=lambda x: f"{x} ({cat_counts[x]})", label_visibility="collapsed"
            )
        except AttributeError:
            selecionadas = st.multiselect(
                "Filtro", options=categorias_ordenadas, 
                format_func=lambda x: f"{x} ({cat_counts[x]})",
                placeholder="Todos os Setores (Clique para filtrar)", label_visibility="collapsed"
            )
            
        # --- ALTERAÇÃO 30: Só exibe se houver filtro selecionado ---
        if not selecionadas:
            st.info("👆 Selecione um ou mais setores acima para visualizar o cardápio.")
            cats_para_exibir = []
        else:
            cats_para_exibir = selecionadas
        
        for cat in cats_para_exibir:
            st.header(f"📌 {cat}")
            
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
                                <img src="{url}" style="width:100%; border-radius: 10px; object-fit: cover; aspect-ratio: 1/1; cursor: pointer; border: 1px solid #eee;">
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
                                <img src="https://via.placeholder.com/150?text=Sem+Foto" style="width:100%; border-radius: 10px; object-fit: cover; aspect-ratio: 1/1; border: 1px solid #eee;">
                            ''', unsafe_allow_html=True)
                            
                    with col2:
                        st.subheader(p["nome"])
                        st.write(p.get("descricao", ""))
                        st.markdown(f"<span class='preco-tag'>R$ {p['preco']:.2f}</span>", unsafe_allow_html=True)
                        
                        if st.button("➕ Adicionar", key=f"add_{p['id']}", use_container_width=True):
                            pid_str = str(p['id'])
                            if pid_str in st.session_state["carrinho"]:
                                st.session_state["carrinho"][pid_str]["qtd"] += 1
                            else:
                                st.session_state["carrinho"][pid_str] = {
                                    "nome": p['nome'], "preco": float(p['preco']), "qtd": 1
                                }
                            st.toast(f"{p['nome']} adicionado ao carrinho!", icon="🛒")
                            st.rerun()
                st.divider()
    
    st.stop()

# ---------------------------------------------------------
# MODO 2: ÁREA ADMINISTRATIVA (Login e Painel da Vendedora)
# ---------------------------------------------------------

if "vendedor_id" not in st.session_state and "is_admin_master" not in st.session_state:
    st.title("🔐 Acesso Restrito - Vendedores")
    
    aba_login, aba_cadastro = st.tabs(["Fazer Login", "Criar minha Loja"])
    
    with aba_login:
        with st.form("form_login"):
            email_login = st.text_input("E-mail")
            senha_login = st.text_input("Senha", type="password")
            
            if st.form_submit_button("Entrar", type="primary"):
                if email_login.lower() == "admin@vitrinedigital.com" and senha_login == "admin123":
                    st.session_state["is_admin_master"] = True
                    st.rerun()
                
                res = supabase.table("vendedores").select("*").eq("email", email_login.lower()).execute()
                
                if not res.data:
                    st.error("❌ E-mail não cadastrado. Verifique a digitação ou crie uma conta.")
                elif res.data[0]["senha"] != hash_senha(senha_login):
                    st.error("❌ Senha incorreta.")
                else:
                    st.session_state["vendedor_id"] = res.data[0]["id"]
                    st.session_state["nome_loja"] = res.data[0]["nome_loja"]
                    st.rerun()

    with aba_cadastro:
        with st.form("form_nova_loja"):
            novo_nome = st.text_input("Nome da sua Loja/Negócio *")
            novo_email = st.text_input("Seu E-mail *")
            novo_whats = st.text_input(
                "WhatsApp para Pedidos (Apenas números com DDD) *",
                max_chars=13, placeholder="5511999998888", help="Digite APENAS números, sem espaços ou traços."
            )
            nova_senha = st.text_input("Crie uma Senha *", type="password")

            if st.form_submit_button("Criar Conta"):
                if not (novo_nome and novo_email and novo_whats and nova_senha):
                    st.warning("Preencha todos os campos obrigatórios (*).")
                elif not novo_whats.isdigit():
                    st.error("❌ O campo de WhatsApp não aceita letras ou símbolos! Digite APENAS números.")
                elif len(novo_whats) < 10:
                    st.error("❌ Telefone incompleto! Faltou o DDD ou números do celular.")
                else:
                    res_nome = supabase.table("vendedores").select("id").eq("nome_loja", novo_nome).execute()
                    res_email = supabase.table("vendedores").select("id").eq("email", novo_email.lower()).execute()
                    res_whats = supabase.table("vendedores").select("id").eq("whatsapp", novo_whats).execute()

                    if res_nome.data:
                        st.error("❌ Já existe uma loja cadastrada com este nome! Escolha outro para se diferenciar.")
                    elif res_email.data:
                        st.error("❌ Este e-mail já está cadastrado em outra conta!")
                    elif res_whats.data:
                        st.error("❌ Este WhatsApp já está cadastrado em outra loja!")
                    else:
                        try:
                            novo_vendedor = {
                                "nome_loja": novo_nome, "email": novo_email.lower(),
                                "whatsapp": novo_whats, "senha": hash_senha(nova_senha)
                            }
                            supabase.table("vendedores").insert(novo_vendedor).execute()
                            st.success("Conta criada com sucesso! Vá para a aba 'Fazer Login' para entrar.")
                        except Exception as e:
                            st.error(f"Erro ao criar conta: {e}")

elif "is_admin_master" in st.session_state and "vendedor_id" not in st.session_state:
    st.title("👑 Painel Supremo - Administração")
    st.info("Você está logado com acesso total ao sistema.")
    
    if st.button("Sair (Logout do Sistema)"):
        del st.session_state["is_admin_master"]
        st.rerun()
        
    st.subheader("Selecione uma loja para gerenciar")
    res_todas = supabase.table("vendedores").select("*").execute()
    todas_lojas = res_todas.data
    
    if not todas_lojas:
        st.warning("Nenhuma loja cadastrada no sistema ainda.")
    else:
        lojas_dict = {f"{l['nome_loja']} ({l['email']})": l for l in todas_lojas}
        loja_escolhida = st.selectbox("Lojas Cadastradas:", list(lojas_dict.keys()))
        
        if st.button("Acessar Painel Desta Loja", type="primary"):
            loja_alvo = lojas_dict[loja_escolhida]
            st.session_state["vendedor_id"] = loja_alvo["id"]
            st.session_state["nome_loja"] = loja_alvo["nome_loja"]
            st.rerun()
            
        st.divider()
        st.markdown(f"### Total de contas ativas: {len(todas_lojas)}")
        for l in todas_lojas:
            st.markdown(f"🏪 **{l['nome_loja']}** | 📧 {l['email']} | 📱 {l['whatsapp']}")

else:
    vid = st.session_state["vendedor_id"]

    if "msg_sucesso" in st.session_state:
        st.toast(st.session_state["msg_sucesso"], icon="✅")
        del st.session_state["msg_sucesso"]

    c_titulo, c_sair = st.columns([3, 2])
    with c_titulo:
        st.title(f"Painel: {st.session_state['nome_loja']}")
    
    with c_sair:
        if "is_admin_master" in st.session_state:
            if st.button("👑 Voltar ao Menu Admin", use_container_width=True):
                del st.session_state["vendedor_id"]
                del st.session_state["nome_loja"]
                st.rerun()
        else:
            if st.button("Sair (Logout)", use_container_width=True):
                del st.session_state["vendedor_id"]
                del st.session_state["nome_loja"]
                st.rerun()

    URL_BASE = "https://vitrine-digital.streamlit.app"
    id_string = f"vitrine_{vid}"
    id_criptografado = base64.urlsafe_b64encode(id_string.encode()).decode()
    link_vitrine = f"{URL_BASE}/?loja={id_criptografado}"
    st.success(f"**Seu Link Exclusivo para clientes:**\n\n{link_vitrine}")

    @st.dialog("✏️ Editar Produto")
    def modal_editar_produto(item):
        with st.form(f"form_edit_{item['id']}", clear_on_submit=False):
            edit_nome = st.text_input("Nome", value=item['nome'])
            edit_desc = st.text_area("Descrição", value=item.get('descricao', ''))
            edit_preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f", value=float(item['preco']))
            edit_cat = st.text_input("Categoria", value=item['categoria'])
            
            st.caption("Para manter fotos atuais, não envie nada. Troca máxima de 3 novas fotos.")
            edit_imagens = st.file_uploader(
                "Substituir Fotos (Máximo 3)", type=["png", "jpg", "jpeg", "webp"], 
                accept_multiple_files=True, key=f"up_{item['id']}"
            )
            
            if st.form_submit_button("Salvar Alterações"):
                if not edit_nome or not edit_cat or edit_preco <= 0:
                    st.error("Preencha Nome, Preço e Categoria.")
                elif len(edit_imagens) > 3:
                    st.error("❌ Envie no máximo 3 fotos!")
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
                                st.error(f"Erro ao atualizar foto: {err}")
                                upload_succeeded = False
                                break
                                
                        if upload_succeeded:
                            update_data["imagem_url"] = urls_geradas[0]
                            update_data["imagem_url_2"] = urls_geradas[1]
                            update_data["imagem_url_3"] = urls_geradas[2]
                    
                    supabase.table("produtos").update(update_data).eq("id", item['id']).execute()
                    st.session_state["msg_sucesso"] = "Alterações salvas com sucesso!"
                    st.rerun()

    @st.dialog("➕ Cadastrar 1 Novo Produto")
    def modal_novo_produto():
        with st.form("form_produto", clear_on_submit=True):
            nome = st.text_input("Nome do Produto *")
            descricao = st.text_area("Descrição (Ingredientes, tamanho)")
            preco = st.number_input("Preço (R$)", min_value=0.0, step=0.50, format="%.2f", value=None)
            categoria = st.text_input("Categoria *")

            imagens_arquivo = st.file_uploader("Fotos do Produto (Máximo 3)", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=True)

            if st.form_submit_button("Salvar Produto"):
                if not nome or not categoria or preco is None or preco <= 0:
                    st.error("Preencha os campos obrigatórios (*).")
                elif len(imagens_arquivo) > 3:
                    st.error("❌ Você pode enviar no máximo 3 fotos por produto!")
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
                                st.error(f"Erro ao enviar foto {idx+1}: {err}")
                                upload_succeeded = False
                                break

                    if upload_succeeded:
                        supabase.table("produtos").insert({
                            "vendedor_id": vid, "nome": nome, "descricao": descricao,
                            "preco": preco, "categoria": categoria,
                            "imagem_url": urls_geradas[0], "imagem_url_2": urls_geradas[1],
                            "imagem_url_3": urls_geradas[2], "disponivel": True
                        }).execute()

                        st.session_state["msg_sucesso"] = "Novo produto cadastrado com sucesso!"
                        st.rerun()

    # --- ALTERAÇÃO 31: Novo Modal no Estilo Pokémon Showdown ---
    @st.dialog("⚡ Cadastro Rápido em Massa")
    def modal_cadastro_massa():
        st.markdown("Copie e cole seus produtos. **Deixe sempre uma linha em branco entre cada produto.**")
        st.code("Bolo de Cenoura\nPreço: 15.50\nCategoria: Bolos\nDescrição: Cobertura de chocolate\n\nCoxinha de Frango\nPreço: 7.00\nCategoria: Salgados", language="text")
        
        texto_importacao = st.text_area("Cole seu cardápio aqui:", height=300)
        
        if st.button("Processar e Salvar Tudo", type="primary"):
            if not texto_importacao.strip():
                st.error("O campo está vazio.")
                return
                
            produtos_para_inserir = []
            # Separa os produtos ignorando espaços vazios extras
            blocos = re.split(r'\n\s*\n', texto_importacao.strip())
            
            erros = 0
            for bloco in blocos:
                linhas = bloco.strip().split('\n')
                if not linhas or not linhas[0]: continue
                
                nome = linhas[0].strip()
                preco = 0.0
                categoria = "Sem Categoria"
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
                        "vendedor_id": vid,
                        "nome": nome[:255],
                        "preco": preco,
                        "categoria": categoria,
                        "descricao": descricao,
                        "disponivel": True
                    })
                else:
                    erros += 1
            
            if produtos_para_inserir:
                supabase.table("produtos").insert(produtos_para_inserir).execute()
                st.session_state["msg_sucesso"] = f"{len(produtos_para_inserir)} produtos cadastrados com sucesso!"
                if erros > 0:
                    st.session_state["msg_sucesso"] += f" ({erros} ignorados por erro de formatação)."
                st.rerun()
            else:
                st.error("❌ Nenhum produto válido encontrado. Verifique se digitou o 'Preço:' corretamente.")

    tab_gerenciamento, tab_config = st.tabs(["📦 Meus Produtos", "⚙️ Configurações da Loja"])

    with tab_gerenciamento:
        # Divide os botões em duas colunas para a vendedora escolher
        c_add1, c_add2 = st.columns(2)
        with c_add1:
            if st.button("➕ Cadastrar Novo", type="primary", use_container_width=True):
                modal_novo_produto()
        with c_add2:
            if st.button("⚡ Cadastro em Massa (Texto)", type="secondary", use_container_width=True):
                modal_cadastro_massa()
            
        st.divider()

        res_meus_prod = supabase.table("produtos").select("*").eq("vendedor_id", vid).execute()
        meus_produtos = res_meus_prod.data

        if not meus_produtos:
            st.info("Você ainda não tem produtos cadastrados.")
        else:
            categorias_admin = sorted(list(set(p["categoria"] for p in meus_produtos)))
            
            for cat in categorias_admin:
                st.markdown(f"#### 📁 {cat}") 
                produtos_cat_admin = [p for p in meus_produtos if p["categoria"] == cat]
                produtos_cat_admin = sorted(produtos_cat_admin, key=lambda x: x["nome"].lower())
                
                for item in produtos_cat_admin:
                    c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
                    with c1:
                        st.write(f"**{item['nome']}** - R$ {item['preco']:.2f}")
                    with c2:
                        novo_status = st.toggle("Ativo", value=item["disponivel"], key=f"status_{item['id']}")
                        if novo_status != item["disponivel"]:
                            supabase.table("produtos").update({"disponivel": novo_status}).eq("id", item["id"]).execute()
                            st.rerun()
                    with c3:
                        if st.button("✏️", key=f"btn_edit_{item['id']}", help="Editar Produto"):
                            modal_editar_produto(item)
                    with c4:
                        if st.button("🗑️", key=f"del_{item['id']}", help="Excluir Produto"):
                            supabase.table("produtos").delete().eq("id", item["id"]).execute()
                            st.rerun()
                    st.divider()

    with tab_config:
        res_minha_loja = supabase.table("vendedores").select("*").eq("id", vid).execute()
        dados_loja = res_minha_loja.data[0]

        with st.form("form_config_loja"):
            st.subheader("Personalizar Perfil da Vitrine")
            edit_nome_loja = st.text_input("Nome da Loja", value=dados_loja['nome_loja'])
            edit_email = st.text_input("E-mail de Login", value=dados_loja['email'])
            edit_whats = st.text_input("WhatsApp para Pedidos", value=dados_loja['whatsapp'], max_chars=13)
            
            edit_desc_loja = st.text_area(
                "Apresentação / Descrição da Loja",
                value=dados_loja.get('descricao_loja', ''),
                help="Ex: Bolos artesanais feitos com carinho. Atendimento das 08h às 18h."
            )
            
            st.divider()
            st.subheader("Ordem das Categorias (Vitrine)")
            st.caption("Limpe a caixa e vá selecionando suas categorias na ordem que deseja que seus clientes vejam (a primeira fica no topo).")
            
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
                "Organize as Categorias", 
                options=minhas_cats_unicas, 
                default=ordem_atual_lista,
            )

            st.divider()
            st.caption("Para manter a logo atual, não envie nada. Para trocar, envie uma nova foto.")
            edit_logo = st.file_uploader("Logo / Foto de Perfil da Loja", type=["png", "jpg", "jpeg", "webp"])

            if st.form_submit_button("Salvar Configurações"):
                if not edit_nome_loja or not edit_email or not edit_whats:
                    st.error("Nome, E-mail e WhatsApp são obrigatórios!")
                elif not edit_whats.isdigit():
                    st.error("❌ O WhatsApp deve conter apenas números!")
                elif len(edit_whats) < 10:
                    st.error("❌ Telefone incompleto! Faltou o DDD ou números.")
                else:
                    res_nome_check = supabase.table("vendedores").select("id").eq("nome_loja", edit_nome_loja).neq("id", vid).execute()
                    res_email_check = supabase.table("vendedores").select("id").eq("email", edit_email.lower()).neq("id", vid).execute()
                    res_whats_check = supabase.table("vendedores").select("id").eq("whatsapp", edit_whats).neq("id", vid).execute()
                    
                    if res_nome_check.data:
                        st.error("❌ Outra loja já usa este nome! Escolha outro.")
                    elif res_email_check.data:
                        st.error("❌ Este e-mail já pertence a outra loja!")
                    elif res_whats_check.data:
                        st.error("❌ Este WhatsApp já está vinculado a outra loja!")
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
                                st.error(f"Erro ao enviar logo: {e}")
                                upload_succeeded = False

                        if upload_succeeded:
                            try:
                                supabase.table("vendedores").update(update_loja).eq("id", vid).execute()
                                st.session_state["nome_loja"] = edit_nome_loja
                                st.session_state["msg_sucesso"] = "Perfil da loja atualizado com sucesso!"
                                st.rerun()
                            except Exception as e:
                                st.error(f"⚠️ Erro ao salvar banco de dados: {e}")