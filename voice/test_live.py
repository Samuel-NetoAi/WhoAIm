"""Testa a voz em tempo real do OMEGA (Live API do Gemini).

Não precisa de microfone nem de alto-falante: o áudio de entrada vem dos
arquivos que o `test_escuta.py` gera, e a saída é contada em bytes em vez de
tocada. É o que permite rodar isto do terminal.

O que se verifica, em ordem de importância:
  1. a sessão abre nesta conta — foi o que esteve bloqueado até 06/08/2026;
  2. ele ENTENDE áudio de verdade, sem transcrição no meio;
  3. ele CHAMA as ferramentas do canal a partir da voz;
  4. quando a sessão morre, o motor local assume — sem isto o OMEGA fica
     mudo toda vez que a cota gratuita estourar, e ela estoura.

O item 4 é o que mais importa no dia a dia e é o único que não depende da
rede: a queda é testada forçando a falha, não esperando ela acontecer.
"""

from __future__ import annotations

import asyncio
import base64
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import websockets  # noqa: E402

import live_engine  # noqa: E402

CONFIG = Path(__file__).resolve().parent / "config" / "api_keys.json"


def chave() -> str:
    try:
        return json.loads(CONFIG.read_text(encoding="utf-8")).get("gemini_api_key", "")
    except Exception:  # noqa: BLE001
        return ""


def audio_de_teste() -> bytes | None:
    """'Ômega, me mostra a pesquisa da Medusa' — gerado pelo test_escuta."""
    caminho = Path(__file__).resolve().parent / "_audio_teste" / "01.wav"
    if not caminho.exists():
        return None
    from test_escuta import _ler_wav_16k

    return _ler_wav_16k(caminho)


class UIFalsa:
    muted = False

    def __init__(self):
        self.log = []

    def write_log(self, m):
        self.log.append(m)

    def set_state(self, *_):
        pass


class TestQueda(unittest.TestCase):
    """A parte que não depende da rede — e a que salva o dia a dia."""

    def _motor(self, **kw):
        return live_engine.LiveEngine(
            gemini_key=kw.get("chave", "invalida"),
            instructions="Você é o OMEGA.",
            tool_executor=lambda n, a: "ok",
            ui=UIFalsa(),
            tools=[{"name": "exibir", "description": "mostra",
                    "parameters": {"type": "object", "properties": {}}}],
        )

    def test_chave_invalida_cai_para_o_local(self):
        m = self._motor()
        m._ao_capturar = lambda *a: None  # sem microfone neste ambiente
        ok = m.run()
        self.assertFalse(ok, "deveria desistir e deixar o motor local assumir")
        self.assertTrue(m.motivo_da_queda, "precisa dizer POR QUE caiu")

    def test_ferramentas_viram_declaracoes_do_gemini(self):
        d = self._motor()._declaracoes()
        self.assertEqual(d[0]["name"], "exibir")
        self.assertIn("parameters", d[0])

    def test_projetos_reais_entram_na_instrucao(self):
        self.assertIn("PROJETOS QUE EXISTEM AGORA", self._motor()._instrucoes())

    def test_barge_in_descarta_o_que_nao_foi_tocado(self):
        """Interromper tem que calar AGORA, não daqui a alguns segundos."""
        m = self._motor()
        for _ in range(50):
            m._saida.put(b"\x00" * 1200)
        m._falando.set()
        m._descartar_saida()
        self.assertTrue(m._saida.empty(), "sobrou áudio para tocar depois do corte")
        self.assertFalse(m._falando.is_set())


@unittest.skipUnless(chave(), "sem chave do Gemini no config")
class TestComRede(unittest.TestCase):
    def _conversar(self, pcm: bytes, ferramentas: list[dict]) -> dict:
        """Manda áudio, devolve o que ele ouviu, disse e chamou."""
        resultado = {"ouviu": "", "disse": "", "ferramentas": [], "bytes": 0}

        async def rodar():
            setup = {"setup": {
                "model": live_engine.MODELO,
                "generationConfig": {"responseModalities": ["AUDIO"]},
                "systemInstruction": {"parts": [{"text":
                    "Você é o OMEGA do canal WhoIAm. Para mostrar pesquisa, "
                    "roteiro ou cenas de uma criatura, CHAME a ferramenta "
                    "exibir. Responda em português, curto."}]},
                "tools": [{"functionDeclarations": ferramentas}],
                "inputAudioTranscription": {},
                "outputAudioTranscription": {},
            }}
            url = f"{live_engine.URL}?key={chave()}"
            async with websockets.connect(url, max_size=None, open_timeout=30) as ws:
                await ws.send(json.dumps(setup))
                self.assertIn("setupComplete",
                              json.loads(await asyncio.wait_for(ws.recv(), 30)))
                for i in range(0, len(pcm), 3200):
                    await ws.send(json.dumps({"realtimeInput": {"audio": {
                        "mimeType": "audio/pcm;rate=16000",
                        "data": base64.b64encode(pcm[i:i + 3200]).decode()}}}))
                await ws.send(json.dumps(
                    {"realtimeInput": {"audioStreamEnd": True}}))

                for _ in range(200):
                    d = json.loads(await asyncio.wait_for(ws.recv(), 40))
                    if "toolCall" in d:
                        for f in d["toolCall"]["functionCalls"]:
                            resultado["ferramentas"].append(f["name"])
                            await ws.send(json.dumps({"toolResponse": {
                                "functionResponses": [{
                                    "id": f["id"], "name": f["name"],
                                    "response": {"result": "exibido na tela"}}]}}))
                        continue
                    sc = d.get("serverContent", {})
                    resultado["ouviu"] += sc.get("inputTranscription", {}).get("text", "")
                    resultado["disse"] += sc.get("outputTranscription", {}).get("text", "")
                    for p in sc.get("modelTurn", {}).get("parts", []):
                        if "inlineData" in p:
                            resultado["bytes"] += len(
                                base64.b64decode(p["inlineData"]["data"]))
                    if sc.get("turnComplete") and resultado["bytes"]:
                        return

        asyncio.run(rodar())
        return resultado

    def test_entende_voz_e_chama_a_ferramenta(self):
        pcm = audio_de_teste()
        if pcm is None:
            self.skipTest("rode `python test_escuta.py` uma vez para gerar o áudio")

        r = self._conversar(pcm, [{
            "name": "exibir",
            "description": "Mostra pesquisa, roteiro ou cenas de uma criatura.",
            "parameters": {"type": "object", "properties": {
                "tipo": {"type": "string"}, "criatura": {"type": "string"}}},
        }])

        print(f"\n   ouviu     : {r['ouviu'].strip()}")
        print(f"   respondeu : {r['disse'].strip()[:80]}")
        print(f"   ferramenta: {r['ferramentas']}")
        print(f"   audio     : {r['bytes']} bytes "
              f"({r['bytes']/2/live_engine.TAXA_SAIDA:.1f}s de fala)")

        self.assertIn("medusa", r["ouviu"].lower(),
                      "não entendeu o nome da criatura no áudio")
        self.assertGreater(r["bytes"], 0, "não respondeu falando")
        self.assertIn("exibir", r["ferramentas"],
                      "ouviu o pedido mas não chamou a ferramenta")


if __name__ == "__main__":
    unittest.main(verbosity=2)
