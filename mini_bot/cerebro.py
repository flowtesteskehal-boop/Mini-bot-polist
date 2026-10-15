"""
cerebro.py — O "cérebro" do Poli 🧠

Repare: o Poli NÃO usa uma IA de verdade (nada de redes neurais!).
Ele decide o que responder usando apenas... if / elif / else!
Ou seja: o próprio bot é um exemplo vivo do que você está aprendendo. 😉
"""

import random

# Respostas usadas quando o Poli não entende a mensagem (o "else" final!)
RESPOSTAS_PADRAO = [
    "Hmm, ainda não sei responder isso... mas sei uma coisa: todo 'else' "
    "guarda uma surpresa! Digite 'ajuda' para ver o que eu sei fazer.",
    "Não entendi 🤔 Mas olha que legal: você acabou de cair no meu 'else'! "
    "É ele quem cuida de tudo que os 'if' não previram.",
    "Essa passou pelos meus 'if' todos e caiu no 'else'! "
    "Tente perguntar: 'o que é if?', 'me conta uma piada' ou digite 'ajuda'.",
]

PIADAS = [
    "Por que o 'if' foi ao médico? Porque ele estava sem condição! 😂",
    "O que o 'else' disse para o 'if'? 'Se você não quiser, eu pego!' 😄",
    "Quantos programadores precisa para trocar uma lâmpada? "
    "Nenhum: if (lampada_queimada) ignore... é problema de hardware! 💡",
    "Por que o código estava triste? Porque tinha muitos problemas "
    "e nenhum era 'elif'... digo, fácil de resolver! 🤭",
]

DICAS = [
    "💡 Dica: 'if' testa uma condição. Se for True, ele executa. Se for False, ele pula!",
    "💡 Dica: use 'elif' quando tiver VÁRIAS condições para testar, uma por uma.",
    "💡 Dica: o 'else' não tem condição — ele roda quando NENHUM if/elif passou.",
    "💡 Dica: '==' compara igualdade, mas '=' atribui um valor. Confundir os dois é o bug nº 1!",
    "💡 Dica: dá para colocar um 'if' DENTRO de outro 'if'. Isso se chama if aninhado!",
    "💡 Dica: 'and' exige que TUDO seja verdade. 'or' aceita que SÓ UM seja verdade.",
    "💡 Dica: indentação (os 4 espaços) é lei no Python! É ela que diz o que está dentro do if.",
]


def _contem(texto: str, *palavras: str) -> bool:
    """Retorna True se alguma das palavras aparece no texto."""
    return any(palavra in texto for palavra in palavras)


