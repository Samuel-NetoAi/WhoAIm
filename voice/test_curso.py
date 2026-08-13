"""Testa o caminho do curso: regra extraída → aprovada → guiando o SEO.

O ponto de tudo isto é o Samuel poder propor um título e o OMEGA responder
"não, o curso falou o contrário na aula 4". Duas coisas têm que ser verdade
para isso não virar um estorvo:

  1. **Nada vale sem ele aprovar.** Uma frase mal transcrita não pode virar
     estratégia do canal em silêncio — mesma regra do `ensinar`.
  2. **Sem regra aprovada, ele não opina.** É a trava do `web.conferir`
     aplicada aqui, e aqui pesa mais: isto decide o que vai ao ar.

Não toca no curso real nem na skill instalada — tudo em pasta temporária.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import aula, curso  # noqa: E402

REGRAS = """# Regras da aula

## Use número no título quando houver contagem
- **Por quê:** o professor mostrou CTR 40% maior
- **Fonte:** aula-01 — [04:12]
- **Confiança:** alta

## Os primeiros 30 segundos decidem a retenção
- **Por quê:** é onde o YouTube mede se prende
- **Fonte:** aula-01 — [11:05]
- **Confiança:** alta

## Poste sempre às 3 da manhã
- **Por quê:** trecho confuso
- **Fonte:** aula-01 — [19:40]
- **Confiança:** baixa

