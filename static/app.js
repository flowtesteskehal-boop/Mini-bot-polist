/* ==========================================================================
   Calculadora Python + HTML — interface
   A interface NÃO calcula nada: toda expressão é enviada para o back-end
   Python (POST /api/calculate) e o resultado vem de lá.
   ========================================================================== */

(() => {
  "use strict";

  const API = "/api/calculate";
  const STORAGE = { history: "calculadora:historico", angle: "calculadora:angulo" };
  const MAX_HISTORY = 40;
  const PREVIEW_DELAY = 260;

  // Tokens que devem ser apagados por inteiro no botão ⌫
  const MULTI_CHAR_TOKENS = [
    "factorial(", "10**", "sqrt(", "cbrt(", "floor(", "ceil(", "round(", "hypot(",
    "log10(", "log2(", "sinh(", "cosh(", "tanh(", "asin(", "acos(", "atan(",
    "log(", "abs(", "exp(", "gcd(", "lcm(", "sin(", "cos(", "tan(", "ln(",
    "**2", "**",
  ].sort((a, b) => b.length - a.length);

  const elements = {
    display: document.getElementById("display"),
    expression: document.getElementById("expression"),
    result: document.getElementById("result"),
    status: document.getElementById("status"),
    scientific: document.getElementById("scientific"),
    toggleScientific: document.getElementById("toggle-scientific"),
    copy: document.getElementById("copy"),
    engine: document.getElementById("engine"),
    historyList: document.getElementById("history-list"),
    historyEmpty: document.getElementById("history-empty"),
    clearHistory: document.getElementById("clear-history"),
    angleButtons: [...document.querySelectorAll("[data-angle]")],
  };

  const state = {
    expression: "",
    angle: "rad",
    lastResult: "0",
    pinned: false,      // true quando o valor exibido veio de uma tecla "="
    history: [],
    requestId: 0,
    previewTimer: null,
  };

  /* ------------------------------------------------------------ utilidades */
  const read = (key, fallback) => {
    try {
      const value = localStorage.getItem(key);
      return value === null ? fallback : JSON.parse(value);
    } catch { return fallback; }
  };

  const write = (key, value) => {
    try { localStorage.setItem(key, JSON.stringify(value)); } catch { /* modo privado */ }
  };

  function setStatus(text, kind = "") {
    elements.status.textContent = text;
    elements.status.className = "display__status" + (kind ? ` is-${kind}` : "");
  }

  function setResult(text, { preview = false, error = false } = {}) {
    elements.result.textContent = text;
    elements.result.className = "display__result"
      + (preview ? " is-preview" : "")
      + (error ? " is-error" : "");
  }

  function renderExpression() {
    elements.expression.textContent = state.expression;
  }

  function shake() {
    elements.display.classList.remove("is-shaking");
    void elements.display.offsetWidth;   // reinicia a animação
    elements.display.classList.add("is-shaking");
  }

  /* ------------------------------------------------------------ back-end -- */
  async function calculate(expression, { silent = false } = {}) {
    const id = ++state.requestId;
    let response;
    try {
      response = await fetch(API, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ expression, angle: state.angle }),
      });
    } catch {
      if (id === state.requestId && !silent) {
        setStatus("servidor Python offline — inicie com: python3 server.py", "error");
      }
      return null;
    }

    let data;
    try {
      data = await response.json();
    } catch {
      data = { ok: false, error: "resposta inválida do servidor." };
    }
    if (id !== state.requestId) return null;   // descarta respostas antigas
    return data;
  }

  /* ------------------------------------------------------------- ações ---- */
  const CONTINUATION = /^(\*\*|[-+*/%^])/;   // tokens que continuam a conta

  function insert(token) {
    // depois de "=": operador continua a partir do resultado, o resto começa novo
    if (state.pinned) {
      state.expression = CONTINUATION.test(token) ? state.lastResult : "";
      state.pinned = false;
    }

    // evita pontos decimais repetidos no mesmo número ("1.2." é erro)
    if (token === ".") {
      const tail = state.expression.match(/[\d.]*$/)[0];
      if (tail.includes(".")) return;
      if (!tail) {
        const last = state.expression.slice(-1);
        if (last === ")" || /[a-zA-Z]$/.test(last)) state.expression += "*";
        state.expression += "0";
      }
    }
    if (token === "(" && /[\d)]$/.test(state.expression.slice(-1))) token = "*(";

    state.expression += token;
    renderExpression();
    schedulePreview();
  }

  function backspace() {
    if (state.pinned) { clearAll(); return; }
    const token = MULTI_CHAR_TOKENS.find((candidate) => state.expression.endsWith(candidate));
    state.expression = token
      ? state.expression.slice(0, -token.length)
      : state.expression.slice(0, -1);
    renderExpression();
    schedulePreview();
  }

  function clearAll() {
    state.expression = "";
    state.pinned = false;
    state.requestId += 1;              // cancela respostas em voo
    renderExpression();
    setResult("0");
    setStatus("");
  }

  function toggleSign() {
    const expression = state.expression.trim();
    if (!expression) return;
    state.pinned = false;
    // troca o sinal da expressão inteira: 2+3  ->  -(2+3)  ->  2+3
    const wrapped = expression.match(/^-\((.*)\)$/s);
    state.expression = wrapped ? wrapped[1] : `-(${expression})`;
    renderExpression();
    schedulePreview();
  }

  function schedulePreview() {
    clearTimeout(state.previewTimer);
    if (state.pinned) return;

    if (!state.expression.trim()) {
      setResult("0");
      setStatus("");
      return;
    }

    setStatus("calculando…");
    state.previewTimer = setTimeout(async () => {
      const data = await calculate(state.expression, { silent: true });
      if (!data) return;
      if (data.ok) {
        setResult(data.result, { preview: true });
        setStatus("pré-visualização ao vivo", "ok");
      } else {
        setStatus("", "");   // enquanto digita, erros de sintaxe são normais
      }
    }, PREVIEW_DELAY);
  }

  async function equals() {
    clearTimeout(state.previewTimer);
    const expression = state.expression.trim();
    if (!expression) return;

    const data = await calculate(expression);
    if (!data) return;

    if (!data.ok) {
      setResult(data.error, { error: true });
      setStatus("erro", "error");
      shake();
      return;
    }

    state.pinned = true;
    state.lastResult = data.result;
    setResult(data.result);
    setStatus(`= calculado no Python${data.normalized && data.normalized !== expression ? ` · ${data.normalized}` : ""}`, "ok");
    pushHistory({ expression, result: data.result });
  }

  /* ------------------------------------------------------------ histórico - */
  function pushHistory(entry) {
    const duplicate = state.history.find(
      (item) => item.expression === entry.expression && item.result === entry.result
    );
    if (duplicate) {
      state.history = state.history.filter((item) => item !== duplicate);
    }
    state.history.unshift({ ...entry, at: Date.now() });
    state.history = state.history.slice(0, MAX_HISTORY);
    write(STORAGE.history, state.history);
    renderHistory();
  }

  function renderHistory() {
    elements.historyList.replaceChildren();
    elements.historyEmpty.hidden = state.history.length > 0;

    state.history.forEach((entry) => {
      const item = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "history__item";
      button.title = `Usar ${entry.expression}`;

      const expression = document.createElement("span");
      expression.className = "history__item-expression";
      expression.textContent = entry.expression;

      const result = document.createElement("span");
      result.className = "history__item-result";
      result.textContent = `= ${entry.result}`;

      button.append(expression, result);
      button.addEventListener("click", () => {
        state.expression = entry.expression;
        state.pinned = false;
        renderExpression();
        setResult(entry.result);
        setStatus("expressão do histórico", "ok");
        schedulePreview();
      });

      item.append(button);
      elements.historyList.append(item);
    });
  }

  /* -------------------------------------------------------------- eventos - */
  document.querySelectorAll(".key").forEach((key) => {
    key.addEventListener("click", () => {
      const action = key.dataset.action;
      if (action === "clear") return clearAll();
      if (action === "backspace") return backspace();
      if (action === "equals") return equals();
      if (action === "sign") return toggleSign();
      if (key.dataset.insert !== undefined) return insert(key.dataset.insert);
    });
  });

  elements.toggleScientific.addEventListener("click", () => {
    const open = elements.scientific.hidden;
    elements.scientific.hidden = !open;
    elements.toggleScientific.classList.toggle("is-active", open);
    elements.toggleScientific.setAttribute("aria-expanded", String(open));
  });

  elements.angleButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.angle = button.dataset.angle;
      elements.angleButtons.forEach((other) => {
        const active = other === button;
        other.classList.toggle("is-active", active);
        other.setAttribute("aria-pressed", String(active));
      });
      write(STORAGE.angle, state.angle);
      setStatus(state.angle === "deg" ? "ângulos em graus" : "ângulos em radianos");
      if (state.expression.trim()) schedulePreview();
    });
  });

  elements.copy.addEventListener("click", async () => {
    const text = elements.result.textContent;
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        // alternativa para contextos sem clipboard API
        const helper = document.createElement("textarea");
        helper.value = text;
        helper.setAttribute("readonly", "");
        helper.style.position = "fixed";
        helper.style.opacity = "0";
        document.body.append(helper);
        helper.select();
        document.execCommand("copy");
        helper.remove();
      }
      setStatus("resultado copiado!", "ok");
    } catch {
      setStatus("não foi possível copiar", "error");
    }
  });

  elements.clearHistory.addEventListener("click", () => {
    state.history = [];
    write(STORAGE.history, state.history);
    renderHistory();
    setStatus("histórico limpo");
  });

  // teclado físico
  document.addEventListener("keydown", (event) => {
    if (event.ctrlKey || event.metaKey || event.altKey) return;
    const { key } = event;

    if (/^[0-9]$/.test(key)) { event.preventDefault(); return insert(key); }
    if (key === "." || key === ",") { event.preventDefault(); return insert("."); }
    if (["+", "-", "*", "/", "(", ")", "^", "%"].includes(key)) {
      event.preventDefault();
      return insert(key === "^" ? "**" : key);
    }
    if (key === "Enter" || key === "=") { event.preventDefault(); return equals(); }
    if (key === "Backspace") { event.preventDefault(); return backspace(); }
    if (key === "Delete" || key === "Escape") { event.preventDefault(); return clearAll(); }
  });

  /* --------------------------------------------------------------- início - */
  async function boot() {
    state.angle = read(STORAGE.angle, "rad") === "deg" ? "deg" : "rad";
    state.history = Array.isArray(read(STORAGE.history, [])) ? read(STORAGE.history, []) : [];
    elements.angleButtons.forEach((button) => {
      const active = button.dataset.angle === state.angle;
      button.classList.toggle("is-active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    renderHistory();
    renderExpression();
    setResult("0");
    setStatus("");

    try {
      const response = await fetch("/api/health");
      const health = await response.json();
      elements.engine.textContent = `Cálculos executados no Python ${health.python} — servidor ${health.status}`;
    } catch {
      elements.engine.textContent = "Servidor Python offline — rode: python3 server.py";
      setStatus("servidor offline", "error");
    }
  }

  boot();
})();
