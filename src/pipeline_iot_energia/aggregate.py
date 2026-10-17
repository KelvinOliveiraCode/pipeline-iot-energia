"""Agregação horária do consumo de energia em SQLite."""

from __future__ import annotations

import sqlite3
from pathlib import Path

AGREGAR_HORARIO = """
INSERT INTO consumo_hora (hora, equipamento, total_kwh, n_leituras)
SELECT
    strftime('%Y-%m-%d %H:00:00', timestamp) AS hora,
    equipamento,
    ROUND(SUM(kwh), 2) AS total_kwh,
    COUNT(*) AS n_leituras
FROM leituras
GROUP BY hora, equipamento
ORDER BY hora, equipamento
"""


def aggregate_hourly(db_path: str | Path) -> list[tuple[str, str, float, int]]:
    """Agrega leituras por hora e equipamento.

    Recria o conteúdo de ``consumo_hora`` a cada execução (idempotente:
    rodar novamente produz o mesmo resultado, sem duplicatas). Retorna as
    linhas ordenadas por (hora, equipamento).
    """
    con = sqlite3.connect(db_path)
    try:
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
        con.execute("DELETE FROM consumo_hora")
        con.execute(AGREGAR_HORARIO)
        con.commit()
        linhas = con.execute(
            "SELECT hora, equipamento, total_kwh, n_leituras "
            "FROM consumo_hora ORDER BY hora, equipamento"
        ).fetchall()
        return [(hora, equip, float(total), int(n)) for hora, equip, total, n in linhas]
    finally:
        con.close()
