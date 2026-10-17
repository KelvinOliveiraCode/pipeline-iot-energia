"""CLI: ingestão sintética, agregação horária e dashboard do console."""

from __future__ import annotations

import argparse

from pipeline_iot_energia.aggregate import aggregate_hourly
from pipeline_iot_energia.dashboard import print_console, render_html
from pipeline_iot_energia.ingest import (
    DEFAULT_DB_PATH,
    EQUIPAMENTOS_PADRAO,
    generate_readings,
    init_db,
    insert_readings,
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pipeline-iot-energia")
    parser.add_argument("--db", default=DEFAULT_DB_PATH)
    parser.add_argument("--leituras", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20261015)
    parser.add_argument("--start", default="2026-10-15 06:00:00")
    parser.add_argument("--html", default=None)
    args = parser.parse_args(argv)

    leituras = generate_readings(
        args.leituras,
        seed=args.seed,
        start=args.start,
        equipamentos=EQUIPAMENTOS_PADRAO,
    )
    init_db(args.db)
    inseridos = insert_readings(args.db, leituras)
    linhas = aggregate_hourly(args.db)
    print_console(args.db)
    if args.html:
        render_html(args.db, args.html)
        print(f"HTML escrito em {args.html}")
    print(f"{inseridos} leituras ingeridas; {len(linhas)} horas agregadas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
