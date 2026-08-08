"""Testa a checagem de fatos do OMEGA.

A parte que mais importa aqui não é achar — é NÃO INVENTAR. Isto alimenta
vídeo publicado; uma data errada dita com segurança é pior do que um "não
consegui confirmar".

Os testes de lógica não tocam a rede. Os de rede estão marcados e podem
falhar sem internet — nesse caso são pulados, não reprovados.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import web  # noqa: E402


def tem_rede() -> bool:
    import requests

    try:
        requests.get("https://pt.wikipedia.org", timeout=8)
        return True
    except Exception:  # noqa: BLE001
        return False


class TestTermosChave(unittest.TestCase):
    """O recuo da frase para o nome próprio — sem ele a busca não acha nada."""

    def test_frase_recua_para_o_nome(self):
        self.assertIn("Umibozu", web._termos_chave("Umibozu origem folclore"))

    def test_pergunta_longa_isola_os_proprios(self):
        t = web._termos_chave("Em que ano Lovecraft publicou O Chamado de Cthulhu")
        self.assertTrue(any("Lovecraft" in x and "Cthulhu" in x for x in t),
                        f"os nomes próprios deveriam sair juntos: {t}")

    def test_nao_repete_a_pergunta_original(self):
        p = "Medusa"
        self.assertNotIn(p.lower(), [x.lower() for x in web._termos_chave(p)])

    def test_pergunta_so_de_palavras_vazias(self):
        self.assertEqual(web._termos_chave("o que e isso"), [])


class TestSemInventar(unittest.TestCase):
    def test_pergunta_vazia(self):
        self.assertIn("o quê", web.conferir("").lower())

    @unittest.skipUnless(tem_rede(), "sem internet")
    def test_coisa_inexistente_admite_que_nao_achou(self):
        r = web.conferir("Zxqwbrtl Vplmqx criatura inventada 99999")
        self.assertIn("NADA ENCONTRADO", r)
        self.assertIn("não confirme", r.lower())


@unittest.skipUnless(tem_rede(), "sem internet")
class TestComRede(unittest.TestCase):
    def test_criatura_do_canal_traz_fonte(self):
        r = web.conferir("Umibozu")
        self.assertIn("Fonte: http", r, "resposta sem fonte não serve")
        self.assertIn("japon", r.lower())

    def test_frase_tambem_acha(self):
        """Foi assim que a primeira versão falhou: o modelo pergunta em frase."""
        r = web.conferir("Umibozu origem folclore")
        self.assertIn("Fonte: http", r)

    def test_lembra_de_mandar_para_a_pesquisa_completa(self):
        """A fronteira com a skill precisa estar na cara do modelo."""
        self.assertIn("pesquisa", web.conferir("Medusa").lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
