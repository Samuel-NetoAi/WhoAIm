"""Testes do parser de roteiro, escritos contra os DOIS formatos reais do canal."""

import unittest

from alpha_align.roteiro import carregar

# Formato Dullahan: cabeçalhos com faixa de blocos, preâmbulo de produção.
DULLAHAN = """# Documento 1 — Roteiro de Narração — Dullahan

Estrutura: 19 blocos (~15s cada). Cabeçalhos de bloco são notas de produção —
não entram na versão final de colagem no ElevenLabs.

---

**[Blocos 1 — abertura / mundo]**
Há uma terra onde o verde termina em penhasco...
e o penhasco termina no mar.

**[Blocos 2-3 — origem, registro de lenda]**
Contam que houve um povo que dançava para agradecer a colheita...
Só sobrou o costume.

**[Bloco 4 — o padre]**
Depois veio quem não temia o altar...
"""

# Formato Dríade: sem cabeçalho, parágrafos separados por linha em branco.
DRIADE = """# Documento 1 — Roteiro de Narração (Dríade)

Narração dissociada: a voz narra apenas a lore da Dríade.

---

Há florestas que ainda guardam seus próprios olhos.

Não os olhos dos animais... nem dos homens.

Chamam-nas de Dríades.
Ninfas nascidas do bosque, não de uma árvore só.
"""


class TestCabecalhos(unittest.TestCase):
    def setUp(self):
        self.roteiro = carregar(DULLAHAN, e_texto=True)

    def test_reconhece_blocos_e_faixas(self):
        self.assertEqual(self.roteiro.origem, "cabecalhos")
        self.assertEqual(len(self.roteiro.blocos), 3)
        self.assertEqual([b.numero for b in self.roteiro.blocos], [1, 2, 4])

    def test_faixa_de_blocos_registra_quantos_clipes_cobre(self):
        # "[Blocos 2-3]" é um grupo de falas para DOIS clipes de 15s.
        self.assertEqual([b.abrange for b in self.roteiro.blocos], [1, 2, 1])
        self.assertEqual(sum(b.abrange for b in self.roteiro.blocos), 4)

    def test_preambulo_de_producao_nao_e_narrado(self):
        todo_o_texto = " ".join(l.texto for l in self.roteiro.linhas)
        self.assertNotIn("ElevenLabs", todo_o_texto)
        self.assertNotIn("19 blocos", todo_o_texto)

    def test_linhas_apontam_para_o_bloco_certo(self):
        self.assertEqual(len(self.roteiro.linhas), 5)
        self.assertEqual([l.bloco for l in self.roteiro.linhas], [0, 0, 1, 1, 2])

    def test_reticencias_nao_viram_palavra(self):
        primeira = self.roteiro.linhas[0]
        self.assertEqual(primeira.tokens[-1].chave, "penhasco")


class TestParagrafos(unittest.TestCase):
    def setUp(self):
        self.roteiro = carregar(DRIADE, e_texto=True)

    def test_sem_cabecalho_cada_paragrafo_e_um_bloco(self):
        self.assertEqual(self.roteiro.origem, "paragrafos")
        self.assertEqual(len(self.roteiro.blocos), 3)

    def test_paragrafo_de_duas_falas_fica_num_bloco_so(self):
        ultimo = self.roteiro.blocos[-1]
        self.assertEqual(len(ultimo.linhas), 2)

    def test_hifen_de_enclise_vira_duas_chaves(self):
        # "Chamam-nas" — o ASR devolve as duas partes separadas.
        chaves = [t.chave for t in self.roteiro.linhas[2].tokens]
        self.assertEqual(chaves[:3], ["chamam", "nas", "de"])


class TestBlocoVazio(unittest.TestCase):
    def test_cabecalho_sem_fala_some_e_indices_continuam_certos(self):
        roteiro = carregar(
            "---\n**[Bloco 1 — nota]**\n\n**[Bloco 2 — real]**\nUma fala qualquer.\n",
            e_texto=True,
        )
        self.assertEqual(len(roteiro.blocos), 1)
        self.assertEqual(roteiro.blocos[0].numero, 2)
        self.assertEqual(roteiro.linhas[0].bloco, 0)


if __name__ == "__main__":
    unittest.main()
