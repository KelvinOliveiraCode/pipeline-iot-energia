# BRIEF — pipeline-iot-energia

## Projeto

`pipeline-iot-energia` — área Dados/BI. Agregação horária de consumo de energia (leituras IoT sintéticas) + dashboard.

## Stack

Python 3.10+, SQLite (stdlib apenas).

## Entregas

| Caminho | O que é |
|---|---|
| `pyproject.toml` | Projeto Python (src layout), script de entrada, grupo de dev com pytest |
| `src/pipeline_iot_energia/__init__.py` | Pacote, versão 0.1.0 |
| `src/pipeline_iot_energia/ingest.py` | Geração determinística de leituras (seed), criação de tabelas, inserção em SQLite |
| `src/pipeline_iot_energia/aggregate.py` | Agregação horária por equipamento (`strftime('%Y-%m-%d %H:00:00', timestamp)`, `SUM(kwh)`, `COUNT(*)`), idempotente |
| `src/pipeline_iot_energia/dashboard.py` | Tabela de texto no console e dashboard HTML estático |
| `src/pipeline_iot_energia/__main__.py` | CLI: `python -m pipeline_iot_energia [--db] [--leituras] [--seed] [--start] [--html]` |
| `tests/test_pipeline.py` | 13 testes pytest (TDD: escritos antes do código) |
| `README.md` | Documentação completa PT-BR + EN |
| `BRIEF.md` | Este resumo |

## Critérios de aceitação (do PLANO_50_PROJETOS.md)

- Agregação correta: coberto por `test_aggregate_hourly_soma_kwh_por_hora_e_equipamento` com valores esperados derivados à mão
- Testes que passem: veja abaixo
- README PT/EN completo: `README.md`

## Como verificar

```sh
# na raiz do projeto
python -m pytest -q
```

Resultado esperado: `13 passed`.

Execução ponta-a-ponta:

```sh
PYTHONPATH=src python -m pipeline_iot_energia --db consumo.db --leituras 200 --seed 20261015 --html dashboard.html
```

Saída: tabela de consumo por hora no console + arquivo `dashboard.html`.

## Autor

Kelvin Oliveira
