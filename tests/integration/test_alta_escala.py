import time
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from src.application.use_cases.loja.cadastrar_loja import CadastrarLojaUseCase
from src.application.use_cases.produto.importar_produtos import ImportarProdutosUseCase
from src.domain.exceptions import DuplicidadeError


def test_importacao_em_massa_1000_produtos_alta_escala(produto_repo) -> None:
    loja_id = uuid4()
    importar_uc = ImportarProdutosUseCase(produto_repo)

    blocos = [
        f"Produto Escala {i}\nPreço: {10 + (i % 50)},90\nCategoria: Categoria {i % 10}\nDescrição: Item de teste {i}"
        for i in range(1000)
    ]
    texto_gigante = "\n\n".join(blocos)

    inicio = time.perf_counter()
    inseridos = importar_uc.executar(loja_id=loja_id, texto_bruto=texto_gigante)
    duracao = time.perf_counter() - inicio

    assert len(inseridos) == 1000
    assert len(produto_repo.listar_por_loja(loja_id)) == 1000
    # Deve processar e persistir 1.000 itens em menos de 1 segundo
    assert duracao < 1.0


def test_concorrencia_50_requisicoes_simultaneas_unicidade(loja_repo) -> None:
    cadastrar_loja_uc = CadastrarLojaUseCase(loja_repo)

    def _tentar_criar_loja_mesmo_nome(indice: int) -> bool:
        try:
            cadastrar_loja_uc.executar(
                vendedor_id=uuid4(),
                nome_loja="Loja Concorrente",
                whatsapp=f"1199999{indice:04d}",
            )
            return True
        except DuplicidadeError:
            return False

    with ThreadPoolExecutor(max_workers=10) as executor:
        resultados = list(executor.map(_tentar_criar_loja_mesmo_nome, range(50)))

    # Apenas 1 loja deve conseguir ser criada; as outras 49 devem ser bloqueadas
    assert sum(1 for r in resultados if r is True) == 1
    assert len(loja_repo.listar_todas()) == 1