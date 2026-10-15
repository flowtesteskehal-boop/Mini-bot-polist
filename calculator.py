"""Motor de cálculo da calculadora.

Avalia expressões matemáticas escritas pelo usuário **sem usar `eval`**:
a expressão é convertida em uma árvore sintática (``ast``) e apenas os nós
permitidos (números, operadores aritméticos e funções da lista branca) são
avaliados. Isso evita a execução de código arbitrário no servidor.

Depende somente da biblioteca padrão do Python.

Uso como biblioteca::

    >>> from calculator import evaluate
    >>> evaluate("2 + 3 * 4").text
    '14'

Uso pela linha de comando::

    python3 calculator.py "2 ** 10"
    python3 calculator.py --deg "sin(30)"
    python3 calculator.py            # modo interativo (REPL)
"""

from __future__ import annotations

import ast
import math
import operator
import re
import sys
from dataclasses import dataclass
from typing import Any, Callable

__all__ = ["CalculatorError", "Result", "evaluate", "format_number", "normalize"]

# ---------------------------------------------------------------------------
# Limites de segurança
# ---------------------------------------------------------------------------
MAX_LENGTH = 500           # tamanho máximo da expressão
MAX_EXPONENT = 1_000       # limite para o expoente de **
MAX_FACTORIAL = 1_000      # limite para o argumento de factorial()
MAX_TREE_NODES = 400       # limite de nós da árvore sintática


class CalculatorError(ValueError):
    """Erro de cálculo com mensagem amigável (em português)."""


@dataclass(frozen=True)
class Result:
    """Resultado de uma expressão avaliada com sucesso."""

    expression: str          # como o usuário digitou
    normalized: str          # como o Python interpretou (após normalização)
    value: int | float       # valor numérico
    text: str                # valor formatado para exibição
    angle: str               # "deg" ou "rad"

    def as_dict(self) -> dict[str, Any]:
        """Representação pronta para virar JSON."""
        return {
            "ok": True,
            "expression": self.expression,
            "normalized": self.normalized,
            "value": self.value,
            "result": self.text,
            "angle": self.angle,
        }


# ---------------------------------------------------------------------------
# Normalização da expressão
# ---------------------------------------------------------------------------
_UNICODE_REPLACEMENTS = {
    "×": "*", "·": "*", "∗": "*", "✕": "*", "✖": "*",
    "÷": "/", "⁄": "/",
    "−": "-", "–": "-", "—": "-",
    "√": "sqrt(", "∛": "cbrt(",
    "π": "pi", "τ": "tau", "φ": "phi",
    "²": "**2", "³": "**3",
    "，": ",",
}

_NUMBER_RE = re.compile(r"(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?")
_PLACEHOLDER_RE = re.compile(r"\x00(\d+)\x00")


def _replace_symbols(expression: str) -> str:
    out = []
    for char in expression:
        out.append(_UNICODE_REPLACEMENTS.get(char, char))
    return "".join(out)


def _balance_parentheses(expression: str) -> str:
    """Fecha automaticamente parênteses deixados abertos no final.

    Assim ``sqrt(9`` vira ``sqrt(9)`` e ``2*(3+4`` vira ``2*(3+4)``.
    """
    depth = 0
    for char in expression:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
    if depth > 0:
        return expression + ")" * depth
    return expression


def _add_implicit_multiplication(expression: str) -> str:
    """Insere o ``*`` omitido pelo usuário.

    Cobre ``2(3+4)``, ``(1+2)(3+4)``, ``2pi``, ``3sqrt(4)`` e ``(1+2)e``.
    Números são temporariamente trocados por marcadores para que o ``e`` de
    ``2e3`` (notação científica) não seja confundido com a constante ``e``.
    """
    numbers: list[str] = []

    def stash(match: re.Match[str]) -> str:
        numbers.append(match.group(0))
        return f"\x00{len(numbers) - 1}\x00"

    stashed = _NUMBER_RE.sub(stash, expression)
    stashed = re.sub(r"(?<=[\x00\)])\s*(?=\()", "*", stashed)
    stashed = re.sub(r"(?<=[\x00\)])\s*(?=pi\b|e\b|tau\b|phi\b)", "*", stashed)

    def restore(match: re.Match[str]) -> str:
        return numbers[int(match.group(1))]

    return _PLACEHOLDER_RE.sub(restore, stashed)


