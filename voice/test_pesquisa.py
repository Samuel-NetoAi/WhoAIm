"""Testa o caminho "mande o OMEGA pesquisar uma criatura" — sem áudio.

Duas rotas levam ao Claude Code, e as duas precisavam de conserto:

1. comando digitado (`pesquisar Quimera`) — funciona sem crédito e sem internet;
2. fala/texto livre no motor GRATUITO — o Gemini precisa poder CHAMAR a
   ferramenta. Antes ele não recebia ferramenta nenhuma e respondia como se
   tivesse executado.

Rodar: .venv/bin/python -m unittest test_pesquisa -v
"""

from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from tools import local_commands


class FakeUI:
    """O mínimo que as duas rotas tocam."""

    def __init__(self):
        self.exibido: tuple[str, str] | None = None
        self.log: list[str] = []
        self.on_text_command = None
        self.muted = False

    def show_document(self, titulo, texto):
        self.exibido = (titulo, texto)

    def show_video(self, titulo, caminho):
        self.exibido = (titulo, caminho)

    def show_hud(self):
        self.exibido = ("hud", "")

    def write_log(self, texto):
        self.log.append(texto)

    def set_state(self, estado):
        pass


class TestComandosDigitados(unittest.TestCase):
    def setUp(self):
        self.ui = FakeUI()

    def test_pesquisar_dispara_o_pipeline(self):
        with patch.object(local_commands, "pipeline_criatura") as pipeline:
            pipeline.return_value = "Iniciei a pesquisa."
            resposta = local_commands.handle("pesquisar Quimera", self.ui)

        pipeline.assert_called_once_with(
            {"action": "start", "creature": "Quimera", "phase": "pesquisa"}
        )
        self.assertEqual(resposta, "Iniciei a pesquisa.")

    def test_produzir_dispara_a_fase_de_producao(self):
        with patch.object(local_commands, "pipeline_criatura") as pipeline:
            local_commands.handle("produzir Quimera", self.ui)
        pipeline.assert_called_once_with(
            {"action": "start", "creature": "Quimera", "phase": "producao"}
        )

    def test_pipeline_sozinho_consulta_andamento(self):
        with patch.object(local_commands, "pipeline_criatura") as pipeline:
            local_commands.handle("pipeline", self.ui)
        pipeline.assert_called_once_with({"action": "status"})

    def test_substantivo_le_e_verbo_age(self):
        """A distinção que faltava: `dossie X` mostra, `pesquisar X` produz.

        Antes, "pesquisa X" caía no leitor de notas e devolvia "ainda não
        existe dossiê" — parecendo que a pesquisa falhou, quando ela nunca
        tinha sido disparada.
        """
        with patch.object(local_commands, "pipeline_criatura") as pipeline:
            local_commands.handle("dossie Quimera", self.ui)
        pipeline.assert_not_called()

    def test_nome_com_espaco_chega_inteiro(self):
        with patch.object(local_commands, "pipeline_criatura") as pipeline:
            local_commands.handle("pesquisar Baba Yaga", self.ui)
        self.assertEqual(pipeline.call_args[0][0]["creature"], "Baba Yaga")

    def test_texto_desconhecido_continua_indo_para_o_modelo(self):
        self.assertIsNone(
            local_commands.handle("me conta uma piada sobre grifos", self.ui)
        )


class TestGuardasDoPipeline(unittest.TestCase):
    """O pipeline real: recusa cedo, com frase, em vez de falhar no meio."""

    def setUp(self):
        from tools import pipeline

        self.pipeline = pipeline

    def test_sem_cli_avisa_e_nao_dispara(self):
        with patch.object(self.pipeline, "_resolver_claude", return_value=None):
            resposta = self.pipeline.pipeline_criatura(
                {"action": "start", "creature": "Quimera"}
            )
        self.assertIn("não está instalado", resposta)
        self.assertFalse(self.pipeline._current["running"])

    def test_sem_pasta_de_projetos_avisa(self):
        with patch.object(self.pipeline, "_resolver_claude", return_value="/bin/true"), \
            patch.object(self.pipeline, "AI_PROJECT_ROOT", Path("/nao/existe/mesmo")):
            resposta = self.pipeline.pipeline_criatura(
                {"action": "start", "creature": "Quimera"}
            )
        self.assertIn("não existe", resposta)
        self.assertFalse(self.pipeline._current["running"])

    def test_shell_so_no_windows(self):
        """No POSIX, shell=True com lista descartaria o prompt.

        `sh -c "claude"` ignora os argumentos seguintes, então o Claude abriria
        em modo interativo e ficaria travado até o timeout de 30 minutos.
        """
        import platform

        self.assertEqual(self.pipeline.E_WINDOWS, platform.system() == "Windows")

    def test_raiz_vem_da_variavel_de_ambiente(self):
        import importlib
        import os

        with patch.dict(os.environ, {"AI_PROJECT_ROOT": "/tmp/raiz-de-teste"}):
            recarregado = importlib.reload(self.pipeline)
            self.assertEqual(str(recarregado.AI_PROJECT_ROOT), "/tmp/raiz-de-teste")
        importlib.reload(self.pipeline)


