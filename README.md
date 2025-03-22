# Simulação de Experiências da NASA

Este projeto é uma simulação de um sistema de gerenciamento de filas e experiências em um ambiente semelhante ao da NASA. O sistema gerencia a entrada e saída de pessoas em diferentes atrações, garantindo que o número máximo de vagas seja respeitado e que as estatísticas de tempo de espera e ocupação sejam coletadas.

## Como Funciona

O sistema é composto por duas classes principais:

1. **NASAExperience**: Gerencia as atrações, filas e estatísticas. Controla a entrada e saída de pessoas nas experiências, garantindo que o número máximo de vagas seja respeitado.

2. **CriaPessoas**: Uma thread que cria pessoas e as adiciona à fila de espera para as atrações. Cada pessoa é associada a uma experiência aleatória.

## Parâmetros de Entrada

O programa recebe os seguintes parâmetros via linha de comando:

- `N_ATRACOES`: Número de atrações disponíveis.
- `N_PESSOAS`: Número total de pessoas que participarão da simulação.
- `N_VAGAS`: Número máximo de vagas por experiência.
- `PERMANENCIA`: Tempo que cada pessoa permanece na experiência (em milissegundos).
- `MAX_INTERVALO`: Intervalo máximo de tempo entre a chegada de pessoas (em milissegundos).
- `SEMENTE`: Semente para a geração de números aleatórios.
- `UNID_TEMPO`: Unidade de tempo para a simulação (em milissegundos).
