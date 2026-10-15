#!/usr/bin/env python3
"""
🤖 MINI BOT Poli — aprenda lógica e if/else se divertindo!

Como rodar:
    python bot.py            -> abre o bot interativo
    python bot.py --demo     -> roda uma demonstração automática (sem digitar)
    python bot.py --quiz     -> vai direto para o quiz

Sem nenhuma biblioteca externa: só Python puro (3.8+).
"""

import random
import sys

from mini_bot.cerebro import responder
from mini_bot.quiz import (
    DESAFIOS,
    EXPLICACOES,
    PERGUNTAS,
    desafio_aleatorio,
    esta_correta,
    pergunta_aleatoria,
)

# Mensagens de comemoração / consolo (escolhidas com random, decididas com if!)
FESTA = ["🎉 ACERTOU! Mandou muito bem!", "🏆 Isso aí! Seu cérebro fez um if perfeito!", "🚀 Boa! Condição True para você!"]
OPS = ["❌ Ops! Não foi dessa vez...", "🙈 Quase! Caiu no else...", "💪 Errou, mas errar é o melhor debugger!"]


def mostrar_codigo(codigo: str) -> None:
    print("  ┌" + "─" * 46)
    for linha in codigo.splitlines():
        print(f"  │ {linha}")
    print("  └" + "─" * 46)


def pedir_opcao(total: int) -> int:
    """Lê um número de 1 até `total`. Devolve -1 se a entrada for inválida."""
    entrada = input(f"  Sua resposta (1-{total}): ").strip()
    if entrada.isdigit() and 1 <= int(entrada) <= total:
        return int(entrada) - 1
    else:
        return -1


def jogar_rodada(item: dict, pontos: int, titulo: str) -> int:
    """Mostra uma pergunta/desafio e devolve os pontos atualizados."""
    print(f"\n{titulo}")
    if "objetivo" in item:
        print(f"  🎯 Objetivo: {item['objetivo']}")
    mostrar_codigo(item["codigo"])
    for numero, opcao in enumerate(item["opcoes"], start=1):
        print(f"    {numero}) {opcao}")

    escolha = pedir_opcao(len(item["opcoes"]))

    if escolha == -1:
        print("  ⚠️ Resposta inválida! Era só digitar o número da opção. 😉")
    elif esta_correta(item, escolha):
        pontos += 10
        print(f"  {random.choice(FESTA)} +10 pontos!")
    else:
        certa = item["opcoes"][item["correta"]]
        print(f"  {random.choice(OPS)} A resposta certa era: '{certa}'")

    print(f"  📖 Por quê? {item['explicacao']}")
    print(f"  ⭐ Pontos: {pontos}")
    return pontos


def modo_quiz(pontos: int) -> int:
    print("\n🎯 QUIZ RELÂMPAGO — O que esse código imprime? (digite 0 numa resposta para voltar)")
    for rodada in range(1, 4):
        pontos = jogar_rodada(pergunta_aleatoria(), pontos, f"--- Pergunta {rodada} de 3 ---")
    print("\n🏁 Fim do quiz! Volte ao menu para jogar mais ou conversar comigo.")
    return pontos


def modo_desafio(pontos: int) -> int:
    desafio = desafio_aleatorio()
    return jogar_rodada(desafio, pontos, f"🧩 DESAFIO: {desafio['titulo']} — complete o código!")


def modo_explicacao() -> None:
    print("\n📚 EXPLICAÇÃO EXPRESS — escolha um tema:")
    for chave, (titulo, _) in EXPLICACOES.items():
        print(f"  {chave}) {titulo}")
    escolha = input("  Tema (número): ").strip()
    if escolha in EXPLICACOES:
        titulo, texto = EXPLICACOES[escolha]
        print(f"\n{titulo}\n{texto}")
    else:
        print("  Tema não encontrado... viu só? Você caiu no meu else! 😄")


def modo_conversa() -> None:
    print("\n💬 MODO CONVERSA — fale comigo! (tente: 'o que é if?', 'piada', 'dica' ou 'sair')")
    while True:
        mensagem = input("\nVocê: ").strip()
        if mensagem.lower() in ("sair", "voltar", "menu"):
            print("Poli: Voltando ao menu! 👋")
            break
        else:
            print(f"Poli: {responder(mensagem)}")


def modo_adivinhe(pontos: int) -> int:
    """Jogo bônus: adivinhe o número — treina if/elif/else com dicas de quente/frio."""
    segredo = random.randint(1, 20)
    print("\n🔢 ADIVINHE O NÚMERO — pensei num número de 1 a 20. Você tem 5 tentativas!")
    for tentativa in range(1, 6):
        entrada = input(f"  Tentativa {tentativa}/5: ").strip()
        if not entrada.isdigit():
            print("  Isso não é um número! Tentativa perdida... 😅")
            continue
        palpite = int(entrada)
        if palpite == segredo:
            pontos += 20
            print(f"  🎉 ACERTOU! Era {segredo}! +20 pontos (total: {pontos})")
            return pontos
        elif palpite < segredo:
            print("  📈 Maior! Tenta um número maior...")
        else:
            print("  📉 Menor! Tenta um número menor...")
    print(f"  😢 Acabaram as tentativas! O número era {segredo}.")
    return pontos


MENU = """
╔══════════════════════════════════════════╗
║   🤖 POLI — seu mini bot de lógica!      ║
╠══════════════════════════════════════════╣
║  1) 💬 Conversar com o Poli             ║
║  2) 🎯 Quiz: o que o código imprime?    ║
║  3) 🧩 Desafio: complete o if           ║
║  4) 📚 Explicação express               ║
║  5) 🔢 Adivinhe o número (bônus)        ║
║  0) 🚪 Sair                              ║
╚══════════════════════════════════════════╝"""


def main() -> None:
    if "--demo" in sys.argv:
        demo()
        return

    print("🤖 Olá! Eu sou o Poli, seu mini bot para treinar LÓGICA e if/else!")
    nome = input("Qual é o seu nome? ").strip() or "Dev"
    if "--quiz" in sys.argv:
        modo_quiz(0)
        return

    pontos = 0
    while True:
        print(MENU)
        opcao = input(f"\n{nome}, escolha uma opção: ").strip()

        if opcao == "1":
            modo_conversa()
        elif opcao == "2":
            pontos = modo_quiz(pontos)
        elif opcao == "3":
            pontos = modo_desafio(pontos)
        elif opcao == "4":
            modo_explicacao()
        elif opcao == "5":
            pontos = modo_adivinhe(pontos)
        elif opcao == "0":
            print(f"\n👋 Tchau, {nome}! Você terminou com ⭐ {pontos} pontos.")
            if pontos >= 30:
                print("🏆 Nível: Mestre do if/else!")
            elif pontos >= 10:
                print("🥈 Nível: Aprendiz de lógica em ascensão!")
            else:
                print("🌱 Nível: Iniciante — volte e pratique mais, você consegue!")
            break
        else:
            print("⚠️ Opção inválida! Você caiu no else do menu... escolha de 0 a 5. 😄")


def demo() -> None:
    """Demonstração automática, sem precisar digitar nada."""
    print("=== DEMO DO POLI ===\n")
    for pergunta in ["Olá!", "o que é if?", "e o elif?", "me conta uma piada", "uma dica, por favor"]:
        print(f"Você: {pergunta}\nPoli: {responder(pergunta)}\n")
    print(f"📚 Banco de conteúdo: {len(PERGUNTAS)} perguntas de quiz e {len(DESAFIOS)} desafios!")
    print("Para jogar de verdade, rode:  python bot.py")


if __name__ == "__main__":
    main()
