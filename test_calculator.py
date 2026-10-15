"""Testes do motor de cálculo.

Execute com::

    python3 -m unittest -v
"""

from __future__ import annotations

import math
import unittest

from calculator import CalculatorError, evaluate, format_number, normalize


class TestBasicArithmetic(unittest.TestCase):
    def test_soma(self):
        self.assertEqual(evaluate("2+2").text, "4")

    def test_precedencia(self):
        self.assertEqual(evaluate("2+3*4").text, "14")

    def test_parenteses(self):
        self.assertEqual(evaluate("(2+3)*4").text, "20")

    def test_divisao_decimal(self):
        self.assertEqual(evaluate("7/2").text, "3.5")

    def test_divisao_inteira_e_resto(self):
        self.assertEqual(evaluate("7//2").text, "3")
        self.assertEqual(evaluate("7%3").text, "1")

    def test_numero_negativo(self):
        self.assertEqual(evaluate("-5+3").text, "-2")

    def test_espacos_sao_ignorados(self):
        self.assertEqual(evaluate("  10   -  4 ").text, "6")


class TestNormalizacao(unittest.TestCase):
    def test_circunflexo_vira_potencia(self):
        self.assertEqual(evaluate("2^10").text, "1024")

    def test_simbolos_unicode(self):
        self.assertEqual(evaluate("6 × 7 ÷ 2").text, "21")
        self.assertEqual(evaluate("√9").text, "3")

    def test_multiplicacao_implicita(self):
        self.assertEqual(evaluate("2(3+4)").text, "14")
        self.assertEqual(evaluate("(1+2)(3+4)").text, "21")

    def test_constante_pi_sem_sinal_de_multiplicacao(self):
        self.assertAlmostEqual(evaluate("2pi").value, 2 * math.pi, places=10)

    def test_parêntese_fechado_automaticamente(self):
        self.assertEqual(evaluate("sqrt(9").text, "3")
        self.assertEqual(evaluate("2*(3+4").text, "14")

    def test_normalize_visivel(self):
        self.assertEqual(normalize("2^3"), "2**3")


class TestFuncoes(unittest.TestCase):
    def test_raiz_quadrada(self):
        self.assertEqual(evaluate("sqrt(144)").text, "12")

    def test_raiz_cubica_negativa(self):
        self.assertAlmostEqual(evaluate("cbrt(-27)").value, -3.0, places=10)

    def test_logaritmos(self):
        self.assertEqual(evaluate("log(100)").text, "2")
        self.assertEqual(evaluate("log(8, 2)").text, "3")
        self.assertEqual(evaluate("ln(1)").text, "0")

    def test_fatorial(self):
        self.assertEqual(evaluate("factorial(5)").text, "120")
        self.assertEqual(evaluate("5!").text, "120")
        self.assertEqual(evaluate("6!/3!").text, "120")

    def test_fatorial_nao_confunde_com_diferente(self):
        self.assertEqual(evaluate("5 != 3").text, "1")
        self.assertEqual(evaluate("5 == 5").text, "1")

    def test_arredondamentos(self):
        self.assertEqual(evaluate("round(3.7)").text, "4")
        self.assertEqual(evaluate("floor(3.7)").text, "3")
        self.assertEqual(evaluate("ceil(3.2)").text, "4")

    def test_hypot(self):
        self.assertEqual(evaluate("hypot(3, 4)").text, "5")

    def test_mdc(self):
        self.assertEqual(evaluate("gcd(12, 18)").text, "6")

    def test_potencia_grande(self):
        self.assertEqual(evaluate("2**64").text, "18446744073709551616")


class TestTrigonometria(unittest.TestCase):
    def test_seno_em_radianos(self):
        self.assertAlmostEqual(evaluate("sin(0)").value, 0.0, places=12)

    def test_cosseno_de_pi(self):
        self.assertAlmostEqual(evaluate("cos(pi)").value, -1.0, places=12)

    def test_seno_em_graus(self):
        self.assertAlmostEqual(evaluate("sin(30)", angle="deg").value, 0.5, places=12)

    def test_modo_invalido(self):
        with self.assertRaises(CalculatorError):
            evaluate("sin(1)", angle="grados")

    def test_arco_seno_em_graus(self):
        self.assertAlmostEqual(evaluate("asin(1)", angle="deg").value, 90.0, places=10)


class TestErros(unittest.TestCase):
    def test_expressao_vazia(self):
        with self.assertRaises(CalculatorError):
            evaluate("   ")

    def test_divisao_por_zero(self):
        with self.assertRaises(CalculatorError):
            evaluate("1/0")

    def test_sintaxe_invalida(self):
        with self.assertRaises(CalculatorError):
            evaluate("2++*")

    def test_funcao_desconhecida(self):
        with self.assertRaises(CalculatorError):
            evaluate("__import__('os').system('ls')")

    def test_nome_desconhecido(self):
        with self.assertRaises(CalculatorError):
            evaluate("minha_variavel + 1")

    def test_raiz_de_negativo(self):
        with self.assertRaises(CalculatorError):
            evaluate("sqrt(-1)")

    def test_expoente_gigante(self):
        with self.assertRaises(CalculatorError):
            evaluate("9**9**9")

    def test_fatorial_invalido(self):
        with self.assertRaises(CalculatorError):
            evaluate("factorial(-3)")
        with self.assertRaises(CalculatorError):
            evaluate("factorial(2.5)")

    def test_expressao_longa(self):
        with self.assertRaises(CalculatorError):
            evaluate("1+" * 400 + "1")

    def test_atribuicao_nao_permitida(self):
        with self.assertRaises(CalculatorError):
            evaluate("x = 1")

    def test_numeros_complexos_rejeitados(self):
        with self.assertRaises(CalculatorError):
            evaluate("(-8)**0.5")


class TestFormatacao(unittest.TestCase):
    def test_inteiro_sem_decimal(self):
        self.assertEqual(format_number(4.0), "4")

    def test_ruido_de_ponto_flutuante(self):
        self.assertEqual(evaluate("0.1+0.2").text, "0.3")

    def test_notacao_cientifica(self):
        self.assertEqual(format_number(1.5e-9), "1.5e-09")

    def test_divisao_um_terco(self):
        self.assertEqual(evaluate("1/3").text, "0.333333333333")


class TestApi(unittest.TestCase):
    def test_resultado_vira_dicionario(self):
        payload = evaluate("10/4").as_dict()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["result"], "2.5")
        self.assertEqual(payload["value"], 2.5)
        self.assertEqual(payload["expression"], "10/4")
        self.assertEqual(payload["angle"], "rad")

    def test_modo_grau_no_payload(self):
        payload = evaluate("sin(90)", angle="deg").as_dict()
        self.assertEqual(payload["angle"], "deg")
        self.assertEqual(payload["result"], "1")


if __name__ == "__main__":
    unittest.main(verbosity=2)
