"""Testa a troca de motor de voz em pleno voo.

O padrão passou a ser o motor LOCAL, e a razão é cota: o Live cobra pelo
ÁUDIO — uma troca curta medida aqui deu 436 tokens, e ele consome enquanto
ouve, não só quando responde. Na camada gratuita isso estoura no meio da
sessão, e foi o que aconteceu com o Samuel (o `1008 policy violation` do
print dele). O local manda texto, e a maior parte do uso são COMANDOS.

Então o Live sobe sob demanda. O que se verifica aqui:
  1. o padrão é o econômico;
  2. "modo conversa" pede a troca, dito de várias formas;
  3. "vamos conversar" NÃO troca de motor — seria péssimo trocar de motor
     porque ele usou a palavra numa frase comum;
  4. o motor em execução sai quando o outro é pedido (senão a troca só
     valeria no próximo reinício do app).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

sys.argv = ["t"]
from tools import motor  # noqa: E402
from tools.local_commands import _quer_modo  # noqa: E402


class TestPadrao(unittest.TestCase):
    def test_o_padrao_e_o_economico(self):
        import main

        self.assertEqual(main.escolher_motor({"gemini_api_key": "x"}), "free")

    def test_config_ainda_manda(self):
        import main

        self.assertEqual(main.escolher_motor({"engine": "live"}), "live")


class TestPedido(unittest.TestCase):
    def setUp(self):
        motor.definir_atual("free")

    def test_troca_dita_de_varias_formas(self):
        for frase in ("modo conversa", "muda pro modo conversa",
                      "entra no modo live", "modo tempo real"):
            self.assertTrue(
                _quer_modo(frase, ("conversa", "live", "tempo", "real")), frase)

    def test_a_palavra_solta_nao_troca_motor(self):
        """"vamos conversar" é conversa, não pedido de trocar de motor."""
        for frase in ("vamos conversar", "quero conversar sobre a Medusa",
                      "fala normal comigo", "conversa comigo"):
            self.assertFalse(_quer_modo(frase, ("conversa", "normal")), frase)

    def test_pedir_marca_e_o_motor_ve(self):
        self.assertIn("Trocando", motor.pedir("live"))
        self.assertEqual(motor.quer_trocar(), "live")

    def test_pedir_o_que_ja_esta_no_ar(self):
        self.assertIn("Já estou", motor.pedir("free"))
        self.assertIsNone(motor.quer_trocar())

    def test_motor_desconhecido(self):
        self.assertIn("Não conheço", motor.pedir("banana"))

    def test_consumir_limpa_o_pedido(self):
        motor.pedir("live")
        self.assertEqual(motor.consumir_pedido(), "live")
        self.assertIsNone(motor.quer_trocar())


class TestOsMotoresSaem(unittest.TestCase):
    """Sem isto a troca só valeria no próximo reinício do app."""

    def setUp(self):
        motor.definir_atual("free")

    def tearDown(self):
        motor.definir_atual("")

    def test_o_local_sai_do_laco(self):
        import inspect

        import free_engine

        fonte = inspect.getsource(free_engine.FreeEngine.run)
        self.assertIn("quer_trocar", fonte,
                      "o motor local nunca sairia para dar lugar ao Live")

    def test_o_live_sai_do_laco(self):
        import inspect

        import live_engine

        fonte = inspect.getsource(live_engine.LiveEngine._bombear_microfone)
        self.assertIn("quer_trocar", fonte,
                      "o Live nunca sairia para dar lugar ao local")

    def test_a_saida_do_live_nao_conta_como_falha(self):
        """Trocar de motor não pode acionar o aviso de 'a voz caiu'.

        Teste de COMPORTAMENTO, não de texto do arquivo: a primeira versão
        comparava posições no fonte e pegou um `except` de outro bloco.
        """
        from unittest.mock import patch

        import live_engine

        class UIFalsa:
            muted = False

            def __init__(self):
                self.log = []

            def write_log(self, m):
                self.log.append(m)

            def set_state(self, *_):
                pass

        ui = UIFalsa()
        m = live_engine.LiveEngine(gemini_key="x", instructions="i",
                                   tool_executor=lambda n, a: "ok", ui=ui)

        async def sessao_que_troca():
            raise live_engine._TrocaDeMotor()

        with patch.object(live_engine.sd, "RawInputStream"),                 patch.object(m, "_sessao", sessao_que_troca),                 patch.object(m, "_tocar", lambda: None):
            resultado = m.run()

        self.assertTrue(resultado, "a troca foi tratada como falha do Live")
        self.assertEqual(m.motivo_da_queda, "",
                         "trocar de motor não é motivo de queda")
        caiu = [l for l in ui.log if "caiu" in l]
        self.assertFalse(caiu, f"avisou que a voz caiu numa troca pedida: {caiu}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
