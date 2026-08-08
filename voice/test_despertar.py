"""Testa o portão da palavra de ativação no motor Live.

Existe por causa de uma coisa vista no primeiro uso real: sem portão, o OMEGA
respondeu a uma conversa da sala que não era com ele. Cada frase dessas é
cota gratuita queimada e uma interrupção que ninguém pediu.

Três coisas precisam ser verdade ao mesmo tempo, e as três são medidas aqui
com áudio de verdade:

  1. ele abre quando é chamado (senão o assistente fica inútil);
  2. ele NÃO abre com conversa de sala (senão o portão não serve para nada);
  3. o comando não se perde ao abrir — "Ômega, monta o vídeo da Medusa" tem
     que chegar inteiro, senão o Samuel repete tudo, que é exatamente o que
     este trabalho existe para acabar.

O áudio vem do `test_escuta.py` (chamadas) e é gerado aqui (distratores).
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

BASE = Path(__file__).resolve().parent
CHAMADAS = BASE / "_audio_teste"
DISTRATORES = BASE / "_audio_fp"

# Conversa de sala. Nada disto pode acordar o OMEGA.
FRASES_DE_SALA = [
    "eu gosto de ter uma habilidade finalizadora, ta ligado",
    "cara, nem com essa metralhadora eu tava conseguindo matar",
    "voce viu o jogo ontem a noite",
    "acho que a gente devia pedir uma pizza",
    "amanha eu preciso acordar cedo pra trabalhar",
    "a minha amiga falou que o filme e muito bom",
    "nao sei se essa e a melhor opcao pra gente",
    "ele chegou em casa e nao falou nada com ninguem",
    "o mercado ali da esquina ta caro demais",
    "deixa eu ver como e que vai ser isso",
]


def gerar_distratores() -> bool:
    import pyttsx3

    DISTRATORES.mkdir(exist_ok=True)
    for i, frase in enumerate(FRASES_DE_SALA, 1):
        alvo = DISTRATORES / f"{i:02d}.wav"
        if alvo.exists():
            continue
        motor = pyttsx3.init()
        for v in motor.getProperty("voices"):
            if "portug" in v.name.lower() or "brazil" in v.name.lower():
                motor.setProperty("voice", v.id)
                break
        motor.setProperty("rate", 175)
        motor.save_to_file(frase, str(alvo))
        motor.runAndWait()
        motor.stop()
        del motor
    return True


class TestNomeNoTexto(unittest.TestCase):
    """A parte barata: reconhecer o nome numa frase já transcrita."""

    def test_formas_que_o_transcritor_produz(self):
        from tools.despertar import encontrar_nome

        for frase in ("Ômega, me mostra a pesquisa", "Omega monta o video",
                      "ó Ômega, abre isso", "omeca, le a pesquisa",
                      "o mega, que horas sao"):
            chamou, _ = encontrar_nome(frase)
            self.assertTrue(chamou, f"não reconheceu o nome em: {frase}")

    def test_devolve_o_que_veio_depois(self):
        from tools.despertar import encontrar_nome

        _, resto = encontrar_nome("Ômega, monta o vídeo da Medusa")
        self.assertEqual(resto, "monta o vídeo da Medusa")

    def test_conversa_de_sala_nao_chama(self):
        from tools.despertar import encontrar_nome

        for frase in ("voce viu o jogo ontem", "acho que devia pedir pizza",
                      "o mercado ali da esquina ta caro",
                      # Estas DEVEM ser ignoradas: sao palavras portuguesas
                      # comuns que estavam na lista de variantes por causa do
                      # Vosk, e acordavam o OMEGA no meio de conversa alheia.
                      "a minha amiga falou que o filme e bom",
                      "nega, vem ca um pouquinho"):
            chamou, _ = encontrar_nome(frase)
            self.assertFalse(chamou, f"abriu à toa em: {frase}")

    def test_nome_muito_no_fim_da_frase_nao_conta(self):
        """Só as primeiras palavras: senão qualquer menção casual abriria."""
        from tools.despertar import encontrar_nome

        chamou, _ = encontrar_nome(
            "ontem eu estava mexendo no computador e o Ômega travou")
        self.assertFalse(chamou)


class TestPortaoComAudio(unittest.TestCase):
    """Com áudio de verdade — é o que mede o portão de fato."""

    @classmethod
    def setUpClass(cls):
        if not CHAMADAS.exists():
            raise unittest.SkipTest("rode `python test_escuta.py` para gerar o áudio")
        gerar_distratores()
        from tools.despertar import Portao

        cls.Portao = Portao

    def _passar(self, arquivo: Path) -> bytes | None:
        """Empurra o wav pelo portão em blocos, como o microfone faria."""
        from test_escuta import _ler_wav_16k

        portao = self.Portao()
        pcm = _ler_wav_16k(arquivo)
        for i in range(0, len(pcm), 3200):
            saida = portao.alimentar(pcm[i:i + 3200])
            if saida is not None:
                return saida
        # Silêncio no fim: é o que fecha a frase no detector de energia.
        return portao.alimentar(b"\x00" * 32000)

    def test_abre_quando_chamado(self):
        abriu = sum(1 for i in range(1, 7)
                    if self._passar(CHAMADAS / f"{i:02d}.wav") is not None)
        print(f"\n   abriu em {abriu}/6 chamadas")
        self.assertGreaterEqual(abriu, 5, "está surdo ao próprio nome")

    def test_nao_abre_com_conversa_de_sala(self):
        falsos = [i for i in range(1, len(FRASES_DE_SALA) + 1)
                  if self._passar(DISTRATORES / f"{i:02d}.wav") is not None]
        print(f"   falsos positivos: {len(falsos)}/{len(FRASES_DE_SALA)}")
        self.assertLessEqual(
            len(falsos), 1,
            f"abriu com conversa de sala: {[FRASES_DE_SALA[i-1] for i in falsos]}")

    def test_o_comando_nao_se_perde(self):
        """O trecho devolvido tem que ser a frase INTEIRA, não só o depois."""
        audio = self._passar(CHAMADAS / "01.wav")
        self.assertIsNotNone(audio)
        segundos = len(audio) / 2 / 16000
        self.assertGreater(segundos, 2.0,
                           f"devolveu só {segundos:.1f}s — o comando foi cortado")

        from tools import transcritor

        texto = transcritor.transcrever(audio).lower()
        print(f"   trecho devolvido: {segundos:.1f}s — '{texto[:60]}'")
        self.assertIn("medusa", texto, "o comando se perdeu ao abrir o portão")


if __name__ == "__main__":
    unittest.main(verbosity=2)
