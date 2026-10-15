#!/usr/bin/env python3
"""Calculadora de linha de comando.

Exemplos::

    python3 cli.py "2+2*3"
    python3 cli.py --deg "sin(30)"
    python3 cli.py "sqrt(2)" "1/7"        # várias expressões de uma vez
    python3 cli.py --tabela 1 2 3 4 5     # executa tudo e mostra uma tabela
    python3 cli.py                        # modo interativo (REPL)

Em qualquer lugar, ``-`` lê a expressão da entrada padrão::

    echo "2^16" | python3 cli.py -
"""

from __future__ import annotations

import argparse
import sys

from calculator import CalculatorError, evaluate


def _fmt(expression: str, angle: str) -> tuple[str, str, str | None]:
    """Devolve (expressão, resultado, erro)."""
    try:
        return expression, evaluate(expression, angle=angle).text, None
    except CalculatorError as error:
        return expression, "-", str(error)


def _run_batch(expressions: list[str], angle: str, table: bool) -> int:
    failures = 0
    for expression in expressions:
        text, result, error = _fmt(expression, angle)
        if table:
            print(f"{text:<28} = {result:<22}{'' if error is None else error}")
        elif error is None:
            print(result)
        else:
            print(f"Erro: {error}", file=sys.stderr)
        failures += error is not None
    return 1 if failures else 0


def _run_repl(angle: str) -> int:
    history: list[tuple[str, str]] = []
    print(f"Calculadora Python — modo interativo ({angle}). ':ajuda' para comandos.")
    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        lowered = line.lower()
        if lowered in {"sair", "exit", "quit", "q"}:
            return 0
        if lowered in {":ajuda", ":help", ":h"}:
            print("  :deg | :rad   alterna o modo de ângulo")
            print("  :historico    mostra as contas desta sessão")
            print("  sair          encerra")
            continue
        if lowered in {":deg", ":graus"}:
            angle = "deg"
            print("modo: graus")
            continue
        if lowered in {":rad", ":radianos"}:
            angle = "rad"
            print("modo: radianos")
            continue
        if lowered == ":historico":
            if not history:
                print("  (nenhum cálculo ainda)")
            for expression, result in history:
                print(f"  {expression} = {result}")
            continue
        try:
            result = evaluate(line, angle=angle)
        except CalculatorError as error:
            print(f"Erro: {error}", file=sys.stderr)
        else:
            history.append((line, result.text))
            print(f"= {result.text}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Calculadora Python de linha de comando.",
        epilog='exemplo: python3 cli.py --deg "sin(30)^2 + cos(30)^2"',
    )
    parser.add_argument("expressoes", nargs="*", help='expressões, ex.: "2+2"')
    parser.add_argument("-d", "--deg", "--graus", action="store_true",
                        help="interpreta ângulos em graus (padrão: radianos)")
    parser.add_argument("-t", "--tabela", action="store_true",
                        help="mostra expressão e resultado em colunas")
    args = parser.parse_args(argv)
    angle = "deg" if args.deg else "rad"

    expressions = list(args.expressoes)
    if expressions and expressions[0] == "-":
        expressions = [line.strip() for line in sys.stdin if line.strip()]

    if not expressions:
        return _run_repl(angle)
    return _run_batch(expressions, angle, args.tabela)


if __name__ == "__main__":
    raise SystemExit(main())
