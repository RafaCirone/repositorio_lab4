"""
Módulo de cálculo de frete baseado na especificação de requisitos:
- RF-01: WHEN o usuário calcular o frete e o carrinho atingir o limite regional, THE SYSTEM SHALL zerar o frete.
- RF-02: WHEN o usuário adicionar um produto THE SYSTEM SHALL recalcular o frete e o valor total.
- RF-03: IF ocorrer erro no cálculo do frete THEN, exibir mensagem 'erro no calculo do frete' e manter valor anterior.
- RB-01: WHILE a região for 'norte', o limite é R$ 300. Demais regiões: R$ 200.
- RB-02: IF valor <=0, THEN exibir erro 'valor de carrinho invalido'.
- RB-03: IF o carrinho estiver vazio, THEN exibir mensagem 'carrinho vazio' e parar de calcular o frete.
"""

from typing import Any, Dict, List, Optional, Union

# Constantes de regras de negócio
LIMITE_REGIONAL_NORTE = 300.0
LIMITE_REGIONAL_DEMAIS = 200.0

FRETE_PADRAO_NORTE = 50.0
FRETE_PADRAO_DEMAIS = 20.0


# Hierarquia de exceções de domínio
class FreteError(ValueError):
    """Exceção base para erros do domínio de frete."""
    pass


class CarrinhoVazioError(FreteError):
    """RB-03: IF o carrinho estiver vazio, THEN exibir mensagem 'carrinho vazio' e parar de calcular o frete."""
    def __init__(self, message: str = "carrinho vazio") -> None:
        super().__init__(message)


class ValorCarrinhoInvalidoError(FreteError):
    """RB-02: IF valor <=0, THEN exibir erro 'valor de carrinho invalido'."""
    def __init__(self, message: str = "valor de carrinho invalido") -> None:
        super().__init__(message)


class CalculoFreteError(FreteError):
    """RF-03: IF ocorrer erro no cálculo do frete THEN, exibir mensagem 'erro no calculo do frete'."""
    def __init__(self, message: str = "erro no calculo do frete") -> None:
        super().__init__(message)


def obter_limite_regional(regiao: Any) -> float:
    """
    Retorna o limite para frete grátis de acordo com a região (RB-01).
    - Região 'norte': R$ 300.00
    - Demais regiões: R$ 200.00
    """
    if not isinstance(regiao, str) or not regiao.strip():
        raise CalculoFreteError("erro no calculo do frete")
    
    regiao_normalizada = regiao.strip().lower()
    if regiao_normalizada == "norte":
        return LIMITE_REGIONAL_NORTE
    return LIMITE_REGIONAL_DEMAIS


def obter_frete_base(regiao: Any) -> float:
    """
    Retorna a tarifa de frete padrão regional quando o limite de frete grátis não for atingido.
    """
    if not isinstance(regiao, str) or not regiao.strip():
        raise CalculoFreteError("erro no calculo do frete")
    
    regiao_normalizada = regiao.strip().lower()
    if regiao_normalizada == "norte":
        return FRETE_PADRAO_NORTE
    return FRETE_PADRAO_DEMAIS


def calcular_frete(
    valor: Optional[Union[float, int, str]] = None,
    regiao: str = "demais",
    itens: Optional[List[Dict[str, Any]]] = None,
    frete_base: Optional[float] = None
) -> float:
    """
    Calcula o valor do frete aplicando as regras de negócio:
    - RB-03: Carrinho vazio gera erro 'carrinho vazio' e para o cálculo.
    - RB-02: Valor <= 0 gera erro 'valor de carrinho invalido'.
    - RF-03: Falha no cálculo gera 'erro no calculo do frete'.
    - RB-01 e RF-01: Se valor atingir o limite regional (300 Norte, 200 demais), zera o frete.
    """
    # RB-03: validação de carrinho vazio quando a lista de itens for informada
    if itens is not None:
        if not isinstance(itens, list) or len(itens) == 0:
            raise CarrinhoVazioError("carrinho vazio")
        # Se valor não foi fornecido explicitamente, soma os itens
        if valor is None:
            try:
                valor = sum(
                    float(item.get("preco", item.get("valor", 0))) * int(item.get("quantidade", 1))
                    for item in itens
                )
            except (ValueError, TypeError, AttributeError):
                raise CalculoFreteError("erro no calculo do frete")
    elif valor is None:
        raise CarrinhoVazioError("carrinho vazio")

    # Conversão e validação do valor do carrinho
    try:
        valor_float = float(valor)
    except (ValueError, TypeError):
        raise CalculoFreteError("erro no calculo do frete")

    # RB-02: IF valor <= 0, THEN exibir erro 'valor de carrinho invalido'
    if valor_float <= 0:
        raise ValorCarrinhoInvalidoError("valor de carrinho invalido")

    # Validação e obtenção do limite regional (RB-01)
    limite = obter_limite_regional(regiao)

    # RF-01: Se o carrinho atingir o limite regional, zera o frete
    if valor_float >= limite:
        return 0.0

    # Se abaixo do limite, aplica a tarifa base regional
    if frete_base is not None:
        return float(frete_base)
    return obter_frete_base(regiao)


def calcular_total(
    valor: Optional[Union[float, int, str]] = None,
    regiao: str = "demais",
    itens: Optional[List[Dict[str, Any]]] = None,
    frete_base: Optional[float] = None
) -> Dict[str, Any]:
    """
    Calcula o frete e consolida o valor total e informações regionais.
    RF-02: Recalcula o frete e o valor total.
    """
    # Se itens foram passados e valor é None, calcular valor
    if itens is not None and valor is None:
        if len(itens) == 0:
            raise CarrinhoVazioError("carrinho vazio")
        try:
            valor = sum(
                float(item.get("preco", item.get("valor", 0))) * int(item.get("quantidade", 1))
                for item in itens
            )
        except (ValueError, TypeError, AttributeError):
            raise CalculoFreteError("erro no calculo do frete")

    frete = calcular_frete(valor=valor, regiao=regiao, itens=itens, frete_base=frete_base)
    valor_float = float(valor)
    limite = obter_limite_regional(regiao)
    total = round(valor_float + frete, 2)

    return {
        "status": "sucesso",
        "valor_carrinho": round(valor_float, 2),
        "regiao": regiao.strip().lower() if isinstance(regiao, str) else regiao,
        "limite_regional": limite,
        "frete": round(frete, 2),
        "frete_gratis": frete == 0.0,
        "total": total,
    }