_POSTFIX_FACTORIAL_RE = re.compile(r"(\d+\.?\d*|\)|pi|e|tau|phi)\s*!(?!=)")


def _replace_postfix_factorial(expression: str) -> str:
    """Converte o fatorial pós-fixado: ``5!`` vira ``factorial(5)``."""
    previous = None
    result = expression
    for _ in range(10):                      # permite "3!!" e afins
        previous, result = result, _POSTFIX_FACTORIAL_RE.sub(r"factorial(\1)", result)
        if result == previous:
            break
    return result


def normalize(expression: str) -> str:
    """Converte o que o usuário digitou em uma expressão Python válida."""
    normalized = _replace_symbols(expression).strip()
    normalized = normalized.replace("^", "**")
    normalized = _replace_postfix_factorial(normalized)
    normalized = _balance_parentheses(normalized)
    return _add_implicit_multiplication(normalized)


# ---------------------------------------------------------------------------
# Funções disponíveis (lista branca)
# ---------------------------------------------------------------------------
def _guarded(name: str, function: Callable[..., Any], minimum: int = 1, maximum: int = 2):
    """Envolve uma função de ``math`` para devolver erros amigáveis."""

    def wrapper(*args: float) -> Any:
        if not minimum <= len(args) <= maximum:
            esperado = str(minimum) if minimum == maximum else f"{minimum} ou {maximum}"
            raise CalculatorError(
                f"{name}() espera {esperado} argumento(s), mas recebeu {len(args)}."
            )
        try:
            return function(*args)
        except ZeroDivisionError as exc:
            raise CalculatorError("Divisão por zero.") from exc
        except ValueError as exc:
            raise CalculatorError(f"Valor inválido para {name}(): {exc}") from exc
        except OverflowError as exc:
            raise CalculatorError(f"O resultado de {name}() é grande demais.") from exc

    wrapper.__name__ = name
    return wrapper


def _factorial(number: float) -> int:
    if number < 0:
        raise CalculatorError("fatorial não existe para números negativos.")
    if number != int(number):
        raise CalculatorError("fatorial só aceita números inteiros.")
    if number > MAX_FACTORIAL:
        raise CalculatorError(f"fatorial aceita no máximo {MAX_FACTORIAL}.")
    return math.factorial(int(number))


def _cbrt(number: float) -> float:
    """Raiz cúbica que também funciona para números negativos."""
    return math.copysign(abs(number) ** (1 / 3), number)


def _lcm(first: float, second: float) -> int:
    """Mínimo múltiplo comum (compatível com Python 3.8, sem math.lcm)."""
    a, b = int(first), int(second)
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // math.gcd(a, b)


def _round(number: float, digits: float = 0) -> float:
    return round(number, int(digits))


def build_namespace(angle: str = "rad") -> dict[str, Any]:
    """Monta o dicionário de constantes e funções visíveis na expressão."""
    angle = (angle or "rad").lower()
    if angle not in {"deg", "rad"}:
        raise CalculatorError("Modo de ângulo inválido: use 'deg' ou 'rad'.")
    to_radians = math.radians if angle == "deg" else (lambda value: value)
    from_radians = math.degrees if angle == "deg" else (lambda value: value)

    namespace: dict[str, Any] = {
        "pi": math.pi,
        "e": math.e,
        "tau": math.tau,
        "phi": (1 + 5 ** 0.5) / 2,
        "inf": math.inf,
        # aritmética
        "abs": _guarded("abs", abs),
        "round": _guarded("round", _round),
        "floor": _guarded("floor", math.floor),
        "ceil": _guarded("ceil", math.ceil),
        "sqrt": _guarded("sqrt", math.sqrt),
        "cbrt": _guarded("cbrt", _cbrt),
        "exp": _guarded("exp", math.exp),
        "ln": _guarded("ln", math.log),
        "log": _guarded("log", lambda value, base=10: math.log(value, base)),
        "log2": _guarded("log2", math.log2),
        "log10": _guarded("log10", math.log10),
        "hypot": _guarded("hypot", math.hypot, 1),
        "gcd": _guarded("gcd", lambda a, b: math.gcd(int(a), int(b))),
        "lcm": _guarded("lcm", _lcm),
        "factorial": _guarded("factorial", _factorial),
        # trigonometria (respeita o modo de ângulo)
        "sin": _guarded("sin", lambda x: math.sin(to_radians(x))),
        "cos": _guarded("cos", lambda x: math.cos(to_radians(x))),
        "tan": _guarded("tan", lambda x: math.tan(to_radians(x))),
        "asin": _guarded("asin", lambda x: from_radians(math.asin(x))),
        "acos": _guarded("acos", lambda x: from_radians(math.acos(x))),
        "atan": _guarded("atan", lambda x: from_radians(math.atan(x))),
        "sinh": _guarded("sinh", math.sinh),
        "cosh": _guarded("cosh", math.cosh),
        "tanh": _guarded("tanh", math.tanh),
    }

    class _Constant(float):
        """Constante que aceita ser chamada como função: ``e(2)`` = ``e*2``."""

        def __call__(self, *values):  # pragma: no cover - conveniência
            result = float(self)
            for value in values:
                result *= value
            return result

    for name in ("pi", "e", "tau", "phi"):
        namespace[name] = _Constant(namespace[name])

    return namespace


