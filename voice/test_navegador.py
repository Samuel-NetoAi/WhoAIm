"""Testa o navegador do OMEGA — com atenção especial às regras de segurança.

O QUE MAIS IMPORTA AQUI NÃO É FUNCIONAR, É NÃO PUBLICAR. Automação de
navegador quebra quando as redes mudam de layout, e isso é aceitável; o que
não é aceitável é o OMEGA apertar "publicar" sozinho, ou digitar senha.
Esses dois testes não dependem de rede e rodam sempre.

O teste com navegador de verdade abre o Chrome e vai ao YouTube. Precisa de
`--real` e de rodar pelo PowerShell ou pelo próprio app: do terminal do
agente o Playwright falha com "spawn UNKNOWN" ao abrir janela visível.

    python test_navegador.py            # só as regras (rápido, sem rede)
    python test_navegador.py --real     # abre o Chrome de verdade
"""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import navegador  # noqa: E402

REAL = "--real" in sys.argv


class TestRegrasDeSeguranca(unittest.TestCase):
    """As duas regras que o Samuel aceitou e que não se negociam."""

    def test_nunca_clica_em_publicar(self):
        fonte = inspect.getsource(navegador)
        for proibido in ("publicar'", 'publicar"', "Publish", "PUBLICAR",
                         "publish'", 'publish"'):
            if proibido in fonte:
                # Só vale se estiver num clique. Menção em comentário é ok.
                for linha in fonte.splitlines():
                    if proibido in linha and ".click(" in linha:
                        self.fail(f"clique em publicar encontrado: {linha.strip()}")

    def test_nao_manipula_senha(self):
        fonte = inspect.getsource(navegador).lower()
        for proibido in ("input[type=password]", "senha\"", "password'",
                         "fill(pass", "type(pass"):
            self.assertNotIn(proibido, fonte,
                             "o OMEGA não pode encostar em campo de senha")

    def test_perfil_e_prints_ficam_fora_do_git(self):
        ignore = (Path(__file__).resolve().parent.parent / ".gitignore"
                  ).read_text(encoding="utf-8")
        self.assertIn("navegador-perfil", ignore, "o perfil contém sessões")
        self.assertIn("_prints", ignore, "os prints mostram a tela logada")


class TestSemNavegador(unittest.TestCase):
    """Comportamento antes de qualquer janela abrir."""

    def test_rede_desconhecida_lista_as_que_existem(self):
        r = navegador.abrir("orkut")
        self.assertIn("YouTube", r)

    def test_video_inexistente_nao_abre_nada(self):
        r = navegador.preparar_postagem("youtube", "C:/nao/existe/video.mp4")
        self.assertIn("Não achei", r)

    def test_ver_sem_janela_aberta(self):
        self.assertIn("Não estou", navegador.ver())

    def test_opera_gx_nao_entra_na_lista(self):
        """Ele abre e não navega — testado. Entrar aqui seria armadilha."""
        nomes = " ".join(n for _, n in navegador.NAVEGADORES).lower()
        self.assertNotIn("opera", nomes)

    def test_brave_e_uma_opcao(self):
        """Testado: lança e navega, inclusive no upload do YouTube."""
        nomes = [n for _, n in navegador.NAVEGADORES]
        self.assertIn("Brave", nomes)

    def test_config_escolhe_o_navegador(self):
        import json
        from unittest.mock import patch

        with patch.object(navegador, "_preferido", return_value="brave"):
            caminho, nome = navegador._executavel()
        if caminho:
            self.assertEqual(nome, "Brave")

    def test_sem_navegador_nenhum_explica_o_opera(self):
        from unittest.mock import patch

        with patch.object(navegador, "_executavel", return_value=(None, None)):
            r = navegador.abrir("youtube")
        self.assertIn("Opera GX não serve", r)

    def test_youtube_aponta_para_a_caixa_de_envio(self):
        """A URL do Studio caía no login; esta abre o envio direto."""
        self.assertEqual(navegador.ENVIO["youtube"], "https://www.youtube.com/upload")

    def test_toda_rede_tem_caminho_ate_o_arquivo(self):
        for chave in ("youtube", "instagram", "tiktok", "x"):
            self.assertIn(chave, navegador.CAMINHO_ATE_O_ARQUIVO)
            self.assertTrue(navegador.CAMINHO_ATE_O_ARQUIVO[chave])

    def test_detecta_parede_de_login(self):
        class Falsa:
            def __init__(self, u):
                self.url = u

        self.assertTrue(navegador._parece_tela_de_login(
            Falsa("https://accounts.google.com/ServiceLogin?service=youtube")))
        self.assertTrue(navegador._parece_tela_de_login(
            Falsa("https://www.tiktok.com/login")))
        self.assertFalse(navegador._parece_tela_de_login(
            Falsa("https://studio.youtube.com/channel/UC123/content?d=ud")))


@unittest.skipUnless(REAL, "use --real, e rode pelo PowerShell")
class TestComNavegadorDeVerdade(unittest.TestCase):
    def test_abre_e_tira_print(self):
        prints = []

        class UIFalsa:
            def show_image(self, titulo, caminho):
                prints.append((titulo, caminho))

        try:
            print("\n  ", navegador.abrir("youtube"))
            print("  ", navegador.ver(UIFalsa()))
            self.assertTrue(prints, "não gerou print")
            arquivo = Path(prints[-1][1])
            self.assertTrue(arquivo.exists() and arquivo.stat().st_size > 5000,
                            "o print saiu vazio")
            print(f"   print: {arquivo.name}, {arquivo.stat().st_size // 1024} KB")
        finally:
            navegador.fechar()


if __name__ == "__main__":
    unittest.main(argv=[a for a in sys.argv if a != "--real"], verbosity=2)
