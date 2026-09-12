import logging
from flask import Flask, jsonify, render_template, request

from frete import (
    CalculoFreteError,
    CarrinhoVazioError,
    ValorCarrinhoInvalidoError,
    calcular_total,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    """Servir a página principal da aplicação."""
    return render_template("index.html")


@app.route("/calcular", methods=["POST"])
def calcular():
    """
    Endpoint POST /calcular para cálculo de frete e total do carrinho.
    Suporta payload JSON e form-data.
    Retorna status HTTP 200 com os valores calculados,
    ou HTTP 400 com mensagens de erro padronizadas:
    - 'carrinho vazio' (RB-03)
    - 'valor de carrinho invalido' (RB-02)
    - 'erro no calculo do frete' (RF-03)
    """
    try:
        # Suporta tanto JSON quanto Form Data
        if request.is_json:
            dados = request.get_json() or {}
        else:
            dados = request.form.to_dict()

        # Flags e campos
        carrinho_vazio = dados.get("carrinho_vazio")
        if carrinho_vazio is True or str(carrinho_vazio).lower() == "true":
            return jsonify({
                "status": "erro",
                "erro": "carrinho vazio",
                "mensagem": "carrinho vazio"
            }), 400

        valor = dados.get("valor")
        regiao = dados.get("regiao", "demais")
        itens = dados.get("itens")

        # Se valor for string vazia, tratar como None
        if isinstance(valor, str) and valor.strip() == "":
            valor = None

        resultado = calcular_total(valor=valor, regiao=regiao, itens=itens)
        return jsonify(resultado), 200

    except CarrinhoVazioError as e:
        logger.warning(f"Carrinho vazio: {e}")
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "mensagem": str(e)
        }), 400

    except ValorCarrinhoInvalidoError as e:
        logger.warning(f"Valor de carrinho inválido: {e}")
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "mensagem": str(e)
        }), 400

    except CalculoFreteError as e:
        logger.warning(f"Erro no cálculo do frete: {e}")
        return jsonify({
            "status": "erro",
            "erro": str(e),
            "mensagem": str(e)
        }), 400

    except Exception as e:
        logger.error(f"Exceção não tratada no cálculo: {e}")
        return jsonify({
            "status": "erro",
            "erro": "erro no calculo do frete",
            "mensagem": "erro no calculo do frete"
        }), 400


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