# ---------------------------------------------------------------------------
# Avaliação (percurso da árvore sintática)
# ---------------------------------------------------------------------------
def _power(base: float, exponent: float) -> Any:
    if isinstance(exponent, (int, float)) and abs(exponent) > MAX_EXPONENT:
        raise CalculatorError(f"expoente muito grande (máximo {MAX_EXPONENT}).")
    result = base ** exponent
    if isinstance(result, complex):
        raise CalculatorError(
            "o resultado não é um número real (raiz de número negativo)."
        )
    if isinstance(result, int) and result.bit_length() > 100_000:
        raise CalculatorError("o resultado é grande demais para ser calculado.")
    return result


_BINARY_OPS: dict[type, Callable[[Any, Any], Any]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: _power,
}

_COMPARISONS: dict[type, Callable[[Any, Any], bool]] = {
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
}

_UNARY_OPS: dict[type, Callable[[Any], Any]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class _Evaluator:
    """Percorre a árvore sintática avaliando somente os nós permitidos."""

    def __init__(self, namespace: dict[str, Any]) -> None:
        self.namespace = namespace

    def visit(self, node: ast.AST) -> Any:
        method = getattr(self, f"visit_{type(node).__name__}", None)
        if method is None:
            raise CalculatorError(
                f"não sei calcular '{type(node).__name__}' nesta expressão."
            )
        return method(node)

    def visit_Expression(self, node: ast.Expression) -> Any:
        return self.visit(node.body)

    def visit_Constant(self, node: ast.Constant) -> Any:
        if isinstance(node.value, bool) or not isinstance(node.value, (int, float)):
            raise CalculatorError("apenas números são permitidos.")
        return node.value

    def visit_Name(self, node: ast.Name) -> Any:
        if node.id not in self.namespace:
            raise CalculatorError(f"nome desconhecido: '{node.id}'.")
        return self.namespace[node.id]

    def visit_BinOp(self, node: ast.BinOp) -> Any:
        operation = _BINARY_OPS.get(type(node.op))
        if operation is None:
            raise CalculatorError("operador não permitido.")
        left = self.visit(node.left)
        right = self.visit(node.right)
        try:
            return operation(left, right)
        except ZeroDivisionError as exc:
            if isinstance(node.op, (ast.Mod, ast.FloorDiv, ast.Div)):
                raise CalculatorError("divisão por zero.") from exc
            raise CalculatorError("operação inválida.") from exc
        except OverflowError as exc:
            raise CalculatorError("o resultado é grande demais.") from exc

    def visit_UnaryOp(self, node: ast.UnaryOp) -> Any:
        operation = _UNARY_OPS.get(type(node.op))
        if operation is None:
            raise CalculatorError("operador unário não permitido.")
        return operation(self.visit(node.operand))

    def visit_Call(self, node: ast.Call) -> Any:
        if not isinstance(node.func, ast.Name):
            raise CalculatorError("chamada de função inválida.")
        function = self.namespace.get(node.func.id)
        if function is None or not callable(function):
            raise CalculatorError(f"função desconhecida: '{node.func.id}'.")
        if node.keywords:
            raise CalculatorError("argumentos nomeados não são aceitos.")
        return function(*[self.visit(argument) for argument in node.args])

    def visit_Compare(self, node: ast.Compare) -> Any:
        left = self.visit(node.left)
        for op, comparator in zip(node.ops, node.comparators):
            operation = _COMPARISONS.get(type(op))
            if operation is None:
                raise CalculatorError("comparação não permitida.")
            right = self.visit(comparator)
            if not operation(left, right):
                return False
            left = right
        return True


# ---------------------------------------------------------------------------
# Formatação
# ---------------------------------------------------------------------------
def format_number(value: Any) -> str:
    """Formata o número para exibição, sem ruído de ponto flutuante."""
    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, complex):
        raise CalculatorError("o resultado não é um número real.")
    if isinstance(value, int):
        return str(value)
    if not isinstance(value, float):
        raise CalculatorError("o resultado não é um número.")

    if math.isnan(value):
        raise CalculatorError("o resultado não é um número (indefinido).")
    if math.isinf(value):
        raise CalculatorError("o resultado é grande demais para ser representado.")

    if value == int(value) and abs(value) < 1e16:
        return str(int(value))

    text = f"{value:.12g}"
    return text