class TestDiagnostico(unittest.TestCase):
    def test_relata_cada_peca_e_conta_as_que_faltam(self):
        titulo, doc, resumo = local_commands._diagnostico()
        self.assertEqual(titulo, "diagnóstico")
        for peca in ("Pasta dos projetos", "Claude Code CLI", "Alpha Studio"):
            self.assertIn(peca, doc)
        # Nesta máquina falta pelo menos o CLI, então tem que dizer isso.
        self.assertTrue(
            "faltando" in resumo or "tudo pronto" in resumo.lower(), resumo
        )


class TestFerramentasNoMotorGratuito(unittest.TestCase):
    """O Gemini precisa RECEBER as ferramentas e ter o resultado devolvido."""

    def setUp(self):
        from free_engine import FreeEngine

        self.ui = FakeUI()
        self.executadas: list[tuple[str, dict]] = []

        def executor(nome, args):
            self.executadas.append((nome, args))
            return "Iniciei a fase de pesquisa e dossiê da criatura Quimera."

        self.engine = FreeEngine(
            gemini_key="x",
            instructions="...",
            tool_executor=executor,
            ui=self.ui,
            local_handler=None,
            tools=[
                {
                    "type": "function",
                    "name": "pipeline_criatura",
                    "description": "Dispara o Claude Code.",
                    "parameters": {
                        "type": "object",
                        "properties": {"creature": {"type": "string"}},
                        "required": ["creature"],
                    },
                }
            ],
        )

    def test_declaracoes_perdem_o_type_da_openai(self):
        declaracoes = self.engine._declaracoes()
        self.assertEqual(len(declaracoes), 1)
        self.assertNotIn("type", declaracoes[0])
        self.assertEqual(
            set(declaracoes[0]), {"name", "description", "parameters"}
        )

    def test_ferramenta_pedida_pelo_modelo_e_de_fato_executada(self):
        respostas = [
            {
                "candidates": [
                    {
                        "content": {
                            "role": "model",
                            "parts": [
                                {
                                    "functionCall": {
                                        "name": "pipeline_criatura",
                                        "args": {"creature": "Quimera"},
                                    }
                                }
                            ],
                        }
                    }
                ]
            },
            {
                "candidates": [
                    {
                        "content": {
                            "parts": [{"text": "Pesquisa iniciada, senhor."}]
                        }
                    }
                ]
            },
        ]
        with patch.object(self.engine, "_chamar_gemini", side_effect=respostas):
            resposta = self.engine._perguntar_gemini("pesquisa a Quimera")

        self.assertEqual(self.executadas, [("pipeline_criatura", {"creature": "Quimera"})])
        self.assertEqual(resposta, "Pesquisa iniciada, senhor.")

    def test_resultado_da_ferramenta_volta_para_o_modelo(self):
        enviados: list[list[dict]] = []

        def espiao(contents):
            enviados.append([dict(c) for c in contents])
            if len(enviados) == 1:
                return {
                    "candidates": [
                        {
                            "content": {
                                "parts": [
                                    {
                                        "functionCall": {
                                            "name": "pipeline_criatura",
                                            "args": {"creature": "Quimera"},
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            return {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}

        with patch.object(self.engine, "_chamar_gemini", side_effect=espiao):
            self.engine._perguntar_gemini("pesquisa a Quimera")

        # A segunda chamada tem que carregar o functionResponse, senão o modelo
        # responde no vazio sem saber o que a ferramenta devolveu.
        segunda = enviados[1]
        resposta_de_ferramenta = segunda[-1]["parts"][0]["functionResponse"]
        self.assertEqual(resposta_de_ferramenta["name"], "pipeline_criatura")
        self.assertIn("Quimera", resposta_de_ferramenta["response"]["result"])

    def test_sem_ferramenta_pedida_devolve_o_texto(self):
        resposta_simples = {
            "candidates": [{"content": {"parts": [{"text": "Bom dia, senhor."}]}}]
        }
        with patch.object(self.engine, "_chamar_gemini", return_value=resposta_simples):
            self.assertEqual(
                self.engine._perguntar_gemini("bom dia"), "Bom dia, senhor."
            )
        self.assertEqual(self.executadas, [])

    def test_looping_de_ferramentas_tem_fim(self):
        sempre_chamando = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "functionCall": {
                                    "name": "pipeline_criatura",
                                    "args": {"creature": "Quimera"},
                                }
                            }
                        ]
                    }
                }
            ]
        }
        with patch.object(self.engine, "_chamar_gemini", return_value=sempre_chamando):
            resposta = self.engine._perguntar_gemini("pesquisa")
        self.assertIn("looping", resposta.lower())
        self.assertLessEqual(len(self.executadas), 3)


if __name__ == "__main__":
    unittest.main()
