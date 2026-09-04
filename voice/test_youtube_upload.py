"""Testa o upload do YouTube — com atenção especial às regras de segurança.

Mesma filosofia do test_navegador.py: o que mais importa não é funcionar, é
nunca subir como público sozinho e nunca tocar em senha. Estes testes não
sobem vídeo de verdade (não dependem de rede nem de token válido) e rodam
sempre.

    python test_youtube_upload.py
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import youtube_upload as yt  # noqa: E402


class TestRegrasDeSeguranca(unittest.TestCase):
    """As regras herdadas do navegador.py — não se negociam aqui também."""

    def test_upload_sempre_nao_listado(self):
        fonte = inspect.getsource(yt)
        self.assertIn('"unlisted"', fonte)
        self.assertNotIn('"public"', fonte,
                          "o OMEGA nunca decide sozinho tornar um vídeo público")

    def test_nao_manipula_senha(self):
        fonte = inspect.getsource(yt).lower()
        for proibido in ("password", "senha ="):
            self.assertNotIn(proibido, fonte)

    def test_escopo_e_so_de_upload(self):
        # Escopo largo demais (leitura de analytics, gestão do canal) amplia
        # à toa o que um token vazado conseguiria fazer.
        self.assertEqual(yt.ESCOPOS, ["https://www.googleapis.com/auth/youtube.upload"])

    def test_credenciais_e_token_fora_do_git(self):
        ignore = (Path(__file__).resolve().parent.parent / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("youtube_client.json", ignore)
        self.assertIn("token.json", ignore)


class TestSemRede(unittest.TestCase):
    """Comportamento antes de qualquer chamada à API."""

    def test_video_inexistente_nao_sobe_nada(self):
        r = yt.enviar("C:/nao/existe/video.mp4", "Título qualquer")
        self.assertIn("Não achei", r)

    def test_titulo_vazio_e_recusado(self):
        r = yt.enviar(str(yt.CLIENT_SECRETS), "   ")
        self.assertIn("título", r.lower())

    def test_disponivel_detecta_as_bibliotecas(self):
        self.assertTrue(yt.disponivel())

    def test_caminhos_de_config_ficam_dentro_de_voice_config(self):
        self.assertEqual(yt.CLIENT_SECRETS.parent, yt.CONFIG_DIR)
        self.assertEqual(yt.TOKEN_FILE.parent, yt.CONFIG_DIR)
        self.assertEqual(yt.CONFIG_DIR.name, "config")


class TestNomeDoProjeto(unittest.TestCase):
    """"postar o Minotauro no youtube" tem que procurar o MINOTAURO.

    Regressão de verdade, encontrada em 04/09/2026: o `re.sub` que tira as
    preposições rodava sem `\\b` e comia a preposição DENTRO do nome —
    "minotauro" virava "mi tauro", "anansi" virava "a nsi" — e o OMEGA dizia
    "não achei vídeo renderizado" para um render que existia. Escapava do
    olho porque "medusa", o exemplo de sempre, não contém nenhuma delas.
    """

    def setUp(self):
        from tools import local_commands

        self.lc = local_commands
        self.procurado: list[str] = []

    def _nome_procurado(self, frase: str) -> str:
        """Vai pela porta da frente (`handle`), não direto no `_postar`: é o
        caminho que o comando de voz percorre de verdade."""
        from unittest.mock import patch

        with patch.object(self.lc, "_latest_render",
                          side_effect=lambda c: self.procurado.append(c)):
            self.lc.handle(frase, _UIdeMentira())
        return self.procurado[-1]

    def test_preposicao_dentro_do_nome_sobrevive(self):
        for frase, esperado in (
            ("postar o minotauro no youtube", "minotauro"),
            ("postar o anansi no youtube", "anansi"),
            ("postar a medusa no youtube", "medusa"),
            ("postar a baba yaga no instagram", "baba yaga"),
        ):
            with self.subTest(frase=frase):
                self.assertEqual(self._nome_procurado(frase), esperado)

    def test_rede_casa_por_palavra_inteira(self):
        """"x" solto casa dentro de meia língua portuguesa."""
        self.assertIn("Em qual rede", self.lc._postar("esfinge", ui=None))


class _UIdeMentira:
    """O mínimo que `handle` toca no caminho de postagem."""

    def show_document(self, titulo, texto): pass
    def show_video(self, titulo, caminho): pass
    def show_hud(self): pass
    def write_log(self, texto): pass
    def set_state(self, estado): pass


if __name__ == "__main__":
    unittest.main(verbosity=2)
