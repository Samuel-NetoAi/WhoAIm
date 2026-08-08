"""Testa a gravação da aula — inclusive a armadilha que ela existe para evitar.

A Mixagem estéreo captura TUDO que sai pelos alto-falantes. Isso é o que
permite gravar a aula sem tocar no vídeo, e é também o que faria a voz do
próprio OMEGA entrar na gravação — e depois virar "regra do curso" na extração.
O teste central aqui é justamente esse: ele fala no meio, e a fala DELE não
pode aparecer na transcrição da aula.

Precisa de saída de áudio funcionando. Roda pelo PowerShell ou pelo app.
"""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import aula, transcritor  # noqa: E402


def tem_mixagem() -> bool:
    return aula._dispositivo_do_pc() is not None


class TestSemDispositivo(unittest.TestCase):
    """O que precisa valer mesmo sem a Mixagem estéreo ligada."""

    def test_parar_sem_gravar_nao_estoura(self):
        if aula.gravando():
            aula.parar()
        self.assertIn("Não estou gravando", aula.parar())

    def test_print_sem_aula_avisa(self):
        self.assertIn("Não estou gravando", aula.print_agora())

    def test_curso_atual_tem_padrao(self):
        self.assertTrue(aula.curso_atual())

    def test_pausa_e_contador_nao_booleano(self):
        """Duas falas sobrepostas não podem religar a captura cedo demais."""
        aula.pausar()
        aula.pausar()
        aula.retomar()
        self.assertGreater(aula._silenciado, 0,
                           "ainda há uma fala em curso; não podia ter religado")
        aula.retomar()
        self.assertEqual(aula._silenciado, 0)

    def test_nome_de_pasta_aguenta_fala(self):
        """O título vem da voz: acento, pontuação e maiúscula entram."""
        self.assertEqual(aula._slug("Títulos que FUNCIONAM!"), "titulos-que-funcionam")
        self.assertEqual(aula._slug("   "), "aula")


@unittest.skipUnless(tem_mixagem(), "Mixagem estéreo não disponível/ativada")
class TestGravacaoReal(unittest.TestCase):
    def setUp(self):
        self.pasta = None

    def tearDown(self):
        if aula.gravando():
            aula.parar()
        # Limpa a aula de teste para não poluir a pasta do curso.
        if self.pasta and self.pasta.exists():
            import shutil

            shutil.rmtree(self.pasta, ignore_errors=True)

    def test_grava_o_som_do_pc_e_ignora_a_voz_do_omega(self):
        from tools import voz_local

        r = aula.iniciar("curso-de-teste", "aula de teste")
        print(f"\n   {r}")
        self.assertIn("Gravando", r)
        self.pasta = aula._estado["pasta"]

        # 1) o "professor": isto TEM que aparecer.
        voz_local.falar("O professor está explicando a retenção do vídeo.",
                        economico=True)
        # A fala acima passou por voz_local, que pausa a captura — para simular
        # o VÍDEO (que não pausa nada) o áudio precisa sair com a captura ativa.
        # Então tocamos de novo sem passar pelo pausador.
        aula.retomar() if aula._silenciado else None
        _tocar_direto("O professor está explicando a retenção do vídeo.")

        time.sleep(0.8)

        # 2) o OMEGA respondendo: isto NÃO pode aparecer.
        voz_local.falar("Batata frita com abacaxi e guarda-chuva roxo.",
                        economico=True)
        time.sleep(0.8)

        fim = aula.parar()
        print(f"   {fim}")

        wav = self.pasta / "audio.wav"
        self.assertTrue(wav.exists(), "não gravou arquivo")
        audio = transcritor.ler_wav_16k(wav)
        segundos = len(audio) / 2 / 16000
        print(f"   gravou {segundos:.1f}s")
        self.assertGreater(segundos, 1.0, "gravou quase nada")

        texto = transcritor.transcrever(audio).lower()
        print(f"   transcrição: '{texto[:90]}'")

        # "professor", e não "retenção": o Whisper já devolveu "detenção" aqui,
        # e o que este teste mede é se o ÁUDIO foi gravado — não a grafia. Um
        # teste que quebra por uma letra vira ruído e acaba sendo ignorado.
        self.assertIn("professor", texto, "não gravou o áudio do 'vídeo'")
        for palavra in ("abacaxi", "guarda-chuva", "batata"):
            self.assertNotIn(
                palavra, texto,
                f"a voz do OMEGA ('{palavra}') entrou na gravação da aula")

    def test_buffer_recente_tem_o_que_transcrever(self):
        aula.iniciar("curso-de-teste", "buffer")
        self.pasta = aula._estado["pasta"]
        _tocar_direto("Testando o buffer dos últimos segundos.")
        time.sleep(0.8)
        trecho = aula.trecho_recente()
        aula.parar()
        segundos = len(trecho) / 2 / 16000
        print(f"\n   buffer: {segundos:.1f}s")
        self.assertGreater(segundos, 0.5, "o buffer rolante ficou vazio")
        self.assertLessEqual(segundos, aula.JANELA_RECENTE + 5)

    def test_print_sob_comando(self):
        aula.iniciar("curso-de-teste", "print")
        self.pasta = aula._estado["pasta"]
        r = aula.print_agora("exemplo de titulo")
        aula.parar()
        print(f"\n   {r}")
        telas = list((self.pasta / "telas").glob("*.jpg"))
        self.assertTrue(telas, "não salvou print")
        self.assertGreater(telas[0].stat().st_size, 5000, "print saiu vazio")


def _tocar_direto(texto: str) -> None:
    """Fala SEM pausar a gravação — simula o áudio do vídeo do curso."""
    import pyttsx3

    motor = pyttsx3.init()
    for v in motor.getProperty("voices"):
        if "portug" in v.name.lower() or "maria" in v.name.lower():
            motor.setProperty("voice", v.id)
            break
    motor.setProperty("rate", 190)
    motor.say(texto)
    motor.runAndWait()
    motor.stop()


if __name__ == "__main__":
    unittest.main(verbosity=2)
