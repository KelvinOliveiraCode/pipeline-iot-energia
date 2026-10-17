"""Suite de testes do pipeline-iot-energia.

Escrita antes do código (TDD). Cada teste nomeia a quebra que catcha e
usa valores esperados derivados à mão — nunca espelhados do código sob teste.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

import pytest

from pipeline_iot_energia.aggregate import aggregate_hourly
from pipeline_iot_energia.dashboard import console_table, render_html
from pipeline_iot_energia.ingest import (
    DEFAULT_DB_PATH,
    Reading,
    generate_readings,
    init_db,
    insert_readings,
)

EQUIPAMENTOS = ("bomba_01", "bomba_02", "bomba_03")


def test_generate_readings_retorna_quantidade_solicitada() -> None:
    leituras = generate_readings(
        47, seed=7, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    assert len(leituras) == 47


def test_generate_readings_tem_campos_obrigatorios() -> None:
    leituras = generate_readings(
        10, seed=1, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    for leitura in leituras:
        assert isinstance(leitura, Reading)
        assert leitura.timestamp
        assert leitura.equipamento in EQUIPAMENTOS
        assert isinstance(leitura.kwh, float)


def test_generate_readings_kwh_nao_eh_negativo() -> None:
    leituras = generate_readings(
        100, seed=3, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    for leitura in leituras:
        assert leitura.kwh >= 0.0


def test_generate_readings_eh_deterministico_pelo_seed() -> None:
    a = generate_readings(
        30, seed=42, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    b = generate_readings(
        30, seed=42, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    assert a == b


def test_timestamp_eh_iso_parseavel() -> None:
    leituras = generate_readings(
        5, seed=9, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    for leitura in leituras:
        datetime.fromisoformat(leitura.timestamp)


def test_default_db_path_é_path() -> None:
    assert isinstance(DEFAULT_DB_PATH, Path)


def test_init_db_cria_tabelas(tmp_path: Path) -> None:
    db = tmp_path / "energia.db"
    init_db(db)
    assert db.exists()
    con = sqlite3.connect(db)
    try:
        tabelas = {
            row[0]
            for row in con.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
        }
        assert "leituras" in tabelas
        assert "consumo_hora" in tabelas
    finally:
        con.close()


def test_insert_readings_persiste_contagem(tmp_path: Path) -> None:
    db = tmp_path / "energia.db"
    init_db(db)
    leituras = generate_readings(
        25, seed=5, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    inseridos = insert_readings(db, leituras)
    assert inseridos == 25
    con = sqlite3.connect(db)
    try:
        (total,) = con.execute("SELECT COUNT(*) FROM leituras").fetchone()
        assert total == 25
    finally:
        con.close()


def test_aggregate_banco_vazio_retorna_lista_vazia(tmp_path: Path) -> None:
    db = tmp_path / "vazio.db"
    init_db(db)
    assert aggregate_hourly(db) == []


def test_aggregate_hourly_soma_kwh_por_hora_e_equipamento(tmp_path: Path) -> None:
    db = tmp_path / "energia.db"
    init_db(db)
    fix = [
        Reading("2026-10-15 08:05:00", "bomba_01", 1.5),
        Reading("2026-10-15 08:40:00", "bomba_01", 2.5),
        Reading("2026-10-15 09:10:00", "bomba_01", 1.0),
        Reading("2026-10-15 08:20:00", "bomba_02", 3.0),
    ]
    insert_readings(db, fix)
    linhas = aggregate_hourly(db)
    assert linhas == [
        ("2026-10-15 08:00:00", "bomba_01", 4.0, 2),
        ("2026-10-15 08:00:00", "bomba_02", 3.0, 1),
        ("2026-10-15 09:00:00", "bomba_01", 1.0, 1),
    ]


def test_aggregate_execucao_repetida_eh_idempotente(tmp_path: Path) -> None:
    db = tmp_path / "energia.db"
    init_db(db)
    leituras = generate_readings(
        40, seed=11, start="2026-10-15 06:00:00", equipamentos=EQUIPAMENTOS
    )
    insert_readings(db, leituras)
    primeira = aggregate_hourly(db)
    segunda = aggregate_hourly(db)
    assert primeira == segunda
    con = sqlite3.connect(db)
    try:
        (total,) = con.execute("SELECT COUNT(*) FROM consumo_hora").fetchone()
        assert total == len(segunda)
    finally:
        con.close()


def test_console_table_contem_cabecalho_e_dados(tmp_path: Path) -> None:
    db = tmp_path / "energia.db"
    init_db(db)
    fix = [
        Reading("2026-10-15 08:05:00", "bomba_01", 1.5),
        Reading("2026-10-15 08:40:00", "bomba_01", 2.5),
    ]
    insert_readings(db, fix)
    aggregate_hourly(db)
    saida = console_table(db)
    assert "hora" in saida.lower()
    assert "bomba_01" in saida
    assert "4.00" in saida


def test_render_html_cria_arquivo_com_tabela(tmp_path: Path) -> None:
    db = tmp_path / "energia.db"
    init_db(db)
    fix = [Reading("2026-10-15 08:05:00", "bomba_01", 1.5)]
    insert_readings(db, fix)
    aggregate_hourly(db)
    saida = tmp_path / "dashboard.html"
    caminho = render_html(db, saida)
    assert caminho == saida
    assert saida.exists()
    conteudo = saida.read_text(encoding="utf-8")
    assert "<table" in conteudo
    assert "bomba_01" in conteudo
    assert "1.50" in conteudo
