tempo limite em ms
valor minimo em R$
percentual em %
#especificação: sistema de calculo de frete

## Requisitos funcionais:
- **(Event-Driven)** RF-01: WHEN o usuário calcular o frete e o carrinho atingir o limite regional, THE SYSTEM SHALL zerar o frete.
- **(Event-Driven)** RF-02: WHEN o usuário adicionar um produto THE SYSTEM SHALL recalcular o frete e o valor total.
- **(unwanted Behaviour)** RF-03: IF ocorrer erro no cálculo do frete THEN, exibir mensagem 'erro no calculo do frete' e manter valor anterior

## Regras de negocios e funções:
- **(State-Driven)** RB-01: WHILE a região for 'norte', o limite é R$ 300. Demais regiões: R$ 200.
- **(unwanted Behaviour)** RB-02: IF valor <=0, THEN exibir erro 'valor de carrinho invalido'.
- **(Unwanted Behaviour)** RB-03: IF o carrinho estiver vazio, THEN exibir mensagem 'carrinho vazio' e parar de calcular o frete.