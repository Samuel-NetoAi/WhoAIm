"""Testes das legendas — os limites de leitura são o produto aqui."""

import unittest

from alpha_align.alinhador import PalavraASR, alinhar
from alpha_align.legendas import (
    DURACAO_MAXIMA,
    MAX_CARACTERES_POR_LINHA,
    gerar,
    para_srt,
    quebrar_em_linhas,
)
from alpha_align.roteiro import carregar
from alpha_align.texto import normalizar

LONGO = """---
Reza a lenda que cada estacao veste uma Driade diferente, um rosto para o gelo e outro para as flores que voltam depois do inverno.

Poucos mortais ja as viram.
"""


def alinhamento_de_teste(duracao=30.0):
    roteiro = carregar(LONGO, e_texto=True)
    palavras = roteiro.chaves
    asr = [
        PalavraASR(p, normalizar(p), i * (duracao / len(palavras)),
                   i * (duracao / len(palavras)) + 0.4)
        for i, p in enumerate(palavras)
    ]
    return alinhar(roteiro, asr, duracao_audio=duracao)


class TestQuebraDeLinha(unittest.TestCase):
    def test_texto_curto_fica_numa_linha(self):
        self.assertEqual(quebrar_em_linhas("Poucos mortais."), ["Poucos mortais."])

    def test_texto_longo_vira_duas_linhas_equilibradas(self):
        linhas = quebrar_em_linhas("Reza a lenda que cada estacao veste uma Driade diferente")
        self.assertEqual(len(linhas), 2)
        for linha in linhas:
            self.assertLessEqual(len(linha), MAX_CARACTERES_POR_LINHA)
        self.assertLess(abs(len(linhas[0]) - len(linhas[1])), 12)

    def test_nunca_parte_palavra(self):
        texto = "Reza a lenda que cada estacao veste uma Driade diferente"
        self.assertEqual(" ".join(quebrar_em_linhas(texto)), texto)


class TestGeracao(unittest.TestCase):
    def setUp(self):
        self.legendas = gerar(alinhamento_de_teste())

    def test_fala_longa_e_repartida_em_varias_legendas(self):
        da_primeira_fala = [c for c in self.legendas if c.linha_roteiro == 0]
        self.assertGreater(len(da_primeira_fala), 1)

    def test_legenda_nunca_mistura_duas_falas(self):
        for legenda in self.legendas:
            self.assertIsInstance(legenda.linha_roteiro, int)
        self.assertEqual(len({c.linha_roteiro for c in self.legendas}), 2)

    def test_nenhuma_legenda_passa_de_duas_linhas(self):
        for legenda in self.legendas:
            self.assertLessEqual(len(legenda.linhas), 2)
            for linha in legenda.linhas:
                self.assertLessEqual(len(linha), MAX_CARACTERES_POR_LINHA)

    def test_legendas_nao_se_sobrepoem(self):
        for atual, proxima in zip(self.legendas, self.legendas[1:]):
            self.assertLessEqual(atual.t1, proxima.t0 + 0.001)

    def test_nenhuma_legenda_passa_do_teto_de_duracao(self):
        for legenda in self.legendas:
            self.assertLessEqual(legenda.t1 - legenda.t0, DURACAO_MAXIMA + 0.001)

    def test_pontuacao_do_roteiro_sobrevive(self):
        # Recolar tokens com espaço perdia vírgula e ponto final — a legenda
        # tem que sair com a pontuação que o roteiro escreveu.
        texto_todo = " ".join(c.texto for c in self.legendas)
        self.assertIn(",", texto_todo)
        self.assertTrue(texto_todo.rstrip().endswith("."))

    def test_nenhuma_legenda_orfa(self):
        # Encher até o limite e jogar o resto na última criava legenda de uma
        # palavra só piscando na tela.
        for legenda in self.legendas:
            self.assertGreaterEqual(len(legenda.texto.split()), 2)

    def test_fatias_da_mesma_fala_ficam_equilibradas(self):
        da_primeira = [c for c in self.legendas if c.linha_roteiro == 0]
        tamanhos = [len(c.texto) for c in da_primeira]
        self.assertLess(max(tamanhos) - min(tamanhos), 30)

    def test_legenda_curta_ganha_tempo_de_leitura(self):
        # Última fala, curta, com muito silêncio depois: deve esticar.
        ultima = self.legendas[-1]
        self.assertGreaterEqual(ultima.t1 - ultima.t0, 0.9)


class TestSRT(unittest.TestCase):
    def test_formato_de_tempo_e_o_do_srt(self):
        srt = para_srt(gerar(alinhamento_de_teste()))
        self.assertIn(" --> ", srt)
        self.assertRegex(srt, r"\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}")
        self.assertTrue(srt.startswith("1\n"))

    def test_numeracao_sequencial(self):
        legendas = gerar(alinhamento_de_teste())
        self.assertEqual([c.indice for c in legendas], list(range(1, len(legendas) + 1)))


if __name__ == "__main__":
    unittest.main()
