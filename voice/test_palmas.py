"""Testes do detector de palmas — com áudio sintético, sem microfone.

O que importa aqui não é acertar a palma (isso é fácil), é NÃO acertar o que
não é palma. Um detector que dispara com porta batendo e voz alta traz a janela
para a frente no meio do trabalho, e vira um estorvo.

Rodar: .venv/bin/python -m unittest test_palmas -v
"""

from __future__ import annotations

import unittest

import clap


class TesteBase(unittest.TestCase):
    def setUp(self):
        self.gestos = 0

        def marcar():
            self.gestos += 1

        self.det = clap.DetectorDePalmas(taxa=16000, ao_detectar=marcar)

    def alimentar(self, *pedacos: bytes) -> None:
        for p in pedacos:
            self.det.alimentar(p)


class TestReconhece(TesteBase):
    def test_duas_palmas_no_intervalo_certo(self):
        self.alimentar(
            clap.silencio(0.5),
            clap.palma(),
            clap.silencio(0.2),
            clap.palma(),
            clap.silencio(0.4),
        )
        self.assertEqual(self.gestos, 1)

    def test_funciona_no_limite_inferior_do_intervalo(self):
        self.alimentar(
            clap.silencio(0.4), clap.palma(), clap.silencio(0.05),
            clap.palma(), clap.silencio(0.3),
        )
        self.assertEqual(self.gestos, 1)

    def test_palma_dividida_entre_dois_blocos_ainda_conta(self):
        """O áudio chega em blocos de 500 ms; o gesto não respeita a fronteira."""
        cheio = clap.silencio(0.4) + clap.palma() + clap.silencio(0.2) + clap.palma()
        meio = len(cheio) // 2
        meio -= meio % 2
        self.alimentar(cheio[:meio], cheio[meio:], clap.silencio(0.3))
        self.assertEqual(self.gestos, 1)


class TestRejeita(TesteBase):
    def test_uma_palma_so_nao_e_gesto(self):
        self.alimentar(clap.silencio(0.5), clap.palma(), clap.silencio(1.0))
        self.assertEqual(self.gestos, 0)

    def test_voz_alta_sustentada_nao_dispara(self):
        """O que separa palma de grito é o DECAIMENTO, não o volume."""
        self.alimentar(
            clap.silencio(0.4),
            clap.voz_alta(0.5),
            clap.silencio(0.2),
            clap.voz_alta(0.5),
            clap.silencio(0.3),
        )
        self.assertEqual(self.gestos, 0)

    def test_silencio_puro_nao_dispara(self):
        self.alimentar(clap.silencio(3.0))
        self.assertEqual(self.gestos, 0)

    def test_sala_barulhenta_nao_vira_gesto(self):
        self.alimentar(clap.silencio(3.0, ruido=2500))
        self.assertEqual(self.gestos, 0)

    def test_palmas_muito_juntas_sao_eco_da_mesma(self):
        self.alimentar(
            clap.silencio(0.4), clap.palma(), clap.silencio(0.01),
            clap.palma(), clap.silencio(0.5),
        )
        self.assertEqual(self.gestos, 0)

    def test_palmas_muito_separadas_nao_sao_um_gesto(self):
        self.alimentar(
            clap.silencio(0.4), clap.palma(), clap.silencio(1.5),
            clap.palma(), clap.silencio(0.4),
        )
        self.assertEqual(self.gestos, 0)


class TestDescanso(TesteBase):
    def test_aplauso_longo_conta_como_um_gesto_so(self):
        """Bater palmas seguidas não pode disparar cinco vezes."""
        pedacos = [clap.silencio(0.4)]
        for _ in range(6):
            pedacos += [clap.palma(), clap.silencio(0.2)]
        self.alimentar(*pedacos)
        self.assertEqual(self.gestos, 1)

    def test_dois_gestos_separados_contam_duas_vezes(self):
        um = [clap.palma(), clap.silencio(0.2), clap.palma()]
        self.alimentar(
            clap.silencio(0.4), *um,
            clap.silencio(2.0),  # passa do descanso
            *um, clap.silencio(0.3),
        )
        self.assertEqual(self.gestos, 2)


class TestRobustez(TesteBase):
    def test_bloco_com_numero_impar_de_bytes_nao_quebra(self):
        # Uma amostra int16 tem 2 bytes; um bloco truncado não pode explodir.
        self.det.alimentar(clap.silencio(0.1)[:-1])

    def test_bloco_vazio_nao_quebra(self):
        self.assertFalse(self.det.alimentar(b""))

    def test_callback_que_falha_nao_derruba_o_audio(self):
        def explode():
            raise RuntimeError("janela fechada")

        det = clap.DetectorDePalmas(taxa=16000, ao_detectar=explode)
        det.alimentar(
            clap.silencio(0.4) + clap.palma() + clap.silencio(0.2) + clap.palma()
        )  # não deve levantar

    def test_palma_fraca_de_longe_ainda_conta(self):
        fraca = lambda: clap.palma(amplitude=6000.0)  # noqa: E731
        self.alimentar(
            clap.silencio(0.5), fraca(), clap.silencio(0.2), fraca(),
            clap.silencio(0.3),
        )
        self.assertEqual(self.gestos, 1)


class TestCusto(TesteBase):
    def test_processar_e_barato_o_bastante_para_o_fluxo_ao_vivo(self):
        """Precisa custar bem menos que o tempo real, senão engasga o Vosk."""
        import time

        audio = clap.silencio(10.0)
        inicio = time.perf_counter()
        self.det.alimentar(audio)
        gasto = time.perf_counter() - inicio
        # 10 s de áudio processados em muito menos que 10 s.
        self.assertLess(gasto, 1.0, f"{gasto:.2f}s para 10s de áudio")


if __name__ == "__main__":
    unittest.main()
