"""Testes do Poli — rode com:  python -m pytest tests/ -q   (ou só: python -m unittest discover tests)"""

import unittest

from mini_bot.cerebro import responder
from mini_bot.quiz import DESAFIOS, PERGUNTAS, esta_correta


class TestCerebro(unittest.TestCase):
    def test_saudacao(self):
        self.assertIn("Poli", responder("olá"))

    def test_explica_if(self):
        self.assertIn("porteiro", responder("o que é if?"))

    def test_explica_elif_antes_de_if(self):
        # 'elif' precisa ser detectado antes das outras regras
        self.assertIn("meio-termo", responder("o que é elif?"))

    def test_piada(self):
        self.assertTrue(len(responder("me conta uma piada")) > 10)

    def test_mensagem_vazia_cai_na_regra_vazia(self):
        self.assertIn("não digitou nada", responder("   "))

    def test_desconhecido_cai_no_else(self):
        resposta = responder("xyzqw blorp zzzz")
        self.assertTrue(len(resposta) > 10)


class TestQuiz(unittest.TestCase):
    def test_todas_perguntas_tem_resposta_valida(self):
        for item in PERGUNTAS + DESAFIOS:
            self.assertTrue(0 <= item["correta"] < len(item["opcoes"]))
            self.assertTrue(item["explicacao"])

    def test_esta_correta(self):
        item = PERGUNTAS[0]
        self.assertTrue(esta_correta(item, item["correta"]))
        errado = (item["correta"] + 1) % len(item["opcoes"])
        self.assertFalse(esta_correta(item, errado))


if __name__ == "__main__":
    unittest.main()
