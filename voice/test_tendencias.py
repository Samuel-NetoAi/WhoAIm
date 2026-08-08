"""Testa a busca de tendências para escolher a próxima criatura.

O pedido do Samuel era "abre o Google Trends e analisa". Medir mudou o
desenho, e os testes guardam o porquê:

- o "em alta" do Brasil é futebol e notícia (medido: "santos futebol clube",
  "brasileirão série a"). Serve para o país, não para um canal de mitologia;
- as consultas EM ASCENSÃO do Trends servem muito, mas vêm de uma API interna
  que responde 429 com frequência — é melhor-esforço, e a falha precisa ser
  DITA, não virar "nada em alta";
- o autocomplete do YouTube é o mais útil e o mais estável: é o que se digita
  onde os vídeos dele vivem.

Os testes de rede são pulados sem internet.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import tendencias  # noqa: E402


def tem_rede() -> bool:
    import requests

    try:
        requests.get("https://suggestqueries-clients6.youtube.com", timeout=8)
        return True
    except Exception:  # noqa: BLE001
        return False


class TestSemRede(unittest.TestCase):
    def test_separa_o_que_ele_ja_produziu(self):
        feitos = {"medusa", "cthullhu"}
        self.assertFalse(tendencias._e_novidade("historia da Medusa", feitos))
        self.assertTrue(tendencias._e_novidade("lendas do folclore", feitos))

    def test_ignora_acento_ao_comparar(self):
        self.assertFalse(tendencias._e_novidade("A DRÍADE da floresta",
                                                {"driade"}))

    def test_falha_de_rede_nao_vira_nada_em_alta(self):
        """Silêncio por falha é indistinguível de silêncio por ausência."""
        original = tendencias.sugestoes_youtube, tendencias.em_ascensao
        try:
            tendencias.sugestoes_youtube = lambda *a, **k: []
            tendencias.em_ascensao = lambda *a, **k: ([], "429 do Trends")
            r = tendencias.pesquisar("mitologia")
        finally:
            tendencias.sugestoes_youtube, tendencias.em_ascensao = original
        self.assertIn("NÃO CONSEGUI DADOS", r)
        self.assertIn("não invente", r.lower())

    def test_trends_fora_do_ar_nao_apaga_o_youtube(self):
        original = tendencias.em_ascensao
        try:
            tendencias.em_ascensao = lambda *a, **k: ([], "429")
            r = tendencias.pesquisar("mitologia") if tem_rede() else ""
        finally:
            tendencias.em_ascensao = original
        if not r:
            self.skipTest("sem internet")
        self.assertIn("YOUTUBE", r, "perdeu a fonte que funcionava")
        self.assertIn("indisponível", r, "escondeu que o Trends falhou")


@unittest.skipUnless(tem_rede(), "sem internet")
class TestComRede(unittest.TestCase):
    def test_autocomplete_do_youtube_responde(self):
        s = tendencias.sugestoes_youtube("mitologia")
        print(f"\n   YouTube: {s[:4]}")
        self.assertTrue(s, "o autocomplete do YouTube é a fonte principal")

    def test_material_manda_falar_curto_e_citar_a_origem(self):
        """Isto vai ser FALADO: lista longa em markdown vira ruído na voz."""
        r = tendencias.pesquisar("mitologia")
        if "NÃO CONSEGUI DADOS" in r:
            self.skipTest("as duas fontes falharam agora")
        self.assertIn("FALADO EM VOZ ALTA", r)
        self.assertIn("3 melhores", r)
        self.assertIn("não prometa alcance", r.lower())

    def test_em_alta_do_dia_existe_mas_e_generico(self):
        """Guardado com a ressalva: é o país inteiro, não o nicho dele."""
        alta = tendencias.alta_do_dia()
        print(f"   em alta hoje: {alta[:3]}")
        self.assertIsInstance(alta, list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
