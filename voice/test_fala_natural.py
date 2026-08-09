"""Todo comando tem que atender a fala natural, não só à frase exata.

Medido antes do conserto: de 20 formas naturais de dizer comandos comuns,
**18 caíam no modelo** em vez de serem atendidas localmente. Isso é um
problema de usabilidade sempre — ninguém fala "projetos", fala "me mostra os
projetos" — e vira um problema de FUNCIONAMENTO quando a cota do Gemini
estoura: cair no modelo passa a significar não funcionar.

O princípio já estava escrito no projeto para os comandos com alvo
(`_extrair_verbo_e_alvo`): a palavra-chave é procurada em qualquer posição.
Os comandos simples tinham ficado para trás, com `low in (...)`.

Este teste existe para que o próximo comando novo não repita isso.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import local_commands as lc  # noqa: E402


class UIFalsa:
    def write_log(self, m):
        pass

    def show_document(self, t, c):
        pass

    def show_hud(self):
        pass

    def falar(self, t, economico=False):
        pass

    def esquecer(self):
        return "esqueci"


def responde(frase: str):
    """Atendeu localmente? (None = cairia no modelo)"""
    import tools.tendencias as tend

    with patch.object(lc, "_ensure_studio", return_value=None), \
            patch.object(lc, "_get_projects", return_value=[]), \
            patch.object(lc, "studio_control", lambda a: "ok"), \
            patch.object(tend, "pesquisar", lambda a="": "material"):
        return lc.handle(frase, UIFalsa())


class TestComandosSimples(unittest.TestCase):
    """Como uma pessoa realmente fala."""

    NATURAIS = [
        "me mostra os projetos",
        "quais projetos eu tenho",
        "lista os projetos",
        "me mostra a ajuda",
        "quais são os comandos",
        "como está o progresso",
        "me diz o progresso dos renders",
        "volta pro início",
        "me mostra as tendências",
        "o que está em alta hoje",
        "revisa as regras pra mim",
        "me mostra as regras",
        "esquece isso",
        "muda de assunto",
        "como você está me entendendo",
        "me mostra o diagnóstico",
        "pode processar o curso agora",
    ]

    def test_nenhuma_cai_no_modelo(self):
        falharam = [f for f in self.NATURAIS if responde(f) is None]
        self.assertFalse(
            falharam,
            f"{len(falharam)} de {len(self.NATURAIS)} cairiam no Gemini "
            f"(e com a cota estourada, isso é não funcionar): {falharam}")


class TestNaoRoubaComandoAlheio(unittest.TestCase):
    """Casar em qualquer posição é poderoso e perigoso na mesma medida."""

    def test_comandos_com_alvo_seguem_o_caminho_certo(self):
        for frase, esperado in (
            ("pesquisa da Medusa", "Medusa"),
            ("ler o roteiro da Medusa", "roteiro"),
            ("apagar projeto Medusa", "remover"),
        ):
            r = responde(frase)
            self.assertIsNotNone(r, frase)
            self.assertIn(esperado.lower(), str(r).lower(), frase)

    def test_frase_de_conversa_nao_vira_comando(self):
        """Se tudo virar comando, a conversa livre morre."""
        for frase in ("bom dia, tudo bem?",
                      "o que você acha dessa ideia",
                      "me conta uma piada"):
            self.assertIsNone(responde(frase),
                              f"'{frase}' foi capturado como comando")

    def test_parar_leitura_nao_encerra_a_aula(self):
        from tools.local_commands import _e_fim_de_aula

        self.assertFalse(_e_fim_de_aula("parar"))


class TestOCasador(unittest.TestCase):
    def test_palavra_inteira_e_nao_pedaco(self):
        """"para" não pode casar dentro de "separar"."""
        self.assertFalse(lc._disse("quero separar as coisas", "para"))
        self.assertTrue(lc._disse("pode parar agora", "parar"))

    def test_ignora_acento(self):
        self.assertTrue(lc._disse("me mostra as tendências", "tendencias"))
        self.assertTrue(lc._disse("qual o diagnostico", "diagnóstico"))

    def test_chave_com_espaco_casa_como_trecho(self):
        self.assertTrue(lc._disse("me diz qual motor está no ar", "qual motor"))
        self.assertFalse(lc._disse("qual criatura tem motor", "qual motor"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
