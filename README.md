# pipeline-iot-energia

## Descrição

Pipeline de dados da área Dados/BI que ingere leituras sintéticas de consumo de energia IoT (timestamp, equipamento, kWh), agrega o consumo por hora em SQLite e expõe um dashboard simples: tabela no console e arquivo HTML estático.

Stack: Python + SQLite (apenas stdlib, sem dependência externa em tempo de execução).

## Como usar

### Pré-requisitos

Python 3.10 ou superior. Para rodar os testes: pytest.

### Executar o pipeline

```sh
PYTHONPATH=src python -m pipeline_iot_energia --db consumo.db --leituras 200 --seed 20261015 --html dashboard.html
```

O comando gera 200 leituras sintéticas determinísticas, insere em `consumo.db`, agrega por hora e imprime a tabela no console. Com `--html`, grava também `dashboard.html`.

Exemplo de saída:

```
hora                 equipamento  total_kwh  leituras
-------------------  -----------  ---------  --------
2026-10-15 06:00:00  bomba_01     3.36       1
2026-10-15 06:00:00  bomba_02     4.60       2
...
```

### Testes

```sh
python -m pytest -q
```

Ou com uv:

```sh
uv run --group dev pytest -q
```

A suíte tem 13 testes e cobre: geração determinística por seed, campos obrigatórios das leituras, kWh não negativo, persistência em SQLite, agregação horária com somas verificadas à mão, idempotência da agregação e renderização do dashboard (console e HTML).

## Licença

MIT

## Autor

Kelvin Oliveira

---

## Description

Data pipeline (Data/BI area) that ingests synthetic IoT energy consumption readings (timestamp, equipment, kWh), aggregates consumption by hour in SQLite, and exposes a simple dashboard: a console table and a static HTML file.

Stack: Python + SQLite (stdlib only, no external runtime dependencies).

## How to use

### Requirements

Python 3.10 or higher. To run tests: pytest.

### Run the pipeline

```sh
PYTHONPATH=src python -m pipeline_iot_energia --db consumo.db --leituras 200 --seed 20261015 --html dashboard.html
```

The command generates 200 deterministic synthetic readings, inserts them into `consumo.db`, aggregates by hour and prints the table to the console. With `--html`, it also writes `dashboard.html`.

Example output:

```
hora                 equipamento  total_kwh  leituras
-------------------  -----------  ---------  --------
2026-10-15 06:00:00  bomba_01     3.36       1
2026-10-15 06:00:00  bomba_02     4.60       2
...
```

### Tests

```sh
python -m pytest -q
```

Or with uv:

```sh
uv run --group dev pytest -q
```

The suite has 13 tests covering: deterministic generation by seed, required reading fields, non-negative kWh, SQLite persistence, hourly aggregation with hand-checked sums, aggregation idempotency, and dashboard rendering (console and HTML).

## License

MIT

## Author

Kelvin Oliveira
