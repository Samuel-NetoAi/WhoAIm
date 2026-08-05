"""Testes do alinhador — o coração do sistema, testado SEM áudio.

O ASR é simulado de propósito: é assim que dá para reproduzir de forma
determinística os casos que dão errado no mundo real (transcrição incompleta,
palavra trocada, silêncio no meio) e verificar que o alinhamento degrada com
elegância em vez de quebrar.
"""

import unittest

from alpha_align.alinhador import PalavraASR, alinhar
from alpha_align.roteiro import carregar
from alpha_align.texto import normalizar

ROTEIRO = """---
**[Bloco 1 — abertura]**
Ninguem sabe ao certo de onde ela veio.

**[Bloco 2 — origem]**
Os gregos diziam que Medusa foi criada assim.
"""


def asr(*pares: tuple[str, float, float]) -> list[PalavraASR]:
    return [
        PalavraASR(palavra=p, chave=normalizar(p), t0=t0, t1=t1) for p, t0, t1 in pares
    ]


class TestAsrPerfeito(unittest.TestCase):
    """Piso de qualidade: com ASR perfeito, todo tempo é medido, nenhum estimado."""

    def setUp(self):
        self.roteiro = carregar(ROTEIRO, e_texto=True)
        palavras = self.roteiro.chaves
        self.asr = asr(*[(p, i * 1.0, i * 1.0 + 0.5) for i, p in enumerate(palavras)])
        self.resultado = alinhar(self.roteiro, self.asr, duracao_audio=20.0)

    def test_todas_as_palavras_viram_ancora(self):
        self.assertEqual(self.resultado.confianca, 1.0)
        self.assertTrue(all(p.ancora for p in self.resultado.palavras))

    def test_tempos_batem_com_o_audio(self):
        primeira = self.resultado.palavras[0]
        self.assertAlmostEqual(primeira.t0, 0.0)
        self.assertAlmostEqual(primeira.t1, 0.5)

    def test_blocos_recebem_inicio_e_fim(self):
        b1, b2 = self.resultado.blocos
        self.assertLess(b1.t1, b2.t0 + 0.001)
        self.assertEqual(len(self.resultado.blocos), 2)


class TestAsrEsparso(unittest.TestCase):
    """O caso real medido: o Vosk acerta uma fração das palavras."""

    def setUp(self):
        self.roteiro = carregar(ROTEIRO, e_texto=True)
        # Só 4 das 14 palavras reconhecidas, espalhadas pelo áudio.
        self.resultado = alinhar(
            self.roteiro,
            asr(("sabe", 0.5, 0.9), ("veio", 4.0, 4.4), ("gregos", 6.0, 6.5),
                ("criada", 10.0, 10.6)),
            duracao_audio=13.0,
        )

    def test_confianca_reflete_a_esparsidade(self):
        self.assertGreater(self.resultado.confianca, 0.2)
        self.assertLess(self.resultado.confianca, 0.4)

    def test_tempo_nunca_anda_para_tras(self):
        tempos = [(p.t0, p.t1) for p in self.resultado.palavras]
        for (t0, t1), (prox_t0, _) in zip(tempos, tempos[1:]):
            self.assertLessEqual(t0, t1)
            self.assertLessEqual(t1, prox_t0 + 0.001)

    def test_palavras_ancoradas_mantem_o_tempo_medido(self):
        ancoradas = {p.chave: (p.t0, p.t1) for p in self.resultado.palavras if p.ancora}
        self.assertEqual(ancoradas["sabe"], (0.5, 0.9))
        self.assertEqual(ancoradas["gregos"], (6.0, 6.5))

    def test_interpolacao_fica_dentro_do_audio(self):
        self.assertGreaterEqual(self.resultado.palavras[0].t0, 0.0)
        self.assertLessEqual(self.resultado.palavras[-1].t1, 13.001)

    def test_palavra_longa_recebe_mais_tempo_que_curta(self):
        por_chave = {p.chave: p for p in self.resultado.palavras if not p.ancora}
        curta = por_chave["de"]
        longa = por_chave["ninguem"]
        self.assertGreater(longa.t1 - longa.t0, curta.t1 - curta.t0)


