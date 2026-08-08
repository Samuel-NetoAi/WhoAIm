"""Testa o canal de aviso ATIVO — o OMEGA falando sem ser perguntado.

Antes, pesquisa e render rodavam em silêncio por minutos e só respondiam a
"status". Estes testes cobrem o que passou a avisar sozinho, e principalmente
os casos em que ele NÃO pode dizer que deu certo.

Rodar: .venv/bin/python -m unittest test_avisos -v
"""

from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from tools import notify


class ColetorDeAvisos:
    """Captura o que seria dito na janela."""

    def __init__(self):
        self.mensagens: list[tuple[str, bool]] = []

    def __call__(self, texto: str, *, falar: bool) -> None:
        self.mensagens.append((texto, falar))

    @property
    def textos(self) -> list[str]:
        return [t for t, _ in self.mensagens]

    @property
    def falados(self) -> list[str]:
        return [t for t, falar in self.mensagens if falar]


class TestCanal(unittest.TestCase):
    def setUp(self):
        self.coletor = ColetorDeAvisos()
        notify.definir_notificador(self.coletor)
        self.addCleanup(notify.definir_notificador, None)

    def test_sem_notificador_nao_quebra(self):
        notify.definir_notificador(None)
        notify.notificar("ninguém está ouvindo")  # não deve levantar

    def test_notificador_que_falha_nao_derruba_a_tarefa(self):
        def explode(texto, *, falar):
            raise RuntimeError("janela fechada")

        notify.definir_notificador(explode)
        notify.notificar("mensagem")  # o aviso falha, a tarefa segue

    def test_duracao_em_portugues_falavel(self):
        self.assertEqual(notify.duracao_falada(40), "40 segundos")
        self.assertEqual(notify.duracao_falada(100), "1 minuto e meio")
        self.assertEqual(notify.duracao_falada(300), "5 minutos")

    def test_batimento_avisa_enquanto_a_tarefa_vive(self):
        rodando = {"v": True}
        notify.batimento(
            0.05,
            lambda d: f"ainda rodando ({d:.2f}s)",
            lambda: rodando["v"],
        )
        time.sleep(0.3)
        rodando["v"] = False
        time.sleep(0.1)

        self.assertGreaterEqual(len(self.coletor.textos), 2)
        self.assertTrue(all("ainda rodando" in t for t in self.coletor.textos))
        # Batimento é ruído se falado: fica só no log.
        self.assertEqual(self.coletor.falados, [])

    def test_batimento_para_quando_a_tarefa_acaba(self):
        rodando = {"v": True}
        notify.batimento(0.05, lambda d: "tic", lambda: rodando["v"])
        time.sleep(0.15)
        rodando["v"] = False
        time.sleep(0.15)
        quantos = len(self.coletor.textos)
        time.sleep(0.2)
        self.assertEqual(len(self.coletor.textos), quantos)


