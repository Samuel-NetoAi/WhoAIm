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

    def _pagina(self, itens):
        class Pagina:
            def evaluate(self, _):
                return itens

        return Pagina()

    def _link(self, sufixo, txt, fraco=False):
        return {"href": URL_REAL.split("?")[0][:-3] + sufixo,
                "txt": txt, "fraco": fraco}

    def test_mantem_a_ordem_e_nao_repete(self):
        """A ordem da página É a ordem do curso — não dá para embaralhar."""
        pag = self._pagina([self._link("aaa", "Aula 1 - Começo"),
                            self._link("bbb", "Aula 2 - Meio"),
                            {"href": "https://members.kiwify.com/conta",
                             "txt": "Minha conta", "fraco": False},
                            self._link("aaa", "Aula 1 - Começo"),
                            self._link("ccc", "Aula 3 - Fim")])
        self.assertEqual([a["titulo"] for a in maratona._lista_de_aulas(pag)],
                         ["Aula 1 - Começo", "Aula 2 - Meio", "Aula 3 - Fim"])

    def test_descarta_as_abas_que_parecem_aula(self):
        """Medido na página real: "Aulas", "Conteúdo" e "Comentários" têm o
        MESMO formato de endereço da aula, e apontam para a própria lição.
        Sem este filtro o OMEGA abriria a mesma página três vezes."""
        pag = self._pagina([self._link("111", ""),
                            self._link("222", "Aulas"),
                            self._link("333", "Current page: Conteúdo"),
                            self._link("444", "Comentários0"),
                            self._link("555", "Aula 1 - A Escolha")])
        achadas = maratona._lista_de_aulas(pag)
        self.assertEqual([a["titulo"] for a in achadas], ["Aula 1 - A Escolha"])

    def test_marca_a_aula_que_ainda_nao_abriu(self):
        """A Kiwify libera por data. A página abre, mas não tem vídeo."""
        pag = self._pagina([
            self._link("aaa", "Aula 1: A Magica do SUBNICHO"),
            self._link("bbb", "Aula 2: O Maior Segredo Liberação em 15/08/2026"),
            self._link("ccc", "Aula 3: HACK para Subnichar", fraco=True)])
        achadas = maratona._lista_de_aulas(pag)
        self.assertEqual([a["bloqueada"] for a in achadas],
                         [False, True, True])
        # A data não pode virar parte do nome da pasta.
        self.assertEqual(achadas[1]["titulo"], "Aula 2: O Maior Segredo")

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


class TestPuloPeloLogin(unittest.TestCase):
    """Medido na Kiwify real, e quase custou a noite inteira.

    A página abre na aula, PULA para /login por volta de 2 s enquanto
    revalida a sessão, e volta sozinha aos 10. Uma checagem única cai no meio
    do pulo mais ou menos na metade das vezes — e o worker encerrou com
    "pediu login" estando logado o tempo todo.
    """

    class Pagina:
        """Reproduz o pulo: aula → /login → aula."""

        def __init__(self, roteiro):
            self.roteiro = list(roteiro)
            self.url = self.roteiro[0]

        def _passo(self):
            if len(self.roteiro) > 1:
                self.roteiro.pop(0)
            self.url = self.roteiro[0]

        def evaluate(self, _):
            pronta = "/login" not in self.url
            self._passo()
            return pronta

    def setUp(self):
        self._time = maratona.time

        class Relogio:
            agora = 0.0

            def sleep(self, s):
                Relogio.agora += s

            def monotonic(self):
                return Relogio.agora

            time = staticmethod(__import__("time").time)

        maratona.time = Relogio()

    def tearDown(self):
        maratona.time = self._time

    def test_espera_a_volta_em_vez_de_desistir(self):
        aula_ = "https://members.kiwify.com/a/b/c"
        pag = self.Pagina([aula_, "https://members.kiwify.com/login?club=x",
                           "https://members.kiwify.com/login?club=x",
                           aula_])
        self.assertTrue(maratona._assentar(pag, 40))

    def test_login_de_verdade_nao_assenta(self):
        """Sessão caída mesmo: fica no /login e ele tem que dizer isso."""
        pag = self.Pagina(["https://members.kiwify.com/login?club=x"])
        self.assertFalse(maratona._assentar(pag, 20))

    def test_pagina_sem_lista_nem_video_nao_conta_como_pronta(self):
        class Vazia:
            url = "https://members.kiwify.com/a/b/c"

            def evaluate(self, _):
                return False

        self.assertFalse(maratona._assentar(Vazia(), 10))


class TestRetomarDepoisDeCair(unittest.TestCase):
    """A pergunta do Samuel: "se der erro de madrugada, perdemos horas?"

    A resposta só pode ser "não" se retomar souber exatamente o que já ficou
    pronto — e, principalmente, o que ficou PELA METADE.
    """

    def setUp(self):
        import tempfile

        from tools import aula as _aula

        self.tmp = tempfile.TemporaryDirectory()
        self._cursos = _aula.CURSOS
        _aula.CURSOS = Path(self.tmp.name) / "Cursos"
        self.raiz = _aula.CURSOS / "curso-x" / "aulas"
        self.raiz.mkdir(parents=True)

    def tearDown(self):
        import shutil

        from tools import aula as _aula

        _aula.CURSOS = self._cursos
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def _pasta(self, slug, minutos, completa):
        d = self.raiz / f"20260809-1800-{slug}"
        (d / "telas").mkdir(parents=True)
        (d / "audio.wav").write_bytes(bytes(int(minutos * 60 * 32_000)))
        if completa:
            maratona._marcar_completa(d, slug, minutos * 60)
        return d

    def test_pula_o_que_terminou(self):
        self._pasta("aula-1-a-escolha", 12, completa=True)
        self.assertTrue(maratona._ja_gravada("curso-x", "Aula 1 A Escolha"))

    def test_NAO_pula_o_que_ficou_pela_metade(self):
        """16 minutos de uma aula de 20 tem WAV grande e parece pronta.

        Foi por isso que a marca deixou de ser "o arquivo é grande": ao
        retomar, ele pularia justamente a aula que o tombo interrompeu.
        """
        self._pasta("aula-2-sub-nicho", 16, completa=False)
        self.assertFalse(maratona._ja_gravada("curso-x", "Aula 2 Sub Nicho"))

    def test_aula_que_nunca_comecou_nao_e_pulada(self):
        self.assertFalse(maratona._ja_gravada("curso-x", "Aula 9"))

    def test_espaco_em_disco_e_conferido_antes(self):
        """Encher o disco na aula 30 custa as trinta seguintes."""
        self.assertEqual(maratona._espaco_curto(), "",
                         "há espaço nesta máquina; não devia reclamar")
        antes = maratona.MINIMO_LIVRE_GB
        maratona.MINIMO_LIVRE_GB = 10_000_000     # nenhum disco tem isso
        try:
            self.assertIn("Libere espaço", maratona._espaco_curto())
        finally:
            maratona.MINIMO_LIVRE_GB = antes


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
