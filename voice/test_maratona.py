"""Testa a maratona do curso SEM abrir navegador nenhum.

O que pode dar errado aqui é caro de descobrir na prática: um erro de
interpretação faz o OMEGA passar três horas navegando quando ele só queria
gravar uma aula, e um erro no acompanhamento do vídeo faz ele gravar uma hora
de silêncio e só descobrir depois. Então o player e a página viram dublês, e
o que se testa é a DECISÃO.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import maratona  # noqa: E402

URL_REAL = ("https://members.kiwify.com/675fa57e-4021-4264-9214-f0cc746d28ec/"
            "fa1d5590-e52a-4fc5-a399-198ff910622e/"
            "75784849-07f9-43a8-b21e-c70fb1b6fa8d?club=3ad27aab-dece-4969")


class TestEntendeOPedido(unittest.TestCase):
    """Assistir O CURSO e assistir UMA AULA são comandos vizinhos e opostos."""

    def test_reconhece_a_maratona(self):
        from tools.local_commands import _e_maratona

        for frase in ("assiste o curso inteiro",
                      "vamos assistir o curso",
                      "quero que você assista o curso todo sozinho",
                      "começa o curso",
                      "grava o curso inteiro pra mim",
                      "faz a maratona das aulas",
                      "assistir todas as aulas do curso"):
            self.assertTrue(_e_maratona(frase.lower()), frase)

    def test_nao_rouba_o_pedido_de_uma_aula_so(self):
        """"assistir aula 2" grava o que está na tela — não navega o curso."""
        from tools.local_commands import _e_maratona, _e_pedido_de_aula

        for frase in ("vamos assistir a aula 2",
                      "assistir aula de miniatura",
                      "grava essa aula",
                      "começa a aula sobre títulos"):
            self.assertFalse(_e_maratona(frase.lower()), frase)
            self.assertTrue(_e_pedido_de_aula(frase.lower()), frase)

    def test_nao_dispara_por_engano(self):
        from tools.local_commands import _e_maratona

        for frase in ("processar curso", "cancelar curso",
                      "parar o curso", "como está o curso",
                      "me mostra as regras do curso"):
            self.assertFalse(_e_maratona(frase.lower()), frase)

    def test_encerrar(self):
        from tools.local_commands import _e_parar_maratona

        for frase in ("parar o curso", "para a maratona",
                      "pode parar o curso", "encerra o curso"):
            self.assertTrue(_e_parar_maratona(frase.lower()), frase)
        for frase in ("assistir o curso", "processar curso"):
            self.assertFalse(_e_parar_maratona(frase.lower()), frase)

    def test_o_modelo_tambem_tem_como(self):
        """Quando o casamento por palavra falhar, o Gemini precisa conseguir."""
        sys.argv = ["t"]
        import main

        f = next((x for x in main.TOOLS if x["name"] == "assistir_curso"), None)
        self.assertIsNotNone(f, "faltou a ferramenta assistir_curso")
        self.assertEqual(sorted(f["parameters"]["properties"]["acao"]["enum"]),
                         ["iniciar", "parar", "situacao"])


class TestAcharAsAulas(unittest.TestCase):

    def test_link_de_aula_x_link_de_menu(self):
        self.assertTrue(maratona.LINK_DE_AULA.search(URL_REAL))
        for outro in ("https://members.kiwify.com/",
                      "https://members.kiwify.com/conta",
                      "https://kiwify.com.br/termos",
                      "https://members.kiwify.com/675fa57e-4021/perfil"):
            self.assertFalse(maratona.LINK_DE_AULA.search(outro), outro)

    def test_mantem_a_ordem_e_nao_repete(self):
        """A ordem da página É a ordem do curso — não dá para embaralhar."""
        a = URL_REAL.split("?")[0]
        b = a[:-3] + "bbb"
        c = a[:-3] + "ccc"

        class Pagina:
            def evaluate(self, _):
                return [a, "https://members.kiwify.com/conta", b,
                        a + "?club=x", c]

        self.assertEqual(maratona._lista_de_aulas(Pagina()), [a, b, c])

    def test_pagina_quebrada_nao_derruba(self):
        class Pagina:
            def evaluate(self, _):
                raise RuntimeError("frame detached")

        self.assertEqual(maratona._lista_de_aulas(Pagina()), [])


class Quadro:
    """Dublê do <video>: devolve os estados na ordem que eu mandar."""

    def __init__(self, estados):
        self.estados = list(estados)
        self.plays = 0

    def evaluate(self, script):
        if "play()" in script:
            self.plays += 1
            return True
        if not self.estados:
            return {"t": 0, "d": 10, "fim": True, "parado": False}
        return self.estados.pop(0)

    def click(self, *a, **k):
        raise RuntimeError("sem botão")


class TestAcompanhar(unittest.TestCase):
    """O laço que decide quando a aula acabou — e quando algo deu errado."""

    def setUp(self):
        from tools import aula as _aula

        # Relógio falso, e não só `sleep` desligado: o laço decide por TEMPO
        # DECORRIDO ("travado há 2 minutos", "mudo há 1 minuto"). Sem adiantar
        # o relógio junto, nada nunca demora e os limites nunca disparam — a
        # primeira versão deste teste passava por engano.
        class Relogio:
            def __init__(self):
                self.agora = 0.0

            def sleep(self, s):
                self.agora += s or 4

            def monotonic(self):
                return self.agora

            time = staticmethod(__import__("time").time)   # o resto é real

        self._time = maratona.time
        maratona.time = Relogio()
        self._pico = _aula._estado.get("pico", 0)
        _aula._estado["pico"] = _aula.PICO_MINIMO + 100   # com som, por padrão
        try:
            maratona.PEDIDO_DE_PARAR.unlink()
        except FileNotFoundError:
            pass

    def tearDown(self):
        from tools import aula as _aula

        maratona.time = self._time
        _aula._estado["pico"] = self._pico

    def _andando(self, ate):
        return [{"t": float(i), "d": 100.0, "fim": False, "parado": False}
                for i in range(0, ate)]

    def test_termina_quando_o_video_termina(self):
        q = Quadro(self._andando(10) +
                   [{"t": 100.0, "d": 100.0, "fim": True, "parado": False}])
        self.assertEqual(maratona._acompanhar(q, 100, 1, 3, "x"), "acabou")

    def test_termina_no_ultimo_segundo_mesmo_sem_o_ended(self):
        """Nem todo player dispara `ended`; sem isto a aula nunca fecharia."""
        q = Quadro(self._andando(5) +
                   [{"t": 99.0, "d": 100.0, "fim": False, "parado": False}])
        self.assertEqual(maratona._acompanhar(q, 100, 1, 3, "x"), "acabou")

    def test_video_mudo_para_em_vez_de_gravar_silencio(self):
        """A falha cara: uma hora de nada, descoberta só na transcrição."""
        from tools import aula as _aula

        _aula._estado["pico"] = 0
        # Muitos estados: o laço tem que desistir por conta própria.
        q = Quadro(self._andando(400))
        self.assertEqual(maratona._acompanhar(q, 100, 1, 3, "x"),
                         "vídeo sem som")
        self.assertGreaterEqual(q.plays, 1, "nem tentou religar o som antes")

    def test_video_travado_nao_prende_para_sempre(self):
        parado = [{"t": 12.0, "d": 100.0, "fim": False, "parado": False}] * 500
        q = Quadro(self._andando(5) + parado)
        self.assertEqual(maratona._acompanhar(q, 100, 1, 3, "x"),
                         "o vídeo travou")

    def test_obedece_o_pedido_de_parar(self):
        maratona.PEDIDO_DE_PARAR.write_text("1", encoding="utf-8")
        try:
            q = Quadro(self._andando(50))
            self.assertEqual(maratona._acompanhar(q, 100, 1, 3, "x"),
                             "você mandou parar")
        finally:
            maratona.PEDIDO_DE_PARAR.unlink()

    def test_pagina_fechada_no_meio_encerra_limpo(self):
        class Morto:
            def evaluate(self, _):
                raise RuntimeError("Target closed")

        self.assertEqual(maratona._acompanhar(Morto(), 100, 1, 3, "x"),
                         "a página saiu do ar")


class TestEstado(unittest.TestCase):

    def setUp(self):
        self.backup = (maratona.ESTADO.read_bytes()
                       if maratona.ESTADO.exists() else None)

    def tearDown(self):
        if self.backup is None:
            maratona.ESTADO.unlink(missing_ok=True)
        else:
            maratona.ESTADO.write_bytes(self.backup)

    def test_estado_orfao_nao_mente_que_esta_rodando(self):
        """O app pode ser reiniciado; um .json parado no disco enganaria."""
        maratona.ESTADO.write_text(
            json.dumps({"rodando": True, "pid": 999999}), encoding="utf-8")
        self.assertFalse(maratona.rodando())

    def test_situacao_sem_nada_nao_inventa(self):
        maratona.ESTADO.unlink(missing_ok=True)
        self.assertIn("Não comecei", maratona.situacao())

    def test_nao_maratona_gravando_uma_aula(self):
        """Duas gravações ao mesmo tempo disputariam a mesma saída de áudio."""
        from tools import aula as _aula

        _aula._estado["gravando"] = True
        try:
            self.assertIn("parar de gravar", maratona.iniciar(URL_REAL))
        finally:
            _aula._estado["gravando"] = False

    def test_sem_link_ele_pede_em_vez_de_chutar(self):
        salvo = maratona.CONFIG.read_bytes() if maratona.CONFIG.exists() else None
        maratona.CONFIG.unlink(missing_ok=True)
        try:
            self.assertIn("link do curso", maratona.iniciar(""))
        finally:
            if salvo is not None:
                maratona.CONFIG.write_bytes(salvo)


if __name__ == "__main__":
    unittest.main(verbosity=2)