class TestRobustez(unittest.TestCase):
    def setUp(self):
        self.roteiro = carregar(ROTEIRO, e_texto=True)

    def test_texto_vem_do_roteiro_mesmo_com_asr_errado(self):
        # O ASR ouviu "medusa" como "vedeta" — a legenda não pode herdar isso.
        resultado = alinhar(
            self.roteiro,
            asr(("vedeta", 6.0, 6.6), ("gregos", 5.0, 5.4)),
            duracao_audio=12.0,
        )
        chaves = [p.chave for p in resultado.palavras]
        self.assertIn("medusa", chaves)
        self.assertNotIn("vedeta", chaves)

    def test_sem_nenhuma_ancora_ainda_cobre_o_audio_inteiro(self):
        resultado = alinhar(self.roteiro, asr(("xxxxx", 1.0, 2.0)), duracao_audio=30.0)
        self.assertEqual(resultado.confianca, 0.0)
        self.assertAlmostEqual(resultado.palavras[0].t0, 0.0)
        self.assertAlmostEqual(resultado.palavras[-1].t1, 30.0, places=1)

    def test_ancora_isolada_de_palavra_curta_e_descartada(self):
        # "de" sozinho no fim do áudio arrastaria toda a interpolação com ele.
        resultado = alinhar(self.roteiro, asr(("de", 11.5, 11.7)), duracao_audio=12.0)
        self.assertEqual(resultado.confianca, 0.0)

    def test_ancora_isolada_de_palavra_longa_e_mantida(self):
        resultado = alinhar(self.roteiro, asr(("diziam", 6.0, 6.5)), duracao_audio=12.0)
        self.assertGreater(resultado.confianca, 0.0)

    def test_cortes_saem_nos_limites_de_bloco(self):
        resultado = alinhar(
            self.roteiro, asr(("gregos", 6.0, 6.5)), duracao_audio=12.0
        )
        cortes = resultado.cortes
        self.assertEqual(cortes[0], 0.0)
        self.assertEqual(cortes[-1], 12.0)
        self.assertEqual(len(cortes), len(resultado.blocos) + 1)

    def test_ancora_fora_da_posicao_esperada_e_rejeitada(self):
        """Regressão: uma âncora deslocada arrastava o alinhamento inteiro.

        "gregos" está a ~60% do roteiro. Se o ASR disser que ela foi falada aos
        0,5s de um áudio de 60s (3%), ele casou com a ocorrência errada — e
        aceitar isso comprimia tudo que vem antes num punhado de segundos.
        Medido na simulação: sem este filtro, o erro mediano com transcrição
        ruim ia a dezenas de segundos.
        """
        resultado = alinhar(
            self.roteiro, asr(("gregos", 0.5, 0.9)), duracao_audio=60.0
        )
        self.assertEqual(resultado.confianca, 0.0)

    def test_ancora_na_posicao_esperada_e_aceita(self):
        # Mesma palavra, agora num tempo compatível com onde ela está no texto.
        resultado = alinhar(
            self.roteiro, asr(("gregos", 33.0, 33.6)), duracao_audio=60.0
        )
        self.assertGreater(resultado.confianca, 0.0)

    def test_silencio_no_fim_do_arquivo_nao_derruba_as_ancoras(self):
        """Narração exportada costuma trazer respiro no início e no fim.

        Se a posição fosse medida contra a duração do ARQUIVO, esse silêncio
        deslocaria todas as frações e o filtro de coerência rejeitaria âncoras
        perfeitamente boas.
        """
        chaves = self.roteiro.chaves
        fala = [(p, 2.0 + i * 0.8, 2.0 + i * 0.8 + 0.6) for i, p in enumerate(chaves)]
        # ~13s de fala num arquivo de 17s: 2s de respiro antes, 2s depois.
        resultado = alinhar(self.roteiro, asr(*fala), duracao_audio=17.0)
        self.assertEqual(resultado.confianca, 1.0)

    def test_roteiro_vazio_e_erro_explicito(self):
        with self.assertRaises(ValueError):
            alinhar(carregar("---\n", e_texto=True), asr(), duracao_audio=5.0)


if __name__ == "__main__":
    unittest.main()
