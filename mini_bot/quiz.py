"""
quiz.py — Perguntas e desafios de if/else 🎯

Cada pergunta mostra um trechinho de código e você precisa prever
o que ele imprime. É o melhor treino de lógica que existe!
"""

import random

# ---------------------------------------------------------------------------
# QUIZ: "O que esse código imprime?"
# campos: codigo, opcoes, correta (índice da opção certa), explicacao
# ---------------------------------------------------------------------------
PERGUNTAS = [
    {
        "codigo": "x = 10\nif x > 5:\n    print('Grande')\nelse:\n    print('Pequeno')",
        "opcoes": ["Grande", "Pequeno", "Nada", "Erro"],
        "correta": 0,
        "explicacao": "10 > 5 é True, então o bloco do 'if' executa e o 'else' é ignorado.",
    },
    {
        "codigo": "nota = 4\nif nota >= 6:\n    print('Aprovado')\nelse:\n    print('Recuperação')",
        "opcoes": ["Aprovado", "Recuperação", "Nada", "Erro"],
        "correta": 1,
        "explicacao": "4 >= 6 é False, então caímos direto no 'else': Recuperação.",
    },
    {
        "codigo": "cor = 'azul'\nif cor == 'vermelho':\n    print('Pare')\nelif cor == 'azul':\n    print('Céu')\nelse:\n    print('Outra cor')",
        "opcoes": ["Pare", "Céu", "Outra cor", "Pare e Céu"],
        "correta": 1,
        "explicacao": "O 1º if é False, mas o elif acerta: cor == 'azul' é True. Só UM bloco roda!",
    },
    {
        "codigo": "idade = 20\nif idade < 18:\n    print('Menor')\nelif idade < 65:\n    print('Adulto')\nelse:\n    print('Idoso')",
        "opcoes": ["Menor", "Adulto", "Idoso", "Adulto e Idoso"],
        "correta": 1,
        "explicacao": "20 não é < 18, mas é < 65 → 'Adulto'. A escadinha para na 1ª condição True!",
    },
    {
        "codigo": "saldo = 0\nif saldo:\n    print('Tem dinheiro')\nelse:\n    print('Sem dinheiro')",
        "opcoes": ["Tem dinheiro", "Sem dinheiro", "Nada", "Erro"],
        "correta": 1,
        "explicacao": "Em Python, o número 0 é considerado False! Então o 'else' executa.",
    },
    {
        "codigo": "a = 5\nb = 5\nif a != b:\n    print('Diferentes')\nelse:\n    print('Iguais')",
        "opcoes": ["Diferentes", "Iguais", "Nada", "Erro"],
        "correta": 1,
        "explicacao": "'!=' significa 'diferente de'. Como 5 == 5, a condição é False → 'Iguais'.",
    },
    {
        "codigo": "chovendo = False\nif not chovendo:\n    print('Vamos passear')\nelse:\n    print('Ficar em casa')",
        "opcoes": ["Vamos passear", "Ficar em casa", "Nada", "Erro"],
        "correta": 0,
        "explicacao": "O 'not' inverte: not False = True. Dia livre para passear! ☀️",
    },
    {
        "codigo": "numero = 7\nif numero % 2 == 0:\n    print('Par')\nelse:\n    print('Ímpar')",
        "opcoes": ["Par", "Ímpar", "Nada", "Erro"],
        "correta": 1,
        "explicacao": "7 % 2 é o resto da divisão = 1, que não é 0. Logo, 7 é Ímpar.",
    },
]

# ---------------------------------------------------------------------------
# DESAFIOS: complete o código escolhendo a condição certa
# ---------------------------------------------------------------------------
DESAFIOS = [
    {
        "titulo": "Liberando a entrada da festa 🎉",
        "codigo": "idade = 19\nif ______:\n    print('Pode entrar!')\nelse:\n    print('Volte quando tiver 18!')",
        "objetivo": "Só entra quem tem 18 anos ou mais.",
        "opcoes": ["idade == 18", "idade >= 18", "idade < 18", "idade = 18"],
        "correta": 1,
        "explicacao": "'>= 18' aceita 18, 19, 20... Cuidado: '=' atribui, não compara!",
    },
    {
        "titulo": "Senha secreta 🔐",
        "codigo": "senha = 'python123'\nif ______:\n    print('Acesso liberado!')\nelse:\n    print('Senha errada!')",
        "objetivo": "Comparar se a senha é igual a 'python123'.",
        "opcoes": ["senha = 'python123'", "senha != 'python123'", "senha == 'python123'", "senha > 'python123'"],
        "correta": 2,
        "explicacao": "Para COMPARAR textos usamos '=='. Um '=' só guardaria o valor na variável.",
    },
    {
        "titulo": "Dia de praia 🏖️",
        "codigo": "sol = True\nferiado = False\nif ______:\n    print('Partiu praia!')\nelse:\n    print('Hoje não...')",
        "objetivo": "Só vai à praia se tiver sol OU for feriado.",
        "opcoes": ["sol and feriado", "sol or feriado", "not sol", "sol == feriado"],
        "correta": 1,
        "explicacao": "Com 'or', basta UM ser True. Tem sol (True), então... partiu praia! 🏖️",
    },
    {
        "titulo": "Desconto da loja 🛒",
        "codigo": "compra = 150\nif ______:\n    print('Ganhou 10% de desconto!')\nelse:\n    print('Sem desconto dessa vez.')",
        "objetivo": "Desconto apenas para compras ACIMA de 100.",
        "opcoes": ["compra >= 100", "compra == 100", "compra > 100", "compra < 100"],
        "correta": 2,
        "explicacao": "'Acima de 100' é estritamente maior: '> 100'. O 100 em si não ganha!",
    },
]

EXPLICACOES = {
    "1": ("🧱 IF — a base de tudo", "    if condicao:\n        # só roda se condicao for True\n\nExemplo:\n    if fome:\n        print('Comer! 🍕')"),
    "2": ("🪜 ELIF — a escadinha", "    if nota >= 9:\n        print('Excelente')\n    elif nota >= 6:   # só chega aqui se o if falhou\n        print('Aprovado')\n\nVocê pode ter quantos elif quiser!"),
    "3": ("🛟 ELSE — o plano B", "    else:\n        # roda quando TUDO acima deu False\n\nSem condição, sempre por último, só um por if."),
    "4": ("⚖️ Operadores", "== igual | != diferente | > maior | < menor\n>= maior ou igual | <= menor ou igual\nand = e (tudo True) | or = ou (um True basta) | not = inverte"),
    "5": ("🪆 IF aninhado — if dentro de if", "    if tem_ingresso:\n        if idade >= 18:\n            print('Pode ver o filme!')\n\nO if de dentro só é avaliado se o de fora for True!"),
}


def pergunta_aleatoria():
    return random.choice(PERGUNTAS)


def desafio_aleatorio():
    return random.choice(DESAFIOS)


def esta_correta(item: dict, indice_escolhido: int) -> bool:
    """Um if/else decidindo seu destino... como tudo na vida de programador."""
    if indice_escolhido == item["correta"]:
        return True
    else:
        return False
