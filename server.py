"""Servidor web da calculadora (apenas biblioteca padrão do Python).

Serve a interface em HTML/CSS/JavaScript e expõe a API que faz os cálculos
no back-end Python:

    GET  /                  -> index.html
    GET  /static/<arquivo>  -> CSS, JavaScript
    GET  /api/health        -> status do servidor
    POST /api/calculate     -> {"expression": "2+2", "angle": "rad"}

Execução::

    python3 server.py                 # http://localhost:8000
    python3 server.py --port 8080
    PORT=9000 python3 server.py
"""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import calculator

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MAX_BODY_BYTES = 64 * 1024
DEFAULT_PORT = int(os.environ.get("PORT", 8000))

mimetypes.add_type("application/javascript", ".js")
mimetypes.add_type("text/css", ".css")
mimetypes.add_type("image/svg+xml", ".svg")


class CalculatorHandler(BaseHTTPRequestHandler):
    """Manipula as requisições HTTP da calculadora."""

    server_version = "CalculadoraPython"
    protocol_version = "HTTP/1.1"

    # ------------------------------------------------------------------ infra
    def log_message(self, format: str, *args) -> None:  # noqa: A002
        sys.stderr.write(
            f"[{self.log_date_time_string()}] {self.address_string()} "
            f"{format % args}\n"
        )

    def _send(self, status: int, body: bytes, content_type: str, extra: dict | None = None) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        for key, value in (extra or {}).items():
            self.send_header(key, value)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _send_error_json(self, status: int, message: str) -> None:
        self._send_json(status, {"ok": False, "error": message})

    def _read_json_body(self) -> dict:
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError as exc:
            raise ValueError("Cabeçalho Content-Length inválido.") from exc
        if length <= 0:
            raise ValueError("Corpo da requisição vazio.")
        if length > MAX_BODY_BYTES:
            raise ValueError("Corpo da requisição muito grande.")
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("JSON inválido.") from exc
        if not isinstance(payload, dict):
            raise ValueError("O corpo deve ser um objeto JSON.")
        return payload

    # ----------------------------------------------------------------- rotas
    def do_GET(self) -> None:  # noqa: N802
        path = unquote(urlparse(self.path).path)

        if path in {"/", "/index.html"}:
            return self._serve_file(BASE_DIR / "index.html")
        if path == "/api/health":
            return self._send_json(
                HTTPStatus.OK,
                {
                    "ok": True,
                    "status": "online",
                    "service": "Calculadora Python",
                    "python": sys.version.split()[0],
                    "angle_options": ["rad", "deg"],
                },
            )
        if path.startswith("/static/"):
            return self._serve_file(STATIC_DIR / path[len("/static/"):])
        if path == "/favicon.ico":
            return self._send(HTTPStatus.NO_CONTENT, b"", "image/x-icon")

        return self._send_error_json(HTTPStatus.NOT_FOUND, "Página não encontrada.")

    def do_HEAD(self) -> None:  # noqa: N802
        self.do_GET()

    def do_POST(self) -> None:  # noqa: N802
        path = unquote(urlparse(self.path).path)
        if path != "/api/calculate":
            return self._send_error_json(
                HTTPStatus.NOT_FOUND, "Rota não encontrada."
            )

        try:
            payload = self._read_json_body()
        except ValueError as error:
            return self._send_error_json(HTTPStatus.BAD_REQUEST, str(error))

        expression = payload.get("expression", "")
        angle = payload.get("angle", "rad")
        if not isinstance(expression, str):
            return self._send_error_json(
                HTTPStatus.BAD_REQUEST, "O campo 'expression' deve ser texto."
            )
        if not isinstance(angle, str):
            angle = "rad"

        try:
            result = calculator.evaluate(expression, angle=angle)
        except calculator.CalculatorError as error:
            return self._send_json(
                HTTPStatus.BAD_REQUEST,
                {"ok": False, "error": str(error), "expression": expression.strip()},
            )
        except Exception as error:  # pragma: no cover - rede de segurança
            self.log_error("erro inesperado: %r", error)
            return self._send_error_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "Erro interno ao calcular. Tente novamente.",
            )

        return self._send_json(HTTPStatus.OK, result.as_dict())

    # ------------------------------------------------------------ arquivos
    @staticmethod
    def _is_inside(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent)
        except ValueError:
            return False
        return True

    def _serve_file(self, path: Path) -> None:
        try:
            resolved = path.resolve()
        except OSError:
            return self._send_error_json(HTTPStatus.NOT_FOUND, "Arquivo não encontrado.")

        # impede acesso fora das pastas do projeto (../ etc.)
        if not any(
            self._is_inside(resolved, allowed)
            for allowed in (BASE_DIR, STATIC_DIR)
            if allowed.exists()
        ) or not resolved.is_file():
            return self._send_error_json(HTTPStatus.NOT_FOUND, "Arquivo não encontrado.")

        content_type, _ = mimetypes.guess_type(resolved.name)
        if resolved.suffix == ".html":
            content_type = "text/html"
        body = resolved.read_bytes()
        self._send(
            HTTPStatus.OK,
            body,
            f"{content_type or 'application/octet-stream'}; charset=utf-8",
        )


def run(host: str = "0.0.0.0", port: int = DEFAULT_PORT) -> None:
    httpd = ThreadingHTTPServer((host, port), CalculatorHandler)
    httpd.daemon_threads = True
    print("=" * 58)
    print("  Calculadora Python (HTML + CSS + JavaScript)")
    print(f"  Interface .....: http://localhost:{port}")
    print(f"  API ...........: POST http://localhost:{port}/api/calculate")
    print(f"  Python ........: {sys.version.split()[0]} | Ctrl+C para parar")
    print("=" * 58)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
    finally:
        httpd.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Servidor da calculadora web.")
    parser.add_argument("--host", default="0.0.0.0", help="endereço de escuta")
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help="porta (padrão: 8000)"
    )
    args = parser.parse_args(argv)
    run(args.host, args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
