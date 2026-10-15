# 🤖 Mini Bot Poli — Aprenda `if/else` se divertindo!

Um mini bot em **Python puro** (sem instalar nada!) que ajuda você a praticar
**lógica de programação** e declarações **`if` / `elif` / `else`** de um jeito
leve e divertido.

> 💡 O segredo do Poli: ele **não usa IA de verdade** — por dentro, ele é feito
> só de `if/elif/else` comparando palavras! Ou seja, o próprio bot é o exercício.

## ▶️ Como rodar

Precisa apenas de Python 3.8 ou mais novo:

```bash
python bot.py           # bot interativo (menu completo)
python bot.py --demo    # demonstração automática, sem digitar nada
python bot.py --quiz    # vai direto para o quiz
```

## 🎮 O que dá para fazer

| Modo | O que é |
|---|---|
| 💬 **Conversar** | Pergunte *"o que é if?"*, *"e o elif?"*, peça uma *"piada"* ou uma *"dica"* |
| 🎯 **Quiz relâmpago** | 8 perguntas do tipo "o que esse código imprime?" com explicação da resposta |
| 🧩 **Desafio** | Complete a condição que falta no `if` (ex.: `if ______:`) |
| 📚 **Explicação express** | Resumos rápidos: `if`, `elif`, `else`, operadores e if aninhado |
| 🔢 **Adivinhe o número** | Jogo bônus de quente/frio que treina comparações (+20 pontos!) |

Você ganha **pontos** a cada acerto e recebe um **nível** ao sair:
🌱 Iniciante → 🥈 Aprendiz → 🏆 Mestre do if/else.

### Exemplos para testar no modo conversa
```
o que é if?            como você funciona?
o que é elif?          me conta uma piada
o que é else?          uma dica, por favor
operadores             ajuda
```

## 📁 Estrutura do projeto

```
Mini-bot-polist/
├── bot.py                  # Programa principal: menu e modos de jogo
├── mini_bot/
│   ├── cerebro.py          # As respostas do chat (uma escadinha de if/elif/else!)
│   └── quiz.py             # Perguntas, desafios e explicações
└── tests/
    └── test_bot.py         # Testes automáticos
```

## 🧪 Rodar os testes

```bash
python -m unittest discover tests -v    # sem instalar nada
# ou, se tiver pytest:  python -m pytest tests/ -q
```

## 🚀 Ideias para praticar (evolua o Poli!)

1. Adicione uma nova pergunta em `mini_bot/quiz.py`
2. Crie uma nova resposta no `cerebro.py` (ex.: detectar a palavra `"python"`)
3. Faça o quiz ter 5 rodadas em vez de 3
4. Adicione um placar que salva os pontos num arquivo `placar.txt`

Feito para aprender programando — divirta-se! 🎉
