import pytest
from frete import (
    LIMITE_REGIONAL_NORTE,
    LIMITE_REGIONAL_DEMAIS,
    FRETE_PADRAO_NORTE,
    FRETE_PADRAO_DEMAIS,
    CarrinhoVazioError,
    ValorCarrinhoInvalidoError,
    CalculoFreteError,
    obter_limite_regional,
    calcular_frete,
    calcular_total,
)


# =====================================================================
# RB-01: WHILE a região for 'norte', o limite é R$ 300. Demais: R$ 200.
# =====================================================================
def test_limite_regional_norte():
    assert obter_limite_regional("norte") == 300.0
    assert obter_limite_regional("NORTE") == 300.0
    assert obter_limite_regional("  norte  ") == 300.0


def test_limite_regional_demais_regioes():
    assert obter_limite_regional("sudeste") == 200.0
    assert obter_limite_regional("sul") == 200.0
    assert obter_limite_regional("nordeste") == 200.0
    assert obter_limite_regional("centro-oeste") == 200.0
    assert obter_limite_regional("demais") == 200.0


# =====================================================================
# RF-01: WHEN o carrinho atingir o limite regional, zerar o frete.
# =====================================================================
def test_frete_zerado_regiao_norte_limite_exato():
    assert calcular_frete(valor=300.0, regiao="norte") == 0.0


def test_frete_zerado_regiao_norte_acima_limite():
    assert calcular_frete(valor=450.0, regiao="norte") == 0.0


def test_frete_tarifado_regiao_norte_abaixo_limite():
    frete = calcular_frete(valor=299.99, regiao="norte")
    assert frete == FRETE_PADRAO_NORTE
    assert frete > 0.0


def test_frete_zerado_demais_regioes_limite_exato():
    assert calcular_frete(valor=200.0, regiao="sudeste") == 0.0
    assert calcular_frete(valor=200.0, regiao="sul") == 0.0


def test_frete_zerado_demais_regioes_acima_limite():
    assert calcular_frete(valor=250.0, regiao="nordeste") == 0.0


def test_frete_tarifado_demais_regioes_abaixo_limite():
    frete = calcular_frete(valor=199.99, regiao="sudeste")
    assert frete == FRETE_PADRAO_DEMAIS
    assert frete > 0.0


# =====================================================================
# RB-02: IF valor <= 0, THEN exibir erro 'valor de carrinho invalido'.
# =====================================================================
@pytest.mark.parametrize("valor_invalido", [0, 0.0, -1, -50.0, -0.01])
def test_valor_carrinho_invalido(valor_invalido):
    with pytest.raises(ValorCarrinhoInvalidoError) as exc_info:
        calcular_frete(valor=valor_invalido, regiao="sudeste")
    assert "valor de carrinho invalido" in str(exc_info.value)

    # Verifica se também é capturado como ValueError padrão
    with pytest.raises(ValueError):
        calcular_frete(valor=valor_invalido, regiao="sudeste")


# =====================================================================
# RB-03: IF carrinho vazio, THEN exibir mensagem 'carrinho vazio' e parar.
# =====================================================================
def test_carrinho_vazio_lista_vazia():
    with pytest.raises(CarrinhoVazioError) as exc_info:
        calcular_frete(itens=[], regiao="sul")
    assert "carrinho vazio" in str(exc_info.value)


def test_carrinho_vazio_sem_valor_e_sem_itens():
    with pytest.raises(CarrinhoVazioError) as exc_info:
        calcular_frete(valor=None, itens=None, regiao="norte")
    assert "carrinho vazio" in str(exc_info.value)


# =====================================================================
# RF-03: IF erro no calculo, THEN mensagem 'erro no calculo do frete'.
# =====================================================================
def test_erro_calculo_regiao_invalida():
    with pytest.raises(CalculoFreteError) as exc_info:
        calcular_frete(valor=100.0, regiao=None)
    assert "erro no calculo do frete" in str(exc_info.value)


def test_erro_calculo_valor_nao_numerico():
    with pytest.raises(CalculoFreteError) as exc_info:
        calcular_frete(valor="texto_invalido", regiao="sul")
    assert "erro no calculo do frete" in str(exc_info.value)


# =====================================================================
# RF-02: Recalcular o frete e o valor total ao adicionar produto.
# =====================================================================
def test_calcular_total_com_itens_abaixo_limite():
    itens = [
        {"nome": "Camiseta", "preco": 50.0, "quantidade": 2},  # 100.0
        {"nome": "Caneca", "preco": 30.0, "quantidade": 1},    # 30.0 -> total 130.0
    ]
    resultado = calcular_total(itens=itens, regiao="sudeste")
    assert resultado["status"] == "sucesso"
    assert resultado["valor_carrinho"] == 130.0
    assert resultado["limite_regional"] == 200.0
    assert resultado["frete"] == FRETE_PADRAO_DEMAIS
    assert resultado["frete_gratis"] is False
    assert resultado["total"] == 130.0 + FRETE_PADRAO_DEMAIS


def test_calcular_total_recalculo_ao_adicionar_atinge_frete_gratis():
    # Carrinho inicial com 1 produto de R$ 130 no Sudeste (frete R$ 20)
    itens = [{"nome": "Teclado", "preco": 130.0, "quantidade": 1}]
    res1 = calcular_total(itens=itens, regiao="sudeste")
    assert res1["frete"] == 20.0
    assert res1["total"] == 150.0

    # Adiciona produto de R$ 80.0 -> total carrinho 210.0 (atinge limite de 200.0)
    itens.append({"nome": "Mouse", "preco": 80.0, "quantidade": 1})
    res2 = calcular_total(itens=itens, regiao="sudeste")
    assert res2["valor_carrinho"] == 210.0
    assert res2["frete"] == 0.0
    assert res2["frete_gratis"] is True
    assert res2["total"] == 210.0
