"""Ingestão de leituras IoT sintéticas (timestamp, equipamento, kWh) em SQLite."""

from __future__ import annotations

import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

DEFAULT_DB_PATH = Path("pipeline_iot_energia.db")
EQUIPAMENTOS_PADRAO = ("bomba_01", "bomba_02", "bomba_03")

CREATE_LEITURAS = """
CREATE TABLE IF NOT EXISTS leituras (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    equipamento TEXT NOT NULL,
    kwh REAL NOT NULL
)
"""

CREATE_INDEX_LEITURAS = """
CREATE INDEX IF NOT EXISTS idx_leituras_equip_ts
    ON leituras (equipamento, timestamp)
"""


@dataclass(frozen=True)
class Reading:
    """Leitura de consumo de um equipamento em um instante."""

    timestamp: str
    equipamento: str
    kwh: float


def generate_readings(
    qtd: int,
    *,
    seed: int,
    start: str,
    equipamentos: tuple[str, ...],
) -> list[Reading]:
    """Gera ``qtd`` leituras sintéticas determinísticas a partir de ``seed``.

    Minutos dentro do dia e kWh são sorteados com ``random.Random(seed)``:
    mesma semente reproduz a mesma lista, sempre.
    """
    if qtd < 0:
        raise ValueError(f"qtd deve ser >= 0, recebeu {qtd}")
    if not equipamentos:
        raise ValueError("equipamentos não pode ser vazio")

    rng = random.Random(seed)
    base = datetime.fromisoformat(start)
    leituras: list[Reading] = []
    for _ in range(qtd):
        minutos = rng.randrange(0, 60 * 24)
        ts = base + timedelta(minutes=minutos)
        timestamp = ts.strftime("%Y-%m-%d %H:%M:%S")
        equipamento = equipamentos[rng.randrange(len(equipamentos))]
        kwh = round(rng.uniform(0.5, 5.0), 2)
        leituras.append(Reading(timestamp=timestamp, equipamento=equipamento, kwh=kwh))
    return leituras


def init_db(db_path: str | Path) -> None:
    """Cria as tabelas ``leituras`` e ``consumo_hora`` se ainda não existirem."""
    con = sqlite3.connect(db_path)
    try:
        con.execute(CREATE_LEITURAS)
        con.execute(CREATE_INDEX_LEITURAS)
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS consumo_hora (
                hora TEXT NOT NULL,
                equipamento TEXT NOT NULL,
                total_kwh REAL NOT NULL,
                n_leituras INTEGER NOT NULL,
                PRIMARY KEY (hora, equipamento)
            )
            """
        )
        con.commit()
    finally:
        con.close()


def insert_readings(db_path: str | Path, leituras: list[Reading]) -> int:
    """Insere leituras na tabela e retorna a quantidade inserida."""
    con = sqlite3.connect(db_path)
    try:
        cur = con.executemany(
            "INSERT INTO leituras (timestamp, equipamento, kwh) VALUES (?, ?, ?)",
            [
                (leitura.timestamp, leitura.equipamento, leitura.kwh)
                for leitura in leituras
            ],
        )
        con.commit()
        return cur.rowcount if cur.rowcount >= 0 else len(leituras)
    finally:
        con.close()
