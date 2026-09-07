"""Testes do publicador — nenhum toca a rede nem gasta cota.

O que se testa aqui é o que o código PROMETE quando a rede não responde: que a
flag de IA vai no corpo, que erro de auditoria vira mensagem legível, e que
'não configurado' falha dizendo o passo que falta em vez de estourar.
"""

import json
import sys
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import publicar as p  # noqa: E402

ok = 0


def verifica(condicao, oque):
    global ok
    assert condicao, f"FALHOU: {oque}"
    ok += 1
    print(f"  ok  {oque}")


def _video(**kw):
    base = dict(arquivo=Path("x.mp4"), titulo="t", descricao="d", tags=["a"],
                conteudo_sintetico=True)
    return p.Video(**{**base, **kw})


# --- a flag de IA, que e o ponto que nao pode falhar em silencio ---
c = _video().corpo()
verifica(c["status"]["containsSyntheticMedia"] is True,
         "conteudo sintetico=True vai como containsSyntheticMedia no corpo")
verifica(_video(conteudo_sintetico=False).corpo()["status"]["containsSyntheticMedia"] is False,
         "conteudo sintetico=False tambem e explicito, nao omitido")

import inspect  # noqa: E402
verifica("conteudo_sintetico" in inspect.signature(p.Video).parameters
         and inspect.signature(p.Video).parameters["conteudo_sintetico"].default
         is inspect.Parameter.empty,
         "conteudo_sintetico NAO tem default — quem chama e obrigado a declarar")

# --- padroes que refletem a regra real do YouTube ---
verifica(c["status"]["privacyStatus"] == "private",
         "privacidade padrao e private (o video nasce privado ate a auditoria)")
verifica(_video(titulo="x" * 300).corpo()["snippet"]["title"] == "x" * 100,
         "titulo e cortado em 100 caracteres antes de ir para a API")

# --- traducao de erro: os tres 403 pedem reacao diferente ---
class _Http(Exception):
    def __init__(self, motivo):
        self.content = json.dumps({"error": {"errors": [{"reason": motivo}]}}).encode()

for motivo, pedaco in (("privacyError", "auditoria"),
                       ("uploadLimitExceeded", "15+"),
                       ("quotaExceeded", "100 uploads")):
    verifica(pedaco in str(p._traduzir(_Http(motivo))),
             f"{motivo} vira mensagem que diz o que fazer")

verifica(isinstance(p._traduzir(_Http("outra_coisa")), _Http),
         "motivo desconhecido volta o erro original, sem inventar explicacao")

# --- 'nao configurado' e um fato diferente de 'quebrou' ---
with mock.patch.object(p, "_dpapi_ler", return_value=None):
    try:
        p.credenciais(interativo=False)
        verifica(False, "deveria ter levantado FaltaConfigurar")
    except p.FaltaConfigurar as e:
        verifica("autorizar" in str(e), "sem token, diz o comando exato que falta rodar")

# Path e imutavel: troca-se o atributo do MODULO por um caminho que nao existe,
# em vez de tentar remendar o metodo .exists() da instancia.
INEXISTENTE = Path(__file__).resolve().parent / "nao-existe-de-proposito.json"
with mock.patch.object(p, "_dpapi_ler", return_value=None), \
     mock.patch.object(p, "SEGREDO_CLIENTE", INEXISTENTE):
    try:
        p.credenciais(interativo=True)
        verifica(False, "deveria ter levantado FaltaConfigurar")
    except p.FaltaConfigurar as e:
        verifica("NÃO cole o conteúdo dele no chat" in str(e),
                 "sem client_secret, avisa para nao colar o segredo no chat")

# --- a cli obriga a declarar mídia sintetica ---
for args in (["subir", "v.mp4", "--titulo", "t"],
             ["subir", "v.mp4", "--titulo", "t", "--sintetico", "--nao-sintetico"]):
    verifica(p.main(args) == 2,
             f"cli recusa quando a declaracao de IA esta ausente ou dupla ({len(args)} args)")

# --- verificar() nao explode quando nada esta configurado ---
with mock.patch.object(p, "SEGREDO_CLIENTE", INEXISTENTE):
    s = p.verificar()
    verifica(s["erro"] and not s["autorizacao valida"],
             "verificar() devolve diagnostico em vez de excecao")

print(f"\n{ok} verificacoes, todas passaram")