_SYNTAX_MESSAGES = [
    ("unexpected eof", "faltam termos na expressão"),
    ("was never closed", "parêntese não fechado"),
    ("invalid decimal literal", "número escrito de forma inválida"),
    ("invalid syntax", "não entendi a expressão"),
    ("unmatched", "parêntese sem par"),
    ("cannot assign", "a expressão não pode conter '='"),
    ("leading zeros", "números não podem começar com zero"),
]


def _translate_syntax_error(error: SyntaxError) -> str:
    """Traduz a mensagem do Python para algo que o usuário entenda."""
    original = (error.msg or "").lower()
    for fragment, translation in _SYNTAX_MESSAGES:
        if fragment in original:
            return translation
    return original or "sintaxe inválida"


# ---------------------------------------------------------------------------
# API principal
# ---------------------------------------------------------------------------
def evaluate(expression: str, angle: str = "rad") -> Result:
    """Avalia ``expression`` e devolve um :class:`Result`.

    Levanta :class:`CalculatorError` quando a expressão é inválida.
    """
    if expression is None or not str(expression).strip():
        raise CalculatorError("Digite uma expressão para calcular.")

    expression = str(expression)
    if len(expression) > MAX_LENGTH:
        raise CalculatorError(
            f"Expressão muito longa (máximo de {MAX_LENGTH} caracteres)."
        )

    normalized = normalize(expression)
    try:
        tree = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError(f"expressão inválida: {_translate_syntax_error(exc)}.") from exc

    if sum(1 for _ in ast.walk(tree)) > MAX_TREE_NODES:
        raise CalculatorError("expressão complexa demais.")

    evaluator = _Evaluator(build_namespace(angle))
    value = evaluator.visit(tree.body)

    return Result(
        expression=expression.strip(),
        normalized=normalized,
        value=value,
        text=format_number(value),
        angle="deg" if (angle or "rad").lower() == "deg" else "rad",
    )


# ---------------------------------------------------------------------------
# Linha de comando
# ---------------------------------------------------------------------------
_HELP = """
Calculadora Python - modo interativo
  digite uma expressão, por exemplo:  (2+3)*4  |  sqrt(2)  |  2^10
  :deg / :rad ............ alterna entre graus e radianos
  :ajuda ................. mostra esta ajuda
  sair ................... encerra
"""


def main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    angle = "rad"
    if arguments and arguments[0] in {"-d", "--deg", "--graus"}:
        angle = "deg"
        arguments.pop(0)

    if arguments:
        expression = " ".join(arguments)
        try:
            result = evaluate(expression, angle=angle)
        except CalculatorError as error:
            print(f"Erro: {error}", file=sys.stderr)
            return 1
        print(result.text)
        return 0

    print(f"Modo interativo ({angle}). Digite ':ajuda' para ver os comandos.")
    while True:
        try:
            line = input("calc> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if not line:
            continue
        if line.lower() in {"sair", "exit", "quit", "q"}:
            return 0
        if line in {":ajuda", ":help", ":h"}:
            print(_HELP.strip())
            continue
        if line in {":deg", ":graus"}:
            angle = "deg"
            print("modo: graus")
            continue
        if line in {":rad", ":radianos"}:
            angle = "rad"
            print("modo: radianos")
            continue
        try:
            result = evaluate(line, angle=angle)
        except CalculatorError as error:
            print(f"Erro: {error}", file=sys.stderr)
        else:
            print(f"= {result.text}")


if __name__ == "__main__":
    raise SystemExit(main())