def responder(mensagem: str) -> str:
    """
    Decide a resposta do Poli usando uma escadinha de if / elif / else.

    Experimente ler este código de cima para baixo: é exatamente assim
    que o Python lê! A primeira condição verdadeira vence. 🏆
    """
    # Normaliza: tudo minúsculo e sem espaços nas pontas
    texto = mensagem.strip().lower()

    # 1️⃣ Mensagem vazia
    if texto == "":
        return "Você não digitou nada... Silêncio também é uma condição: False! 😅 Digite 'ajuda'."

    # 2️⃣ Saudações
    elif _contem(texto, "olá", "ola", "oi", "opa", "e aí", "eai", "bom dia", "boa tarde", "boa noite"):
        return "Olá! 👋 Eu sou o Poli, seu parceiro de lógica! Quer um 'quiz', uma 'dica' ou aprender sobre 'if'?"

    # 3️⃣ Pedido de ajuda
    elif _contem(texto, "ajuda", "help", "o que você sabe", "comandos", "menu"):
        return (
            "Eu posso:\n"
            "  • Explicar: pergunte 'o que é if?', 'o que é elif?' ou 'o que é else?'\n"
            "  • Brincar: peça uma 'piada' ou uma 'dica'\n"
            "  • Treinar: volte ao menu e escolha Quiz ou Desafio!\n"
            "  • Conversar: pergunte meu 'nome' ou 'como você funciona?'"
        )

    # 4️⃣ Explicações sobre if / elif / else (o coração do bot!)
    elif "elif" in texto:
        return (
            "O 'elif' é o meio-termo! Ele significa 'else + if' (senão, se...).\n"
            "Ele testa uma NOVA condição, só quando o 'if' de cima falhou:\n\n"
            "    nota = 7\n"
            "    if nota >= 9:\n"
            "        print('Excelente!')\n"
            "    elif nota >= 6:      # <-- só testa se a de cima for False\n"
            "        print('Aprovado!')\n"
            "    else:\n"
            "        print('Recuperação!')\n\n"
            "Como nota = 7, o resultado é: Aprovado! 🎉"
        )

    elif _contem(texto, "o que é else", "que é else", " else", "else ") or texto == "else":
        return (
            "O 'else' é o plano B! 🛟 Ele NÃO tem condição: roda quando "
            "todos os if/elif acima deram False.\n\n"
            "    idade = 15\n"
            "    if idade >= 18:\n"
            "        print('Pode dirigir')\n"
            "    else:                # <-- sem condição!\n"
            "        print('Ainda não pode dirigir')\n\n"
            "Detalhe importante: só pode existir UM else por if, e ele é sempre o último!"
        )

    elif _contem(texto, "o que é if", "que é if", " if", "if ") or texto == "if":
        return (
            "O 'if' é o porteiro do código! 🚪 Ele só deixa o bloco executar "
            "se a condição for True (verdadeira):\n\n"
            "    fome = True\n"
            "    if fome:             # True? Então entra!\n"
            "        print('Hora de comer! 🍕')\n\n"
            "Se a condição for False, o Python simplesmente PULA o bloco. "
            "Simples assim! Quer conhecer o irmão dele? Pergunte sobre 'elif' ou 'else'."
        )

    # 5️⃣ Como o Poli funciona (meta! 🤯)
    elif _contem(texto, "como você funciona", "como voce funciona", "você é uma ia", "voce e uma ia"):
        return (
            "Segredo revelado: eu não tenho cérebro de robô! 🤖 "
            "Sou feito só de if/elif/else comparando palavras da sua mensagem. "
            "Quando nada combina, caio no 'else' final. Ou seja: EU SOU um exercício de lógica!"
        )

    # 6️⃣ Identidade
    elif _contem(texto, "seu nome", "quem é você", "quem e voce"):
        return "Eu sou o Poli 🤖 — POLI de 'POLIvalente da lógica'! Meu superpoder é transformar if/else em diversão."

    # 7️⃣ Diversão
    elif "piada" in texto:
        return random.choice(PIADAS)

    elif "dica" in texto:
        return random.choice(DICAS)

    # 8️⃣ Operadores de comparação
    elif _contem(texto, "operador", "comparação", "comparacao", "==", ">=", "!="):
        return (
            "Operadores são os 'juízes' das condições ⚖️:\n"
            "  ==  igual a        !=  diferente de\n"
            "  >   maior que      <   menor que\n"
            "  >=  maior ou igual <=  menor ou igual\n\n"
            "E os conectores: 'and' (e), 'or' (ou) e 'not' (não/inverte).\n"
            "Ex: if idade >= 18 and tem_carteira:  -> só entra se os DOIS forem True!"
        )

    # 9️⃣ Agradecimento e tchau
    elif _contem(texto, "obrigad", "valeu", "brigad"):
        return "Por nada! 😊 Lembre-se: praticar um pouquinho todo dia vence qualquer 'else' da vida!"

    elif _contem(texto, "tchau", "adeus", "até mais", "fui"):
        return "Tchau! 👋 Que suas condições sejam sempre True. Até a próxima!"

    # 🔟 ELSE FINAL: nenhuma condição bateu... igualzinho ao Python!
    else:
        return random.choice(RESPOSTAS_PADRAO)
