"""Dashboard simples: tabela de texto no console e HTML estático."""

from __future__ import annotations

from html import escape
from pathlib import Path

from pipeline_iot_energia.aggregate import aggregate_hourly


def console_table(db_path) -> str:
    """Renderiza a agregação horária como tabela de texto alinhada."""
    linhas = aggregate_hourly(db_path)
    cabecalho = ["hora", "equipamento", "total_kwh", "leituras"]
    rows = [cabecalho] + [
        [hora, equipamento, f"{total:.2f}", str(n)]
        for hora, equipamento, total, n in linhas
    ]
    larguras = [
        max(len(str(celula)) for celula in coluna) for coluna in zip(*rows)
    ]
    partes: list[str] = []
    for i, linha in enumerate(rows):
        partes.append(
            "  ".join(str(celula).ljust(larguras[j]) for j, celula in enumerate(linha))
        )
        if i == 0:
            partes.append("  ".join("-" * largura for largura in larguras))
    return "\n".join(partes)


def print_console(db_path) -> None:
    """Imprime a tabela de agregação no console."""
    print(console_table(db_path))


def render_html(db_path, output_path) -> Path:
    """Gera arquivo HTML estático com a tabela de agregação horária."""
    linhas = aggregate_hourly(db_path)
    corpo = ""
    for hora, equipamento, total, n in linhas:
        corpo += (
            f"<tr><td>{escape(hora)}</td><td>{escape(equipamento)}</td>"
            f"<td>{total:.2f}</td><td>{n}</td></tr>\n"
        )
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>Consumo de Energia — Agregação Horária</title>
<style>
  body {{ font-family: ui-sans-serif, system-ui, sans-serif; margin: 2rem; }}
  table {{ border-collapse: collapse; width: 100%; max-width: 640px; }}
  th, td {{ border: 1px solid #9ca3af; padding: 0.5rem 0.75rem; text-align: left; }}
  th {{ background: #f3f4f6; }}
  tr:nth-child(even) td {{ background: #f9fafb; }}
</style>
</head>
<body>
<h1>Consumo de Energia — Agregação Horária</h1>
<table>
  <thead>
    <tr><th>Hora</th><th>Equipamento</th><th>Total (kWh)</th><th>Leituras</th></tr>
  </thead>
  <tbody>{corpo}</tbody>
</table>
</body>
</html>
"""
    saida = Path(output_path)
    saida.write_text(html, encoding="utf-8")
    return saida
