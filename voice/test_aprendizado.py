"""Testa o laço que faz o OMEGA melhorar com o uso.

A pergunta do Samuel era "como se treina um agente desses". Para o caso dele
a resposta não é fine-tuning — é isto: registrar o que falhou, deixá-lo
corrigir, e realimentar o vocabulário. O que se verifica aqui é que o laço
FECHA: uma lição dada por voz precisa valer na mesma hora, tanto na correção
do texto quanto no viés que guia a escuta. Uma lição que só vale no próximo
reinício não é aprendizado, é configuração.

Usa arquivos temporários — não encosta no diário real do Samuel.
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import aprendizado, contexto_fala, vocabulario  # noqa: E402
import free_engine  # noqa: E402


class Isolado(unittest.TestCase):
    """Cada teste com diário e vocabulário próprios."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self._diario, self._aprendido = aprendizado.DIARIO, aprendizado.APRENDIDO
        aprendizado.DIARIO = base / "aprendizado.jsonl"
        aprendizado.APRENDIDO = base / "vocabulario-aprendido.json"
        # Sem isto o mapa continua com as lições REAIS do Samuel, carregadas
        # na importação, e o teste passa (ou falha) por causa delas.
        vocabulario.recarregar()
        contexto_fala.hotwords(forcar=True)

    def tearDown(self):
        aprendizado.DIARIO, aprendizado.APRENDIDO = self._diario, self._aprendido
        vocabulario.recarregar()
        contexto_fala.hotwords(forcar=True)
        self.tmp.cleanup()


class TestDiario(Isolado):
    def test_guarda_o_que_ouvi_e_o_que_entendi(self):
        aprendizado.registrar("amiga abre a meduza", "Ômega abre a Medusa",
                              "local", True)
        reg = aprendizado.ler()[-1]
        self.assertEqual(reg["bruta"], "amiga abre a meduza")
        self.assertEqual(reg["corrigida"], "Ômega abre a Medusa")
        self.assertTrue(reg["ok"])

    def test_nao_derruba_a_voz_quando_o_disco_falha(self):
        aprendizado.DIARIO = Path("Z:/inexistente/aprendizado.jsonl")
        aprendizado.registrar("oi", "oi", "local", True)  # não pode levantar

    def test_so_as_falhas_viram_candidatos(self):
        aprendizado.registrar("mostra o roteiro do umiboso", "", "gemini", False)
        aprendizado.registrar("abre o umiboso", "", "gemini", False)
        aprendizado.registrar("pesquisa da medusa", "", "local", True)
        palavras = [p for p, _ in aprendizado.candidatos(minimo=2)]
        self.assertIn("umiboso", palavras)
        self.assertNotIn("medusa", palavras,
                         "o que funcionou não é candidato a ensinar")

    def test_palavras_comuns_nao_poluem_a_lista(self):
        for _ in range(3):
            aprendizado.registrar("me arruma aquele negocio ali", "", "gemini", False)
        palavras = [p for p, _ in aprendizado.candidatos(minimo=2)]
        self.assertNotIn("aquele", palavras)


class TestLicaoValeNaHora(Isolado):
    """O ponto do exercício: ensinar tem que surtir efeito imediato."""

    def test_corrige_o_texto_imediatamente(self):
        self.assertNotIn("Umibozu", vocabulario.corrigir("abre o umiboso"))
        aprendizado.ensinar("umiboso", "Umibozu")
        self.assertIn("Umibozu", vocabulario.corrigir("abre o umiboso"))

    def test_passa_a_guiar_a_escuta(self):
        """Sem isto o Whisper continuaria produzindo o erro para sempre."""
        aprendizado.ensinar("zaratustro", "Zaratustra")
        self.assertIn("Zaratustra", contexto_fala.hotwords(forcar=True))

    def test_recusa_licao_pela_metade(self):
        self.assertIn("duas formas", aprendizado.ensinar("umiboso", ""))
        self.assertEqual(aprendizado.aprendidos(), {})

    def test_licao_sobrevive_ao_reinicio(self):
        aprendizado.ensinar("umiboso", "Umibozu")
        self.assertEqual(
            json.loads(aprendizado.APRENDIDO.read_text(encoding="utf-8")),
            {"umiboso": "Umibozu"})


class TestSucessoOuFalha(unittest.TestCase):
    """Se "não entendi" contasse como sucesso, nada nunca entraria na lista."""

    def test_reconhece_as_respostas_de_fracasso(self):
        for r in ("Não entendi qual projeto é Xyz.",
                  "Falhou: erro de rede",
                  "Ferramenta desconhecida: abc",
                  "Não consegui confirmar."):
            self.assertFalse(free_engine._deu_certo(r), r)

    def test_reconhece_as_de_sucesso(self):
        for r in ("pesquisa — Medusa na tela.",
                  "Lendo o roteiro — 12 trechos.",
                  "Interrompendo a leitura."):
            self.assertTrue(free_engine._deu_certo(r), r)

    def test_resposta_vazia_nao_e_sucesso(self):
        self.assertFalse(free_engine._deu_certo(""))


if __name__ == "__main__":
    unittest.main(verbosity=2)
