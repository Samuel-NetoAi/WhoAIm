"""Testa a espinha das seis fases — sem disparar Claude Code nenhum.

O que se testa aqui é a DECISÃO: qual fase vem agora, o que já está pronto, e
principalmente o que ele diz sobre uma fase que depende de ferramenta que não
existe. Um painel que mente é pior que não ter painel.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import fases  # noqa: E402


class TestEntendeOPedido(unittest.TestCase):

    def test_reconhece_a_fase_e_a_criatura(self):
        from tools.local_commands import _criatura_da_fase, _fase_pedida

        casos = [
            ("vamos começar a fase 0 da Medusa", 0, "Medusa"),
            ("fase 3 do Cthulhu", 3, "Cthulhu"),
            ("roda a fase zero da Baba Yaga", 0, "Baba Yaga"),
            ("Ômega, quero a fase 2 da Dullhan agora", 2, "Dullhan"),
        ]
        for frase, n, criatura in casos:
            self.assertEqual(_fase_pedida(frase.lower()), n, frase)
            self.assertEqual(_criatura_da_fase(frase), criatura, frase)

    def test_sem_a_palavra_fase_nao_dispara(self):
        """"vamos começar" sozinho é ambíguo com meia dúzia de outras coisas."""
        from tools.local_commands import _fase_pedida

        for frase in ("vamos começar", "começa a aula 2", "0 problemas",
                      "assistir o curso inteiro"):
            self.assertIsNone(_fase_pedida(frase.lower()), frase)

    def test_pode_seguir_nao_colide_com_a_aula(self):
        """"continuar a aula" retoma gravação; "pode continuar" avança fase."""
        from tools.local_commands import _e_retomada_de_aula, _e_seguir

        for frase in ("pode seguir", "segue", "pode continuar", "avança"):
            self.assertTrue(_e_seguir(frase.lower()), frase)
            self.assertFalse(_e_retomada_de_aula(frase.lower()), frase)

        for frase in ("continuar a aula", "retoma a aula", "voltei, pode "
                      "continuar gravando"):
            self.assertTrue(_e_retomada_de_aula(frase.lower()), frase)
            self.assertFalse(_e_seguir(frase.lower()), frase)

    def test_o_modelo_tambem_tem_como(self):
        sys.argv = ["t"]
        import main

        f = next((x for x in main.TOOLS if x["name"] == "fases"), None)
        self.assertIsNotNone(f, "faltou a ferramenta fases")
        self.assertEqual(sorted(f["parameters"]["properties"]["acao"]["enum"]),
                         ["comecar", "seguir", "situacao"])


class TestEstado(unittest.TestCase):

    def setUp(self):
        import tempfile

        from tools import pipeline

        self.tmp = tempfile.TemporaryDirectory()
        self._raiz = fases.AI_PROJECT_ROOT
        self._raiz_pipe = pipeline.AI_PROJECT_ROOT
        fases.AI_PROJECT_ROOT = Path(self.tmp.name)
        pipeline.AI_PROJECT_ROOT = Path(self.tmp.name)
        self.notes = Path(self.tmp.name) / "Criaturas" / "Medusa" / "medusa-video" / "notes"
        self.notes.mkdir(parents=True)

    def tearDown(self):
        import shutil

        from tools import pipeline

        fases.AI_PROJECT_ROOT = self._raiz
        pipeline.AI_PROJECT_ROOT = self._raiz_pipe
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def test_comeca_na_fase_zero(self):
        self.assertEqual(fases.proxima("Medusa"), 0)

    def test_o_arquivo_no_disco_manda_mais_que_o_registro(self):
        """Ele pode ter gerado o dossiê à mão, ou o app pode ter caído antes
        de anotar. Quem diz o que existe é o arquivo."""
        (self.notes / "dossie.md").write_text("x", encoding="utf-8")
        self.assertEqual(fases.proxima("Medusa"), 1)
        self.assertEqual(fases.estado_de("Medusa", 0), fases.NAO_COMECOU)

    def test_estado_sobrevive_ao_fechamento_do_app(self):
        fases.marcar("Medusa", 1, fases.AGUARDANDO, "esperando aprovação")
        self.assertEqual(fases.estado_de("Medusa", 1), fases.AGUARDANDO)
        self.assertTrue((self.notes / "fases.json").exists())

    def test_nao_pula_fase(self):
        r = fases.comecar("Medusa", 2)
        self.assertIn("ainda não terminou", r)
        self.assertIn("fase 1", r)

    def test_fase_sem_ferramenta_NAO_diz_pronta(self):
        """A 3 depende de um MCP que não existe. Dizer 'pronta' seria mentira,
        e mentira de painel custa uma produção parada sem ninguém saber."""
        for n in (0, 1, 2):
            fases.marcar("Medusa", n, fases.PRONTA)
        r = fases.comecar("Medusa", 3)
        self.assertIn("MCP", r)
        self.assertEqual(fases.estado_de("Medusa", 3), fases.AGUARDANDO)
        self.assertNotIn(fases.PRONTA, fases.estado_de("Medusa", 3))

    def test_publicar_continua_sendo_dele(self):
        for n in range(5):
            fases.marcar("Medusa", n, fases.PRONTA)
        r = fases.comecar("Medusa", 5)
        self.assertIn("PARO", r)
        self.assertIn("botão é seu", r)

    def test_anuncia_a_proxima_com_o_que_ela_precisa(self):
        """É esta frase que aposenta a decoreba dos quarenta comandos."""
        r = fases.anunciar("Medusa", 0)
        self.assertIn("fase 1", r)
        self.assertIn("Model sheets", r)
        self.assertIn("pode seguir", r)

    def test_anuncia_o_que_falta_quando_falta(self):
        r = fases.anunciar("Medusa", 2)
        self.assertIn("MCP", r, "não avisou que a fase 3 depende de mim")

    def test_no_fim_nao_inventa_fase_7(self):
        r = fases.anunciar("Medusa", 5)
        self.assertIn("última", r)

    def test_seguir_sem_nome_com_duas_em_curso_pergunta(self):
        (self.notes / "dossie.md").write_text("x", encoding="utf-8")
        outra = (Path(self.tmp.name) / "Criaturas" / "Sobek" / "sobek-video"
                 / "notes")
        outra.mkdir(parents=True)
        (outra / "dossie.md").write_text("x", encoding="utf-8")
        self.assertEqual(sorted(fases.em_andamento()), ["Medusa", "Sobek"])

    def test_situacao_lista_todas(self):
        (self.notes / "dossie.md").write_text("x", encoding="utf-8")
        r = fases.situacao()
        self.assertIn("Medusa", r)
        self.assertIn("fase 1", r)


class TestCursoAgindoSozinho(unittest.TestCase):
    """O curso entra nas fases 0 e 5 — e cala a boca no resto.

    A trava que importa é a mesma de `tools/web.py`: sem fonte, não afirma.
    Um OMEGA que opina de SEO sem regra aprovada, com voz de quem leu o curso,
    é pior que um OMEGA calado — porque o Samuel vai acreditar.
    """

    def setUp(self):
        import tempfile

        from tools import aula as _aula
        from tools import curso as _curso

        from tools import pipeline

        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self._cursos = _aula.CURSOS
        # ISOLAR A RAIZ TAMBÉM. Sem isto o teste lia o estado da Medusa DE
        # VERDADE — e `marcar` teria escrito na pasta real dela.
        self._raiz, self._raiz_pipe = fases.AI_PROJECT_ROOT, pipeline.AI_PROJECT_ROOT
        fases.AI_PROJECT_ROOT = pipeline.AI_PROJECT_ROOT = raiz
        _aula.CURSOS = raiz / "Cursos"
        self.pasta = _aula.CURSOS / _aula.curso_atual()
        self.pasta.mkdir(parents=True)
        (raiz / "Criaturas" / "Medusa" / "medusa-video" / "notes").mkdir(parents=True)
        for n in range(5):
            fases.marcar("Medusa", n, fases.PRONTA)
        self.curso = _curso

    def tearDown(self):
        import shutil

        from tools import aula as _aula

        from tools import pipeline

        _aula.CURSOS = self._cursos
        fases.AI_PROJECT_ROOT = self._raiz
        pipeline.AI_PROJECT_ROOT = self._raiz_pipe
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def _aprovar(self, texto):
        (self.pasta / "regras-aprovadas.md").write_text(texto, encoding="utf-8")

    def test_sem_regra_aprovada_nao_inventa(self):
        self.assertEqual(self.curso.orientar(("titulo",)), "")

    def test_traz_so_as_regras_da_decisao_pedida(self):
        self._aprovar(
            "## Título entre 40 e 60 caracteres\n"
            "- **Decisão:** titulo\n- **Fonte:** aula 1 — [03:20]\n\n"
            "## Poste terça e quinta às 19h\n"
            "- **Decisão:** quando-postar\n- **Fonte:** aula 7 — [11:02]\n")
        material = self.curso.orientar(("titulo",))
        self.assertIn("40 e 60 caracteres", material)
        self.assertNotIn("terça e quinta", material,
                         "trouxe regra de outra decisão; na fase 0 isso é ruído")

    def test_manda_citar_a_fonte(self):
        self._aprovar("## Use número no título\n- **Decisão:** titulo\n"
                      "- **Fonte:** aula 1 — [03:20]\n")
        material = self.curso.orientar(("titulo",))
        self.assertIn("citando a aula e o minuto", material)
        self.assertIn("[03:20]", material)
        self.assertIn("não acrescente conselho seu",
                      material.lower().replace("nao", "não"))

    def test_a_fase_5_puxa_o_pacote_inteiro(self):
        self._aprovar("## Thumb com rosto e contraste\n"
                      "- **Decisão:** thumbnail\n- **Fonte:** aula 9 — [02:03]\n")
        r = fases.comecar("Medusa", 5)
        self.assertIn("Thumb com rosto", r,
                      "a fase 5 é a que mais rende curso; veio sem regra")

    def test_a_fase_5_continua_sem_publicar(self):
        self._aprovar("## Qualquer regra\n- **Decisão:** titulo\n"
                      "- **Fonte:** aula 1 — [00:10]\n")
        r = fases.comecar("Medusa", 5)
        self.assertIn("botão é seu", r)


class TestPipelineAceitaAsFases(unittest.TestCase):
    """As fases 1 e 2 foram separadas — o pipeline precisa conhecer as duas."""

    def test_rotulos_cobrem_as_quatro(self):
        from tools.pipeline import ROTULOS

        for chave in ("pesquisa", "model-sheets", "storyboards", "producao"):
            self.assertIn(chave, ROTULOS)

    def test_cada_fase_promete_arquivo_diferente(self):
        from tools.pipeline import _arquivos_da_fase

        ms = {p.name for p in _arquivos_da_fase("Medusa", "model-sheets")}
        sb = {p.name for p in _arquivos_da_fase("Medusa", "storyboards")}
        self.assertIn("model-sheets.md", ms)
        self.assertIn("prompts.md", sb)
        self.assertNotIn("prompts.md", ms,
                         "a fase 1 não pode prometer os storyboards")

    def test_fase_desconhecida_nao_passa(self):
        from tools.pipeline import pipeline_criatura

        r = pipeline_criatura({"creature": "Medusa", "phase": "inventada"})
        self.assertIn("Não conheço a fase", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
