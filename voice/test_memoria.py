"""Prova que o OMEGA lembra do assunto entre uma frase e a seguinte.

Antes disto, `_perguntar_gemini` montava `contents` do zero a cada fala. O
sintoma parecia ser de escuta ("ele não me entende"), mas não era: ele ouvia
"e o roteiro dela?" perfeitamente e não tinha como saber quem era "ela".

Não gasta cota: a chamada ao Gemini é substituída por um dublê que só registra
o que teria sido enviado. O que se testa aqui é o CONTEÚDO da requisição.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import free_engine  # noqa: E402


class UIFalsa:
    muted = False

    def __init__(self):
        self.log = []

    def write_log(self, m):
        self.log.append(m)

    def set_state(self, *_):
        pass


def motor(local=None):
    m = free_engine.FreeEngine.__new__(free_engine.FreeEngine)
    m.gemini_key = "x"
    m.instructions = "Você é o OMEGA."
    m.tool_executor = lambda n, a: "ok"
    m.ui = UIFalsa()
    m.local_handler = local
    m.tools = []
    m._historico = []
    m._ultima_fala = 0.0
    m._gemini_ate = 0.0
    m._voz_indisponivel = True
    m.enviados = []

    def dublê(contents):
        m.enviados.append(contents)
        return {"candidates": [{"content": {"parts": [{"text": "certo."}]}}]}

    m._chamar_gemini = dublê
    return m


class TestMemoria(unittest.TestCase):
    def test_segunda_pergunta_carrega_a_primeira(self):
        m = motor()
        m._perguntar_gemini("me mostra a pesquisa da Medusa")
        m._perguntar_gemini("e o roteiro dela?")

        enviado = m.enviados[-1]
        textos = [p["text"] for t in enviado for p in t["parts"]]
        self.assertIn("me mostra a pesquisa da Medusa", textos,
                      "a pergunta anterior sumiu — 'dela' fica sem referência")
        self.assertEqual(enviado[-1]["parts"][0]["text"], "e o roteiro dela?")

    def test_comando_local_tambem_vira_contexto(self):
        """O caso mais comum: 'pesquisa da Medusa' nem chega ao Gemini."""
        m = motor(local=lambda texto, ui: "pesquisa — Medusa na tela.")
        m.falar = lambda t, economico=False: None
        m.processar_texto("pesquisa da Medusa")
        m._perguntar_gemini("e o roteiro dela?")

        textos = [p["text"] for t in m.enviados[-1] for p in t["parts"]]
        self.assertIn("pesquisa da Medusa", textos)
        self.assertIn("pesquisa — Medusa na tela.", textos)

    def test_silencio_longo_encerra_o_assunto(self):
        m = motor()
        m._perguntar_gemini("me mostra a pesquisa da Medusa")
        # Um "sim" dito horas depois não pode responder à pergunta da véspera.
        m._ultima_fala -= free_engine.MEMORIA_EXPIRA + 1
        m._perguntar_gemini("e o roteiro dela?")
        self.assertEqual(len(m.enviados[-1]), 1,
                         "o assunto velho deveria ter sido esquecido")

    def test_memoria_nao_cresce_sem_limite(self):
        m = motor()
        for i in range(40):
            m._perguntar_gemini(f"pergunta {i}")
        self.assertLessEqual(len(m._historico), 2 * free_engine.MAX_TURNOS_MEMORIA)

    def test_projetos_reais_vao_na_instrucao(self):
        """Sem a lista, 'aquele negócio da Medusa' não tem como ser resolvido."""
        m = motor()
        texto = m._instrucoes_com_estado()
        self.assertIn("Você é o OMEGA.", texto)
        self.assertIn("PROJETOS QUE EXISTEM AGORA", texto)
        self.assertIn("Medusa", texto)


if __name__ == "__main__":
    unittest.main(verbosity=2)
