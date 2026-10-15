# 🧮 Calculadora Python + HTML

Calculadora web completa: **interface em HTML, CSS e JavaScript** e **cálculos feitos
no Python** (back-end), além de um **modo de linha de comando**.

O front-end não calcula nada sozinho — ele envia cada expressão para a API Python,
que avalia com segurança (sem `eval`), devolve o resultado e a interface exibe.
Assim a mesma lógica é usada no navegador e no terminal.

```
Mini-bot-polist/
├── index.html            # interface (HTML)
├── static/
│   ├── style.css         # aparência (CSS)
│   └── app.js            # interação + chamadas à API (JavaScript)
├── server.py             # servidor HTTP e API REST (Python puro, sem dependências)
├── calculator.py         # motor de cálculo (AST, sem eval)
├── cli.py                # calculadora de terminal
├── test_calculator.py    # 44 testes automatizados
└── README.md
```

---

## 🚀 Como executar

Requisito: **Python 3.8+** (nenhuma biblioteca externa — só a biblioteca padrão).

### 1. Interface web

```bash
python3 server.py
```

Abra **http://localhost:8000** no navegador.

Para usar outra porta:

```bash
python3 server.py --port 8080
# ou
PORT=8080 python3 server.py
```

### 2. Linha de comando

```bash
python3 cli.py "2+2*3"              # 14
python3 cli.py --deg "sin(30)"      # 0.5
python3 cli.py --tabela "5!" "1/7"  # mostra em colunas
python3 cli.py                      # modo interativo (REPL)
echo "2^16" | python3 cli.py -      # lê da entrada padrão
```

### 3. Motor de cálculo direto no Python

```python
from calculator import evaluate

evaluate("2+3*4").text          # '14'
evaluate("2^10").text           # '1024'
evaluate("sin(30)", angle="deg").text   # '0.5'
evaluate("2+2").as_dict()       # {'ok': True, 'result': '4', ...}
```

---

## ✨ Recursos

**Interface**
- Teclado virtual com botões, suporte a **teclado físico** (números, operadores,
  `Enter` = calcular, `Backspace` = apagar, `Esc` = limpar).
- **Pré-visualização ao vivo**: mostra o resultado enquanto você digita.
- Painel de **funções científicas** (π, e, potência, raiz, log, trigonometria, fatorial…).
- Alternância **RAD / DEG** para ângulos.
- **Histórico** persistente (salvo no navegador) — clique em qualquer conta para reusá-la.
- Botão para copiar o resultado, layout responsivo e acessível (ARIA, foco visível,
  `prefers-reduced-motion`).

**Motor de cálculo**
- `+ - * / // % **`, parênteses e precedência correta.
- `^` tratado como potência (`2^10` = 1024) e símbolos como `×`, `÷`, `√`, `π`, `−`.
- Multiplicação implícita: `2(3+4)`, `(1+2)(3+4)`, `2pi`.
- Fatorial pós-fixado: `5!`, `6!/3!`.
- Parênteses fechados automaticamente: `sqrt(9` funciona.
- Funções: `sqrt`, `cbrt`, `abs`, `round`, `floor`, `ceil`, `ln`, `log(x, base)`,
  `log2`, `log10`, `exp`, `hypot`, `gcd`, `lcm`, `factorial`,
  `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`.
- Constantes: `pi`, `e`, `tau`, `phi`.
- **Segurança**: a expressão é convertida em árvore sintática (`ast`) e somente nós
  e funções da lista branca são avaliados — `__import__('os')` ou `x = 1` são recusados.
  Há limites de tamanho da expressão, de expoente (`|x| ≤ 1000`) e de fatorial (`≤ 1000`).
- Números gigantes com precisão exata de inteiros (`2^64` = 18446744073709551616).

---

## 🔌 API

O servidor expõe duas rotas (JSON):

**`POST /api/calculate`**

```bash
curl -X POST http://localhost:8000/api/calculate \
     -H "Content-Type: application/json" \
     -d '{"expression": "sqrt(144) + 2^5", "angle": "rad"}'
```

```json
{
  "ok": true,
  "expression": "sqrt(144) + 2^5",
  "normalized": "sqrt(144) + 2**5",
  "value": 44.0,
  "result": "44",
  "angle": "rad"
}
```

Em caso de erro, responde HTTP 400:

```json
{ "ok": false, "error": "divisão por zero.", "expression": "1/0" }
```

**`GET /api/health`**

```json
{ "ok": true, "status": "online", "service": "Calculadora Python", "python": "3.11.2" }
```

---

## 🧪 Testes

```bash
python3 -m unittest -v
```

44 testes cobrindo aritmética, precedência, normalização, funções matemáticas,
trigonometria RAD/DEG, formatação de números e tentativas de injeção de código.

---

## 📐 Exemplos de uso

| Expressão | Resultado | Observação |
|---|---|---|
| `2+3*4` | `14` | precedência |
| `(2+5)^2` | `49` | `^` vira potência |
| `7/2` | `3.5` | divisão real |
| `7//2` | `3` | divisão inteira |
| `7%3` | `1` | resto |
| `1/7` | `0.142857142857` | 12 dígitos significativos |
| `0.1+0.2` | `0.3` | sem ruído de ponto flutuante |
| `2^64` | `18446744073709551616` | inteiro exato |
| `2pi` | `6.28318530718` | multiplicação implícita |
| `sqrt(9` | `3` | parêntese automático |
| `5!` | `120` | fatorial |
| `sin(30)` com DEG | `0.5` | modo graus |
| `log(8, 2)` | `3` | log na base 2 |
| `hypot(3, 4)` | `5` | hipotenusa |
| `1/0` | erro | *divisão por zero* |
| `sqrt(-1)` | erro | *o resultado não é um número real* |

---

## ⚠️ Observações técnicas

- **Sem dependências externas**: nada de Flask ou Django — `server.py` usa
  `http.server` da biblioteca padrão, então funciona em qualquer instalação de Python.
- **`protocol_version = HTTP/1.1`** com `Content-Length` em todas as respostas
  (keep-alive correto e compatível com proxies).
- O servidor escuta em `0.0.0.0` e é multithread (`ThreadingHTTPServer`).
- O acesso a arquivos é restrito à pasta do projeto (`/static/../../etc/passwd` → 404).
- **Para produção**: use um servidor WSGI/ASGI (Gunicorn, uWSGI, Nginx) na frente ou
  exponha a lógica de `calculator.py` via Flask/FastAPI — a API é a mesma.