## Dúvidas
- ficou ambíguo se vale para Shorts
"""


class TelaFalsa:
    def __init__(self):
        self.documentos = []

    def show_document(self, titulo, conteudo):
        self.documentos.append((titulo, conteudo))

    def write_log(self, _m):
        pass


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self._cursos, self._skill = aula.CURSOS, curso.SKILL_WHOIAM
        aula.CURSOS = base / "Cursos"
        curso.SKILL_WHOIAM = base / "skill" / "algoritmo-youtube.md"
        self.pasta = aula.CURSOS / "teste" / "aulas" / "aula-01"
        self.pasta.mkdir(parents=True)
        (self.pasta / "transcricao.md").write_text("x", encoding="utf-8")
        (self.pasta / "regras.md").write_text(REGRAS, encoding="utf-8")
        curso._pendente_de_aprovacao.update({"itens": [], "curso": ""})

    def tearDown(self):
        aula.CURSOS, curso.SKILL_WHOIAM = self._cursos, self._skill
        curso._pendente_de_aprovacao.update({"itens": [], "curso": ""})
        shutil.rmtree(self.tmp.name, ignore_errors=True)


class TestLeituraDasRegras(Base):
    def test_secoes_que_nao_sao_regra_ficam_de_fora(self):
        """'Dúvidas' aprovado como regra vira lixo dentro da skill de SEO."""
        titulos = [b.splitlines()[0][3:] for _, b in curso.propostas("teste")]
        self.assertEqual(len(titulos), 3, titulos)
        self.assertNotIn("Dúvidas", titulos)

    def test_ignora_acento_no_titulo_da_secao(self):
        """O Claude escreve 'Dúvidas'; a transcrição às vezes devolve 'Duvidas'."""
        (self.pasta / "regras.md").write_text(
            "## Uma regra\n- x\n\n## Duvidas\n- y\n", encoding="utf-8")
        self.assertEqual(len(curso.propostas("teste")), 1)


class TestAprovacao(Base):
    def test_nada_vale_antes_de_aprovar(self):
        self.assertIn("NÃO HÁ REGRA APROVADA", curso.avaliar("qualquer título", "teste"))

    def test_revisar_mostra_numerado_com_a_fonte(self):
        ui = TelaFalsa()
        curso.revisar(ui, "teste")
        _titulo, conteudo = ui.documentos[-1]
        self.assertIn("1. Use número", conteudo)
        self.assertIn("[04:12]", conteudo, "sem a fonte ele não pode citar a aula")

    def test_descartada_nao_passa_a_valer(self):
        ui = TelaFalsa()
        curso.revisar(ui, "teste")
        curso.decidir("descartar 3")
        curso.decidir("aprovar todas")
        valendo = (aula.CURSOS / "teste" / "regras-aprovadas.md").read_text(
            encoding="utf-8")
        self.assertIn("Use número", valendo)
        self.assertNotIn("3 da manhã", valendo, "a descartada entrou mesmo assim")

    def test_aprovar_espelha_na_skill_de_seo(self):
        ui = TelaFalsa()
        curso.revisar(ui, "teste")
        curso.decidir("aprovar todas")
        self.assertTrue(curso.SKILL_WHOIAM.exists(), "a skill não recebeu nada")
        texto = curso.SKILL_WHOIAM.read_text(encoding="utf-8")
        self.assertIn("Use número", texto)
        self.assertIn("não republicar", texto, "falta a regra do material comprado")
        self.assertIn("cite a fonte", texto.lower())

    def test_confianca_baixa_nao_entra_por_atacado(self):
        """A extração marca "baixa" quando o trecho estava confuso.

        Aprovar essas de enfiada é como o defeito entra: uma frase mal ouvida
        vira regra do canal, e depois o OMEGA a cita com a autoridade de "o
        curso disse". O gesto largo é que se barra — por número ele aprova.
        """
        ui = TelaFalsa()
        curso.revisar(ui, "teste")
        r = curso.decidir("aprovar todas")
        self.assertIn("confiança BAIXA de fora", r)
        self.assertNotIn("baixa", curso.SKILL_WHOIAM.read_text(encoding="utf-8"))

    def test_por_numero_ele_ainda_manda(self):
        """Barrar o atacado não é tirar a decisão dele."""
        ui = TelaFalsa()
        curso.revisar(ui, "teste")
        itens = curso._pendente_de_aprovacao["itens"]
        i = next(n for n, (_, b) in enumerate(itens, 1)
                 if "baixa" in b.lower())
        curso.decidir(f"aprovar {i}")
        self.assertIn("baixa",
                      curso.SKILL_WHOIAM.read_text(encoding="utf-8").lower())

    def test_nao_repete_o_que_ja_foi_aprovado(self):
        ui = TelaFalsa()
        curso.revisar(ui, "teste")
        curso.decidir("aprovar todas")
        sobrou = curso.revisar(ui, "teste")
        # Sobra só a de confiança baixa, que o atacado deixou de fora.
        self.assertNotIn("Use número", sobrou)

    def test_decidir_sem_revisar_antes(self):
        self.assertIn("revisar regras", curso.decidir("aprovar todas"))

    def test_pedido_vago_pede_precisao(self):
        curso.revisar(TelaFalsa(), "teste")
        self.assertIn("Diga quais", curso.decidir("aprovar"))


class TestAvaliacao(Base):
    def _aprovar_tudo(self):
        curso.revisar(TelaFalsa(), "teste")
        curso.decidir("aprovar todas")

    def test_entrega_as_regras_e_a_proposta(self):
        self._aprovar_tudo()
        r = curso.avaliar("Medusa: a verdade sobre a gorgona", "teste")
        self.assertIn("Use número", r, "não mandou as regras para comparar")
        self.assertIn("Medusa: a verdade", r, "não mandou a proposta")
        self.assertIn("[04:12]", r, "sem a fonte ele não cita a aula")

    def test_manda_citar_a_fonte_e_nao_inventar(self):
        self._aprovar_tudo()
        r = curso.avaliar("Um título qualquer", "teste").lower()
        self.assertIn("citando a aula", r)
        self.assertIn("não falou disso", r)

    def test_proposta_vazia(self):
        self.assertIn("o quê", curso.avaliar("", "teste").lower())


class TestFila(Base):
    def test_aula_transcrita_sem_regras_entra_na_fila(self):
        (self.pasta / "regras.md").unlink()
        self.assertEqual([p.name for p in curso.sem_regras("teste")], ["aula-01"])

    def test_aula_sem_audio_nao_e_pendente(self):
        self.assertEqual(curso.pendentes("teste"), [])




class TestAprovarPorDecisao(unittest.TestCase):
    """São 38 aulas e mais de quinhentas regras.

    Aprovar de uma em uma, por número, é trabalho que ninguém termina — e
    trabalho que não se termina vira regra nenhuma valendo, ou seja, o curso
    inteiro desperdiçado. Por isso "aprovar tudo de título".
    """

    def setUp(self):
        import tempfile

        from tools import aula as _aula

        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self._cursos, self._skill = _aula.CURSOS, curso.SKILL_WHOIAM
        # A SKILL REAL FICA FORA DISTO. Um teste meu já gravou regras
        # inventadas em ~/.claude/skills/whoiam/references/algoritmo-youtube.md,
        # e a `whoiam` teria passado a gerar SEO com base em regra que nunca
        # existiu — mentira com cara de curso, que é o pior desfecho possível.
        _aula.CURSOS = raiz / "Cursos"
        curso.SKILL_WHOIAM = raiz / "skill" / "algoritmo-youtube.md"
        (_aula.CURSOS / _aula.curso_atual()).mkdir(parents=True)

        def regra(titulo, decisao):
            return (f"## {titulo}\n- **Decisão:** {decisao}\n"
                    "- **Fonte:** aula 1 — [01:00]\n- **Confiança:** alta")

        self.itens = [(None, regra("Título com número", "titulo")),
                      (None, regra("Título curto", "titulo")),
                      (None, regra("Thumb com rosto", "thumbnail")),
                      (None, regra("Poste 19h", "quando-postar"))]
        curso._pendente_de_aprovacao.update(
            {"itens": list(self.itens), "curso": _aula.curso_atual()})

    def tearDown(self):
        import shutil

        from tools import aula as _aula

        _aula.CURSOS, curso.SKILL_WHOIAM = self._cursos, self._skill
        curso._pendente_de_aprovacao.update({"itens": [], "curso": ""})
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def test_aprova_um_assunto_inteiro_de_uma_vez(self):
        r = curso.decidir("aprovar tudo de título")
        self.assertIn("2 regra(s) de titulo", r)
        aprovadas = curso.SKILL_WHOIAM.read_text(encoding="utf-8")
        self.assertIn("Título com número", aprovadas)
        self.assertNotIn("Thumb com rosto", aprovadas,
                         "aprovou regra de outro assunto")

    def test_diz_o_que_sobrou_por_assunto(self):
        """"restam 47" não ajuda ninguém; "thumbnail (12), tags (4)" ajuda."""
        r = curso.decidir("aprovar tudo de título")
        self.assertIn("thumbnail (1)", r)
        self.assertIn("quando-postar (1)", r)

    def test_assunto_que_nao_esta_na_fila_nao_apaga_nada(self):
        r = curso.decidir("descartar tudo de canal")
        self.assertIn("Nenhuma", r)
        self.assertEqual(len(curso._pendente_de_aprovacao["itens"]), 4)

    def test_descartar_um_assunto_nao_leva_os_outros(self):
        curso.decidir("descartar tudo de título")
        sobrou = curso._pendente_de_aprovacao["itens"]
        self.assertEqual(len(sobrou), 2)
        self.assertFalse(curso.SKILL_WHOIAM.exists(),
                         "descartar não pode escrever na skill")

    def test_numero_continua_valendo(self):
        curso.decidir("aprovar 3")
        self.assertIn("Thumb com rosto",
                      curso.SKILL_WHOIAM.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
