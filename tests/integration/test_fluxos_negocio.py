import pytest

from src.application.use_cases.auth.autenticar_vendedor import AutenticarVendedorUseCase
from src.application.use_cases.auth.cadastrar_vendedor import CadastrarVendedorUseCase
from src.application.use_cases.auth.redefinir_senha import RedefinirSenhaUseCase
from src.application.use_cases.loja.atualizar_loja import ArquivoUpload, AtualizarLojaUseCase
from src.application.use_cases.loja.cadastrar_loja import CadastrarLojaUseCase
from src.application.use_cases.produto.alternar_disponibilidade import AlternarDisponibilidadeUseCase
from src.application.use_cases.produto.cadastrar_produto import CadastrarProdutoUseCase
from src.application.use_cases.produto.editar_produto import EditarProdutoUseCase
from src.application.use_cases.produto.excluir_produto import ExcluirProdutoUseCase
from src.domain.exceptions import CredenciaisInvalidasError, DuplicidadeError
from src.infra.mappers.loja_mapper import LojaMapper
from src.infra.mappers.produto_mapper import ProdutoMapper


def test_fluxo_completo_onboarding_e_unicidade(vendedor_repo, loja_repo, hasher) -> None:
    cad_vendedor = CadastrarVendedorUseCase(vendedor_repo, hasher)
    cad_loja = CadastrarLojaUseCase(loja_repo)
    auth_vendedor = AutenticarVendedorUseCase(vendedor_repo, hasher)

    # 1. Cadastro válido
    vendedor = cad_vendedor.executar("João Silva", "joao@loja.com", "123456")
    assert vendedor.id is not None

    loja = cad_loja.executar(vendedor.id, "Empório do João", "11999998888", "Produtos artesanais")
    assert loja.id is not None

    # 2. Bloqueio de unicidade (e-mail, nome da loja e WhatsApp)
    with pytest.raises(DuplicidadeError):
        cad_vendedor.executar("Outro João", "joao@loja.com", "123456")

    vendedor2 = cad_vendedor.executar("Maria", "maria@loja.com", "123456")
    assert vendedor2.id is not None

    with pytest.raises(DuplicidadeError):
        cad_loja.executar(vendedor2.id, "Empório do João", "11977776666")

    with pytest.raises(DuplicidadeError):
        cad_loja.executar(vendedor2.id, "Loja da Maria", "11999998888")

    # 3. Autenticação
    autenticado = auth_vendedor.executar("joao@loja.com", "123456")
    assert autenticado.id == vendedor.id


def test_fluxo_redefinicao_de_senha(vendedor_repo, loja_repo, hasher) -> None:
    cad_vendedor = CadastrarVendedorUseCase(vendedor_repo, hasher)
    cad_loja = CadastrarLojaUseCase(loja_repo)
    redefinir_uc = RedefinirSenhaUseCase(vendedor_repo, loja_repo, hasher)
    auth_uc = AutenticarVendedorUseCase(vendedor_repo, hasher)

    vendedor = cad_vendedor.executar("Ana", "ana@loja.com", "senhaAntiga")
    assert vendedor.id is not None
    cad_loja.executar(vendedor.id, "Doces da Ana", "11911112222")

    # Tentativa com WhatsApp errado deve falhar
    with pytest.raises(CredenciaisInvalidasError):
        redefinir_uc.executar("ana@loja.com", "11900000000", "senhaNova")

    # Redefinição correta
    redefinir_uc.executar("ana@loja.com", "11911112222", "senhaNova")
    autenticado = auth_uc.executar("ana@loja.com", "senhaNova")
    assert autenticado.id == vendedor.id


def test_fluxo_crud_produtos_e_mappers(vendedor_repo, loja_repo, produto_repo, storage_repo, hasher) -> None:
    vendedor = CadastrarVendedorUseCase(vendedor_repo, hasher).executar("Carlos", "carlos@loja.com", "1234")
    assert vendedor.id is not None
    loja = CadastrarLojaUseCase(loja_repo).executar(vendedor.id, "Adega Carlos", "11933334444")
    assert loja.id is not None

    cad_prod = CadastrarProdutoUseCase(produto_repo, storage_repo)
    edit_prod = EditarProdutoUseCase(produto_repo, storage_repo)
    toggle_prod = AlternarDisponibilidadeUseCase(produto_repo)
    del_prod = ExcluirProdutoUseCase(produto_repo)

    foto = ArquivoUpload(nome="vinho.jpg", conteudo=b"bytes_imagem", content_type="image/jpeg")
    produto = cad_prod.executar(
        loja_id=loja.id,
        nome="Vinho Tinto",
        preco=89.90,
        categoria="Vinhos",
        imagens=[foto],
    )
    assert produto.id is not None
    assert len(produto.imagens_url) == 1

    # Valida ida e volta dos Mappers (Banco <-> Domínio)
    payload_db = ProdutoMapper.to_persistence(produto)
    entidade_reconstruida = ProdutoMapper.to_entity(payload_db)
    assert entidade_reconstruida.nome == produto.nome
    assert entidade_reconstruida.preco == produto.preco

    payload_loja = LojaMapper.to_persistence(loja)
    loja_reconstruida = LojaMapper.to_entity(payload_loja)
    assert loja_reconstruida.nome_loja == loja.nome_loja

    # Edição e pausa de estoque
    edit_prod.executar(produto.id, "Vinho Tinto Reserva", 110.00, "Vinhos")
    toggle_prod.executar(produto.id, disponivel=False)

    visiveis_cliente = produto_repo.listar_por_loja(loja.id, apenas_visiveis=True)
    todos_lojista = produto_repo.listar_por_loja(loja.id, apenas_visiveis=False)
    assert len(visiveis_cliente) == 0
    assert len(todos_lojista) == 1

    # Exclusão
    del_prod.executar(produto.id)
    assert produto_repo.buscar_por_id(produto.id) is None