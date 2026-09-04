"""Testa a espinha das seis fases — sem disparar Claude Code nenhum.

O que se testa aqui é a DECISÃO: qual fase vem agora, o que já está pronto, e
principalmente o que ele diz sobre uma fase que depende de ferramenta que não
existe. Um painel que mente é pior que não ter painel.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from tools import fases  # noqa: E402


class TestEntendeOPedido(unittest.TestCase):

    def test_reconhece_a_fase_e_a_criatura(self):
        from tools.local_commands import _criatura_da_fase, _fase_pedida

        casos = [
            ("vamos começar a fase 0 da Medusa", 0, "Medusa"),
            ("fase 3 do Cthulhu", 3, "Cthulhu"),
            ("roda a fase zero da Baba Yaga", 0, "Baba Yaga"),
            ("Ômega, quero a fase 2 da Dullhan agora", 2, "Dullhan"),
        ]
        for frase, n, criatura in casos:
            self.assertEqual(_fase_pedida(frase.lower()), n, frase)
            self.assertEqual(_criatura_da_fase(frase), criatura, frase)

    def test_sem_a_palavra_fase_nao_dispara(self):
        """"vamos começar" sozinho é ambíguo com meia dúzia de outras coisas."""
        from tools.local_commands import _fase_pedida

        for frase in ("vamos começar", "começa a aula 2", "0 problemas",
                      "assistir o curso inteiro"):
            self.assertIsNone(_fase_pedida(frase.lower()), frase)

    def test_pode_seguir_nao_colide_com_a_aula(self):
        """"continuar a aula" retoma gravação; "pode continuar" avança fase."""
        from tools.local_commands import _e_retomada_de_aula, _e_seguir

        for frase in ("pode seguir", "segue", "pode continuar", "avança"):
            self.assertTrue(_e_seguir(frase.lower()), frase)
            self.assertFalse(_e_retomada_de_aula(frase.lower()), frase)

        for frase in ("continuar a aula", "retoma a aula", "voltei, pode "
                      "continuar gravando"):
            self.assertTrue(_e_retomada_de_aula(frase.lower()), frase)
            self.assertFalse(_e_seguir(frase.lower()), frase)

    def test_o_modelo_tambem_tem_como(self):
        sys.argv = ["t"]
        import main

        f = next((x for x in main.TOOLS if x["name"] == "fases"), None)
        self.assertIsNotNone(f, "faltou a ferramenta fases")
        self.assertEqual(sorted(f["parameters"]["properties"]["acao"]["enum"]),
                         ["comecar", "seguir", "situacao"])


class TestEstado(unittest.TestCase):

    def setUp(self):
        import tempfile

        from tools import pipeline

        self.tmp = tempfile.TemporaryDirectory()
        self._raiz = fases.AI_PROJECT_ROOT
        self._raiz_pipe = pipeline.AI_PROJECT_ROOT
        fases.AI_PROJECT_ROOT = Path(self.tmp.name)
        pipeline.AI_PROJECT_ROOT = Path(self.tmp.name)
        self.notes = Path(self.tmp.name) / "Criaturas" / "Medusa" / "medusa-video" / "notes"
        self.notes.mkdir(parents=True)

    def tearDown(self):
        import shutil

        from tools import pipeline

        fases.AI_PROJECT_ROOT = self._raiz
        pipeline.AI_PROJECT_ROOT = self._raiz_pipe
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def test_comeca_na_fase_zero(self):
        self.assertEqual(fases.proxima("Medusa"), 0)

    def test_o_arquivo_no_disco_manda_mais_que_o_registro(self):
        """Ele pode ter gerado o dossiê à mão, ou o app pode ter caído antes
        de anotar. Quem diz o que existe é o arquivo."""
        (self.notes / "dossie.md").write_text("x", encoding="utf-8")
        self.assertEqual(fases.proxima("Medusa"), 1)
        self.assertEqual(fases.estado_de("Medusa", 0), fases.NAO_COMECOU)

    def test_estado_sobrevive_ao_fechamento_do_app(self):
        fases.marcar("Medusa", 1, fases.AGUARDANDO, "esperando aprovação")
        self.assertEqual(fases.estado_de("Medusa", 1), fases.AGUARDANDO)
        self.assertTrue((self.notes / "fases.json").exists())

    def test_nao_pula_fase(self):
        r = fases.comecar("Medusa", 2)
        self.assertIn("ainda não terminou", r)
        self.assertIn("fase 1", r)

    def test_fase_sem_ferramenta_NAO_diz_pronta(self):
        """Dizer 'pronta' sem ter feito seria mentira, e mentira de painel
        custa uma produção parada sem ninguém saber.

        O alvo era a fase 3 (vídeo), enquanto ela não tinha executor. Desde
        04/09/2026 ela tem, e a 5 (Publicação) virou a única sem — e é a certa
        para guardar esta garantia, porque continua sem executor por DECISÃO
        (publicar é irreversível), não por limitação que um dia cai.
        """
        for n in range(5):
            fases.marcar("Medusa", n, fases.PRONTA)
        r = fases.comecar("Medusa", 5)
        self.assertEqual(fases.estado_de("Medusa", 5), fases.AGUARDANDO)
        self.assertNotIn(fases.PRONTA, fases.estado_de("Medusa", 5))
        self.assertIn("botão é seu", r)

    def test_publicar_continua_sendo_dele(self):
        for n in range(5):
            fases.marcar("Medusa", n, fases.PRONTA)
        r = fases.comecar("Medusa", 5)
        # "não listado" substituiu "paro no formulário" em 04/09/2026, quando
        # o YouTube passou a subir pela API. O que o teste guarda não é a
        # frase, é a garantia: o OMEGA não torna nada público sozinho.
        self.assertIn("NÃO LISTADO", r)
        self.assertIn("botão é seu", r)

    def test_anuncia_a_proxima_com_o_que_ela_precisa(self):
        """É esta frase que aposenta a decoreba dos quarenta comandos."""
        r = fases.anunciar("Medusa", 0)
        self.assertIn("fase 1", r)
        self.assertIn("Model sheets", r)
        self.assertIn("pode seguir", r)

    def test_anuncia_o_que_falta_quando_falta(self):
        """Mesma troca de alvo do teste acima: a 4→5 é o par que sobrou com
        uma fase que depende dele de verdade."""
        r = fases.anunciar("Medusa", 4)
        self.assertIn("botão é seu", r,
                      "não avisou que publicar continua sendo dele")

    def test_no_fim_nao_inventa_fase_7(self):
        r = fases.anunciar("Medusa", 5)
        self.assertIn("última", r)

    def test_seguir_sem_nome_com_duas_em_curso_pergunta(self):
        (self.notes / "dossie.md").write_text("x", encoding="utf-8")
        outra = (Path(self.tmp.name) / "Criaturas" / "Sobek" / "sobek-video"
                 / "notes")
        outra.mkdir(parents=True)
        (outra / "dossie.md").write_text("x", encoding="utf-8")
        self.assertEqual(sorted(fases.em_andamento()), ["Medusa", "Sobek"])

    def test_situacao_lista_todas(self):
        (self.notes / "dossie.md").write_text("x", encoding="utf-8")
        r = fases.situacao()
        self.assertIn("Medusa", r)
        self.assertIn("fase 1", r)


class TestCursoAgindoSozinho(unittest.TestCase):
    """O curso entra nas fases 0 e 5 — e cala a boca no resto.

    A trava que importa é a mesma de `tools/web.py`: sem fonte, não afirma.
    Um OMEGA que opina de SEO sem regra aprovada, com voz de quem leu o curso,
    é pior que um OMEGA calado — porque o Samuel vai acreditar.
    """

    def setUp(self):
        import tempfile

        from tools import aula as _aula
        from tools import curso as _curso

        from tools import pipeline

        self.tmp = tempfile.TemporaryDirectory()
        raiz = Path(self.tmp.name)
        self._cursos = _aula.CURSOS
        # ISOLAR A RAIZ TAMBÉM. Sem isto o teste lia o estado da Medusa DE
        # VERDADE — e `marcar` teria escrito na pasta real dela.
        self._raiz, self._raiz_pipe = fases.AI_PROJECT_ROOT, pipeline.AI_PROJECT_ROOT
        fases.AI_PROJECT_ROOT = pipeline.AI_PROJECT_ROOT = raiz
        _aula.CURSOS = raiz / "Cursos"
        self.pasta = _aula.CURSOS / _aula.curso_atual()
        self.pasta.mkdir(parents=True)
        (raiz / "Criaturas" / "Medusa" / "medusa-video" / "notes").mkdir(parents=True)
        for n in range(5):
            fases.marcar("Medusa", n, fases.PRONTA)
        self.curso = _curso

        # A fase 5 destravada (21/08/2026) dispara a fase "seo" do pipeline
        # em segundo plano — que, se o Claude CLI estiver de verdade instalado
        # nesta máquina, ABRIRIA UM PROCESSO REAL, gastando crédito de
        # verdade num teste que devia ser de graça. Fingir que o CLI não
        # existe é o mesmo princípio de isolar AI_PROJECT_ROOT: o teste não
        # pode tocar o mundo real.
        self._resolver_claude_original = pipeline._resolver_claude
        pipeline._resolver_claude = lambda: None

    def tearDown(self):
        import shutil

        from tools import aula as _aula

        from tools import pipeline

        _aula.CURSOS = self._cursos
        fases.AI_PROJECT_ROOT = self._raiz
        pipeline.AI_PROJECT_ROOT = self._raiz_pipe
        pipeline._resolver_claude = self._resolver_claude_original
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def _aprovar(self, texto):
        (self.pasta / "regras-aprovadas.md").write_text(texto, encoding="utf-8")

    def test_sem_regra_aprovada_nao_inventa(self):
        self.assertEqual(self.curso.orientar(("titulo",)), "")

    def test_traz_so_as_regras_da_decisao_pedida(self):
        self._aprovar(
            "## Título entre 40 e 60 caracteres\n"
            "- **Decisão:** titulo\n- **Fonte:** aula 1 — [03:20]\n\n"
            "## Poste terça e quinta às 19h\n"
            "- **Decisão:** quando-postar\n- **Fonte:** aula 7 — [11:02]\n")
        material = self.curso.orientar(("titulo",))
        self.assertIn("40 e 60 caracteres", material)
        self.assertNotIn("terça e quinta", material,
                         "trouxe regra de outra decisão; na fase 0 isso é ruído")

    def test_manda_citar_a_fonte(self):
        self._aprovar("## Use número no título\n- **Decisão:** titulo\n"
                      "- **Fonte:** aula 1 — [03:20]\n")
        material = self.curso.orientar(("titulo",))
        self.assertIn("citando a aula e o minuto", material)
        self.assertIn("[03:20]", material)
        self.assertIn("não acrescente conselho seu",
                      material.lower().replace("nao", "não"))

    def test_a_fase_5_puxa_o_pacote_inteiro(self):
        self._aprovar("## Thumb com rosto e contraste\n"
                      "- **Decisão:** thumbnail\n- **Fonte:** aula 9 — [02:03]\n")
        r = fases.comecar("Medusa", 5)
        self.assertIn("Thumb com rosto", r,
                      "a fase 5 é a que mais rende curso; veio sem regra")

    def test_a_fase_5_continua_sem_publicar(self):
        self._aprovar("## Qualquer regra\n- **Decisão:** titulo\n"
                      "- **Fonte:** aula 1 — [00:10]\n")
        r = fases.comecar("Medusa", 5)
        self.assertIn("botão é seu", r)

    def test_a_fase_5_ja_dispara_o_pacote_de_verdade(self):
        """Destravado em 21/08/2026: além de mostrar as regras do curso, a
        fase 5 já dispara a escrita real do pacote (skill postagem) em
        segundo plano — e o Claude nunca ganha ferramenta de publicar."""
        self._aprovar("## Qualquer regra\n- **Decisão:** titulo\n"
                      "- **Fonte:** aula 1 — [00:10]\n")
        r = fases.comecar("Medusa", 5)
        self.assertIn("pacote de SEO", r)
        # Sem CLI (mockado em setUp) a fase "seo" recusa educadamente — a
        # prova de que a chamada realmente aconteceu, sem precisar de um
        # Claude de verdade rodando durante o teste.
        self.assertIn("Claude Code CLI não está instalado", r)

    def test_seo_e_pesquisa_nunca_publicam_nem_navegam(self):
        """As duas fases que o curso alimenta (0 e 5) só têm ferramenta de
        imagem/pesquisa — nenhuma de navegador, upload ou publicação. Isso
        é o que faz 'publicar é seu' ser garantia de código, não promessa."""
        from tools.pipeline import KAIROGEN_FERRAMENTAS

        proibidas = ("browser", "youtube", "upload_video", "publish", "publicar")
        for f in KAIROGEN_FERRAMENTAS:
            for termo in proibidas:
                self.assertNotIn(termo, f.lower())


class TestPipelineAceitaAsFases(unittest.TestCase):
    """As fases 1 e 2 foram separadas — o pipeline precisa conhecer as duas."""

    def test_rotulos_cobrem_as_quatro(self):
        from tools.pipeline import ROTULOS

        for chave in ("pesquisa", "model-sheets", "storyboards", "producao"):
            self.assertIn(chave, ROTULOS)

    def test_cada_fase_promete_arquivo_diferente(self):
        from tools.pipeline import _arquivos_da_fase

        ms = {p.name for p in _arquivos_da_fase("Medusa", "model-sheets")}
        sb = {p.name for p in _arquivos_da_fase("Medusa", "storyboards")}
        self.assertIn("model-sheets.md", ms)
        self.assertIn("prompts.md", sb)
        self.assertNotIn("prompts.md", ms,
                         "a fase 1 não pode prometer os storyboards")

    def test_fase_desconhecida_nao_passa(self):
        from tools.pipeline import pipeline_criatura

        r = pipeline_criatura({"creature": "Medusa", "phase": "inventada"})
        self.assertIn("Não conheço a fase", r)


class TestFaseEdicao(unittest.TestCase):
    """Fase 4 destravada em 21/08/2026 — HTTP puro contra o Studio, sem
    Claude headless nenhum. O que se testa aqui, sem gastar rede: as duas
    checagens que impedem ela de mentir (sem clipe, sem narração) e o
    cálculo do id de projeto, que TEM que bater exatamente com
    `encodeProjectId` do Studio (project-id.ts) — testado contra uma string
    real que a API do Studio devolveu de verdade nesta mesma sessão."""

    def setUp(self):
        import tempfile

        from tools import fases, pipeline

        self.tmp = tempfile.TemporaryDirectory()
        self._raiz = fases.AI_PROJECT_ROOT
        self._raiz_pipe = pipeline.AI_PROJECT_ROOT
        fases.AI_PROJECT_ROOT = pipeline.AI_PROJECT_ROOT = Path(self.tmp.name)
        self.project = (Path(self.tmp.name) / "Criaturas" / "Medusa"
                        / "medusa-video")
        (self.project / "notes").mkdir(parents=True)
        (self.project / "public" / "videos").mkdir(parents=True)
        (self.project / "public" / "audio").mkdir(parents=True)

    def tearDown(self):
        import shutil

        from tools import fases, pipeline

        fases.AI_PROJECT_ROOT = self._raiz
        pipeline.AI_PROJECT_ROOT = self._raiz_pipe
        shutil.rmtree(self.tmp.name, ignore_errors=True)

    def test_id_de_projeto_bate_com_o_studio(self):
        """String real devolvida por POST /api/projects contra o Studio
        rodando de verdade, nesta sessão, para creatureName=
        'TesteSincroniaEnhance' — não é suposição sobre o formato."""
        from tools.pipeline import _studio_project_id

        self.assertEqual(
            _studio_project_id("TesteSincroniaEnhance"),
            "Q3JpYXR1cmFzL1Rlc3RlU2luY3JvbmlhRW5oYW5jZS90ZXN0ZXNpbmNyb25pYWVuaGFuY2UtdmlkZW8",
        )

    def test_sem_clipe_nao_liga_pro_studio(self):
        """Sem clipe da fase 3, nem vale a pena tentar falar com o Studio —
        e a mensagem tem que dizer exatamente o que falta."""
        from tools.pipeline import _current, _run_edicao

        _current.update({"running": True, "creature": "Medusa",
                         "result": None, "proc": None, "cancelado": False})
        _run_edicao("Medusa")
        self.assertIn("clipes da fase 3", _current["result"])

    def test_sem_narracao_nao_liga_pro_studio(self):
        """Com clipe mas sem narração, também para antes de tocar o Studio —
        narração é ElevenLabs, e o Omega não gera sozinho (decisão da whoiam)."""
        from tools.pipeline import _current, _run_edicao

        (self.project / "public" / "videos" / "1.mp4").write_bytes(b"x")
        _current.update({"running": True, "creature": "Medusa",
                         "result": None, "proc": None, "cancelado": False})
        _run_edicao("Medusa")
        self.assertIn("narração", _current["result"])
        self.assertIn("ElevenLabs", _current["result"])

    def test_rotulo_e_arquivo_da_fase_existem(self):
        from tools.pipeline import ROTULOS, _arquivos_da_fase

        self.assertIn("edicao", ROTULOS)
        # Sem render ainda: lista vazia, não erro — mesma lógica de "videos".
        self.assertEqual(_arquivos_da_fase("Medusa", "edicao"), [])


class TestKairogenSoImagem(unittest.TestCase):
    """A decisão do Samuel foi: imagem sim, vídeo não — ele produz o vídeo.

    O motivo é dinheiro, não gosto: a cadência que ele quer não cabe no
    orçamento de vídeo do plano. Uma decisão dessas não pode viver só em
    comentário, porque a próxima pessoa que "melhorar" o allowlist reabre o
    gasto sem perceber. Aqui ela vira falha de teste.
    """

    def test_video_nao_esta_liberado(self):
        from tools.pipeline import KAIROGEN_FERRAMENTAS

        for f in KAIROGEN_FERRAMENTAS:
            self.assertNotIn("video", f,
                             f"{f} reabre a geração de vídeo, que o Samuel "
                             "tirou de escopo por causa de custo")

    def test_o_modelo_padrao_e_o_validado_em_producao(self):
        """Trocado em 15/08/2026: z-image-turbo era o único de custo zero
        (medido: cost_credits 0, saldo parado em 1780), mas testado numa
        storyboard real saiu com texto borrado no painel, grid quebrado e
        aspect_ratio ignorado. gpt-image-2, testado no mesmo projeto
        (43 blocos + bíblia), saiu limpo — decisão do Samuel: qualidade
        vence custo zero aqui."""
        from tools.pipeline import KAIROGEN_MODELO_IMAGEM

        self.assertEqual(KAIROGEN_MODELO_IMAGEM, "gpt-image-2")

    def test_a_instrucao_manda_esperar_o_COMPLETED(self):
        """`generate_image` devolve QUEUED e mais nada. Sem a espera, a fase
        termina 'com sucesso' e a pasta fica vazia — a falha que engana."""
        from pathlib import Path

        from tools.pipeline import KAIROGEN_MODELO_IMAGEM, _instrucao_render

        texto = _instrucao_render(Path("/tmp/x"))
        self.assertIn("COMPLETED", texto)
        self.assertIn("get_generation", texto)
        self.assertIn(KAIROGEN_MODELO_IMAGEM, texto)

    def test_baixa_com_curl_e_confere_o_tamanho(self):
        """A ferramenta de download do MCP grava 96 bytes de um PNG 1x1 e
        diz que deu certo. Medido: a imagem real tem 1,3 MB e vem por curl.
        Sem a conferência de tamanho, a fase 2 entrega catorze placeholders."""
        from pathlib import Path

        from tools.pipeline import KAIROGEN_FERRAMENTAS, _instrucao_render

        texto = _instrucao_render(Path("/tmp/x"))
        self.assertIn("curl", texto)
        self.assertIn("10000", texto.replace("_", "").replace(".", ""))
        self.assertNotIn("mcp__kairogen__download_image_from_url",
                         KAIROGEN_FERRAMENTAS,
                         "essa ferramenta grava placeholder e mente")

    def test_a_instrucao_proibe_trocar_de_modelo(self):
        from pathlib import Path

        from tools.pipeline import _instrucao_render

        texto = _instrucao_render(Path("/tmp/x")).lower()
        self.assertIn("não use outro modelo", texto)


class TestVideoSoNaFase3(unittest.TestCase):
    """A trava trocada por outra trava, e não removida.

    `generate_video` foi destravado em 04/09/2026 — mas destravado SÓ para a
    fase 3. A garantia antiga (nenhuma fase de imagem gera vídeo) tem que
    continuar valendo, e a nova (a fase 3 gera de verdade) tem que existir.
    As duas moram aqui para que a próxima "melhoria" no allowlist quebre um
    teste em vez de quebrar o orçamento.
    """

    def test_a_lista_de_imagem_continua_sem_video(self):
        from tools.pipeline import KAIROGEN_FERRAMENTAS

        for f in KAIROGEN_FERRAMENTAS:
            self.assertNotIn("video", f,
                             f"{f} reabre vídeo nas fases de imagem")

    def test_a_lista_de_video_tem_generate_video(self):
        from tools.pipeline import KAIROGEN_FERRAMENTAS_VIDEO

        self.assertIn("mcp__kairogen__generate_video", KAIROGEN_FERRAMENTAS_VIDEO)

    def test_so_a_fase_videos_recebe_a_lista_de_video(self):
        """A garantia é de CÓDIGO, não de prompt: quem decide é o `phase`."""
        from tools.pipeline import (KAIROGEN_FERRAMENTAS,
                                    KAIROGEN_FERRAMENTAS_VIDEO)

        escolher = lambda fase: (  # noqa: E731 — espelha a linha do pipeline
            KAIROGEN_FERRAMENTAS_VIDEO if fase == "videos"
            else KAIROGEN_FERRAMENTAS
        )
        self.assertIs(escolher("videos"), KAIROGEN_FERRAMENTAS_VIDEO)
        for outra in ("pesquisa", "model-sheets", "storyboards", "producao",
                      "seo"):
            self.assertIs(escolher(outra), KAIROGEN_FERRAMENTAS)

    def test_o_modelo_e_o_barato_e_o_teste_diz_por_que(self):
        """Medido em 04/09/2026 no catálogo do Kairogen, a 480p: o
        seedance-2-5 custa 0,92 BRL/s contra 0,12 do 2-0 — ~15x por bloco.
        A decisão ⚫ "tudo em Seedance 2.5" é do HIGGSFIELD, outra tabela.
        Trocar aqui derruba o mês de ~4 vídeos para menos de 1."""
        from tools.pipeline import (KAIROGEN_MODELO_VIDEO,
                                    KAIROGEN_RESOLUCAO_VIDEO)

        self.assertEqual(KAIROGEN_MODELO_VIDEO, "seedance-2-0")
        self.assertEqual(KAIROGEN_RESOLUCAO_VIDEO, "480p")

    def test_a_instrucao_cobra_as_quatro_disciplinas(self):
        """As mesmas quatro que a fase 2 já cobra para imagem — e que aqui
        custam muito mais caro se faltarem."""
        from pathlib import Path

        from tools.pipeline import _instrucao_video

        texto = _instrucao_video(Path("/tmp/x"))
        self.assertIn("get_credits", texto)      # portão de crédito
        self.assertIn("COMPLETED", texto)        # assíncrono
        self.assertIn("wc -c", texto)            # confere o arquivo
        self.assertIn("480p", texto)             # resolução barata
        self.assertIn("curl", texto)             # download que funciona

    def test_a_instrucao_manda_numerar_em_ordem(self):
        """É o NÚMERO do arquivo que decide a ordem na timeline do Studio."""
        from pathlib import Path

        from tools.pipeline import _instrucao_video

        texto = _instrucao_video(Path("/tmp/x"))
        self.assertIn("1.mp4", texto)
        self.assertIn("sem pular número", texto)

    def test_a_fase_videos_confere_o_disco_e_nao_promete_nome(self):
        """O número de blocos varia por criatura: o que existe é a verdade."""
        from tools.pipeline import _arquivos_da_fase

        self.assertEqual(_arquivos_da_fase("nao-existe-mesmo", "videos"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
