"""Testa o que quebrou no uso real: pedir para NARRAR virava gerar roteiro.

O Samuel disse "quero que você narre a pesquisa do Pennywise" e o OMEGA
respondeu que não sabia narrar documentos e disparou a produção do roteiro.
Duas causas somadas, e nenhuma delas era erro dele:

  1. a instrução de sistema dizia, com todas as letras, "NUNCA leia um
     documento inteiro em voz alta" — escrita antes de a leitura existir.
     Ele estava obedecendo.
  2. `ler`/`narrar` só existiam como comando DIGITADO. No motor Live o áudio
     vai direto ao modelo sem passar pelos comandos locais, então a
     capacidade simplesmente não estava ao alcance dele.

O terceiro problema apareceu na sequência: ele disparou uma produção de
minutos e, quando o Samuel disse "não precisa", respondeu que não dava para
parar. Era verdade — e é o tipo de coisa que não pode ser verdade.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

sys.argv = ["test"]
import main  # noqa: E402
from tools import leitura, pipeline  # noqa: E402


class UIFalsa:
    muted = False

    def __init__(self):
        self.log = []
        self.falas = []
        self.documentos = []

    def write_log(self, m):
        self.log.append(m)

    def set_state(self, *_):
        pass

    def show_document(self, t, c):
        self.documentos.append(t)

    def falar(self, texto, economico=False):
        self.falas.append(("modelo", economico))

    def falar_leitura(self, texto, economico=True):
        self.falas.append(("local", economico))


class TestInstrucao(unittest.TestCase):
    def test_nao_proibe_mais_ler_em_voz_alta(self):
        self.assertNotIn("nunca leia um documento inteiro em voz alta",
                         main.INSTRUCTIONS)

    def test_avisa_para_nao_confundir_ler_com_produzir(self):
        # Espaços normalizados: a instrução é quebrada em linhas, e o teste
        # não pode depender de onde cai a quebra.
        i = " ".join(main.INSTRUCTIONS.lower().split())
        self.assertIn("jamais gerar roteiro novo", i)

    def test_avisa_que_produzir_custa(self):
        self.assertIn("créditos", main.INSTRUCTIONS)


class TestFerramentas(unittest.TestCase):
    def nomes(self):
        return [t["name"] for t in main.TOOLS]

    def test_o_modelo_de_voz_tem_como_ler(self):
        self.assertIn("ler", self.nomes())
        self.assertIn("parar_leitura", self.nomes())

    def test_ler_deixa_escolher_a_voz(self):
        ferramenta = next(t for t in main.TOOLS if t["name"] == "ler")
        vozes = ferramenta["parameters"]["properties"]["voz"]["enum"]
        self.assertEqual(sorted(vozes), ["boa", "comum"])

    def test_pipeline_pode_ser_cancelado(self):
        p = next(t for t in main.TOOLS if t["name"] == "pipeline_criatura")
        self.assertIn("cancelar", p["parameters"]["properties"]["action"]["enum"])

    def test_narrar_pede_a_voz_boa(self):
        """'voz=boa' tem que virar o verbo 'narrar', não 'ler'."""
        vistos = []
        ui = UIFalsa()
        original = main._local
        try:
            main._local = lambda texto, _ui: vistos.append(texto) or "ok"
            executor = main.make_tool_executor(ui)
            executor("ler", {"criatura": "Medusa", "voz": "boa"})
            executor("ler", {"criatura": "Medusa", "voz": "comum"})
        finally:
            main._local = original
        self.assertTrue(vistos[0].startswith("narrar"), vistos[0])
        self.assertTrue(vistos[1].startswith("ler"), vistos[1])


class TestLeituraNoLive(unittest.TestCase):
    """No Live, ler NÃO pode passar pelo modelo."""

    def tearDown(self):
        leitura.parar()
        leitura._pendente.clear()

    def test_usa_a_voz_da_maquina_e_nao_o_modelo(self):
        ui = UIFalsa()
        leitura.ler("teste", "Uma frase curta apenas.", ui)
        import time

        time.sleep(0.4)
        self.assertTrue(ui.falas, "não falou nada")
        self.assertEqual(ui.falas[0][0], "local",
                         "mandou o documento para o MODELO dizer — queimaria a "
                         "cota e ele resumiria em vez de ler")

    def test_sem_o_gancho_usa_falar_normal(self):
        """O motor local não define falar_leitura e tem que continuar valendo."""
        # Classe própria, e não subclasse de UIFalsa: apagar o método na
        # subclasse não some com o herdado, e o teste passava por acidente.
        class SemGancho:
            muted = False

            def __init__(self):
                self.falas = []

            def write_log(self, m):
                pass

            def falar(self, texto, economico=False):
                self.falas.append(("modelo", economico))

        ui = SemGancho()
        leitura.ler("teste", "Outra frase curta.", ui)
        import time

        time.sleep(0.4)
        self.assertEqual(ui.falas[0][0], "modelo")


class TestCancelamento(unittest.TestCase):
    def setUp(self):
        self._estado = dict(pipeline._current)

    def tearDown(self):
        pipeline._current.clear()
        pipeline._current.update(self._estado)

    def test_sem_nada_rodando(self):
        pipeline._current.update({"running": False})
        self.assertIn("Não há nada", pipeline.cancelar())

    def test_marca_para_abortar_antes_de_o_processo_abrir(self):
        pipeline._current.update({"running": True, "creature": "IT A Coisa",
                                  "proc": None, "cancelado": False})
        r = pipeline.cancelar()
        self.assertIn("IT A Coisa", r)
        self.assertTrue(pipeline._current["cancelado"])

    def test_mata_o_processo_e_os_filhos(self):
        mortos = []

        class ProcFalso:
            pid = 4242

            def terminate(self):
                mortos.append("terminate")

        original = pipeline.subprocess.run
        try:
            pipeline.subprocess.run = lambda *a, **k: mortos.append(a[0])
            pipeline._current.update({"running": True, "creature": "X",
                                      "proc": ProcFalso(), "cancelado": False})
            pipeline.cancelar()
        finally:
            pipeline.subprocess.run = original

        if pipeline.E_WINDOWS:
            self.assertIn("/T", mortos[0],
                          "sem /T os filhos seguem rodando e gastando créditos")
            self.assertIn("4242", mortos[0])
        else:
            self.assertIn("terminate", mortos)

    def test_cancelado_nao_e_relatado_como_concluido(self):
        """O ponto de integração: mataram o processo no meio.

        Sem isto o `_run_claude` seguiria o caminho normal e, como o Claude
        morto devolve código != 0, o Samuel ouviria "terminou com erro" em vez
        de "cancelei" — o que faria parecer defeito o que foi obediência.
        """
        import tempfile
        from unittest.mock import patch

        class Proc:
            pid = 1
            returncode = 1

            def communicate(self, timeout=None):
                return "", "morto"

        with tempfile.TemporaryDirectory() as tmp, \
                patch.object(pipeline, "AI_PROJECT_ROOT", Path(tmp)), \
                patch.object(pipeline, "_resolver_claude", return_value="/bin/true"), \
                patch.object(pipeline.subprocess, "Popen",
                             side_effect=lambda *a, **k: Proc()), \
                patch.object(pipeline, "notificar", lambda *a, **k: None), \
                patch.object(pipeline, "batimento", lambda *a, **k: None):
            pipeline._current.update({"running": True, "creature": "IT A Coisa",
                                      "result": None, "proc": None,
                                      "cancelado": True})
            pipeline._run_claude("IT A Coisa", "producao")

        resultado = pipeline._current["result"]
        self.assertIn("Cancelei", resultado)
        self.assertNotIn("erro", resultado.lower())
        self.assertFalse(pipeline._current["running"])

    def test_o_comando_digitado_tambem_cancela(self):
        from tools import local_commands

        pipeline._current.update({"running": True, "creature": "IT A Coisa",
                                  "proc": None, "cancelado": False})
        r = local_commands.handle("cancelar pesquisa", UIFalsa())
        self.assertIsNotNone(r)
        self.assertIn("IT A Coisa", r)


if __name__ == "__main__":
    unittest.main(verbosity=2)