class TestAvisoDaPesquisa(unittest.TestCase):
    """O aviso final da pesquisa precisa refletir o que REALMENTE foi gravado."""

    def setUp(self):
        from tools import pipeline

        self.pipeline = pipeline
        self.coletor = ColetorDeAvisos()
        notify.definir_notificador(self.coletor)
        self.addCleanup(notify.definir_notificador, None)

        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.raiz = Path(self.tmp.name)

    def _rodar(self, returncode=0, escrever=None):
        # Popen, não run: o pipeline passou a usar Popen para poder CANCELAR
        # o trabalho no meio (antes o Samuel pedia para parar e o OMEGA
        # respondia, com razão, que não dava). `communicate()` é o que devolve
        # a saída agora.
        class Proc:
            pid = 1234

            def __init__(self):
                self.returncode = returncode

            def communicate(self, timeout=None):
                if escrever:
                    for caminho in escrever:
                        caminho.parent.mkdir(parents=True, exist_ok=True)
                        caminho.write_text("conteúdo", encoding="utf-8")
                return "", ""

        with patch.object(self.pipeline, "AI_PROJECT_ROOT", self.raiz), patch.object(
            self.pipeline, "_resolver_claude", return_value="/bin/true"
        ), patch.object(self.pipeline.subprocess, "Popen",
                        side_effect=lambda *a, **k: Proc()):
            self.pipeline._current.update(
                {"running": True, "creature": "Quimera", "result": None,
                 "proc": None, "cancelado": False}
            )
            self.pipeline._run_claude("Quimera", "pesquisa")

    def test_sucesso_avisa_falando_e_nomeia_o_arquivo(self):
        dossie = (
            self.raiz / "Criaturas" / "Quimera" / "quimera-video" / "notes" / "dossie.md"
        )
        self._rodar(returncode=0, escrever=[dossie])

        self.assertEqual(len(self.coletor.falados), 1)
        aviso = self.coletor.falados[0]
        self.assertIn("Quimera", aviso)
        self.assertIn("dossie.md", aviso)
        self.assertIn("Studio", aviso)

    def test_sucesso_sem_arquivo_nao_diz_que_deu_certo(self):
        """Código 0 sem arquivo é o caso traiçoeiro: parece sucesso e não é.

        Só se descobriria abrindo a aba Notas e achando-a vazia.
        """
        self._rodar(returncode=0, escrever=None)

        aviso = self.coletor.falados[0]
        self.assertIn("não encontrei", aviso)
        self.assertNotIn("Gravei", aviso)

    def test_erro_avisa_falando(self):
        self._rodar(returncode=1, escrever=None)
        self.assertIn("erro", self.coletor.falados[0].lower())

    def test_termina_sempre_liberando_o_pipeline(self):
        self._rodar(returncode=1)
        self.assertFalse(self.pipeline._current["running"])


class TestAvisoDoRender(unittest.TestCase):
    def setUp(self):
        from tools import studio

        self.studio = studio
        self.coletor = ColetorDeAvisos()
        notify.definir_notificador(self.coletor)
        self.addCleanup(notify.definir_notificador, None)
        self.studio._vigiando.clear()

    def _vigiar(self, estados):
        """Roda a vigia com uma sequência de respostas do Studio."""

        class Resposta:
            def __init__(self, job):
                self.ok = True
                self._job = job

            def json(self):
                return {"job": self._job}

        respostas = [Resposta(e) for e in estados]

        with patch.object(self.studio, "INTERVALO_VIGIA", 0.01), patch.object(
            self.studio.requests, "get", side_effect=respostas
        ):
            self.studio._acompanhar_render("pid", "job1", "Medusa", "full")
            for _ in range(200):
                if not self.studio._vigiando:
                    break
                time.sleep(0.01)

    def test_avisa_progresso_e_fala_ao_ficar_pronto(self):
        self._vigiar(
            [
                {"status": "rendering", "progress": 0.3},
                {"status": "rendering", "progress": 0.8},
                {"status": "done", "outputPath": "/x/renders/full-medusa.mp4"},
            ]
        )
        progresso = [t for t, falar in self.coletor.mensagens if not falar]
        self.assertTrue(any("30 por cento" in t for t in progresso))
        self.assertTrue(any("80 por cento" in t for t in progresso))

        self.assertEqual(len(self.coletor.falados), 1)
        self.assertIn("full-medusa.mp4", self.coletor.falados[0])

    def test_render_rapido_nao_despeja_todas_as_faixas(self):
        """Pular de 0 a 90% não deve gerar 25/50/75 de uma vez."""
        self._vigiar(
            [
                {"status": "rendering", "progress": 0.9},
                {"status": "done", "outputPath": "/x/renders/full.mp4"},
            ]
        )
        progresso = [t for t, falar in self.coletor.mensagens if not falar]
        self.assertEqual(len(progresso), 1)

    def test_falha_do_render_e_falada(self):
        self._vigiar([{"status": "error", "error": "ffmpeg morreu"}])
        self.assertIn("falhou", self.coletor.falados[0])
        self.assertIn("ffmpeg", self.coletor.falados[0])

    def test_nao_abre_duas_vigias_do_mesmo_job(self):
        self.studio._vigiando.add("job1")
        with patch.object(self.studio.requests, "get") as get:
            self.studio._acompanhar_render("pid", "job1", "Medusa", "full")
            time.sleep(0.05)
        get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
