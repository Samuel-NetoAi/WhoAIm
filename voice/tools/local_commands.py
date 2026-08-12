"""Comandos de texto que rodam 100% local — sem OpenAI, sem internet.

Existem para que o Omega seja útil mesmo sem créditos na conta: ler o que as
skills geraram, listar projetos, abrir o vídeo renderizado, disparar render.
Tudo isso é arquivo local + a API do Studio em localhost, nada externo.

Quando há créditos, a voz continua sendo o caminho principal; estes comandos
ficam como atalho digitado. `handle()` devolve None quando não reconhece o
texto, e aí quem chama repassa para o modelo de voz.
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher
import unicodedata
from pathlib import Path

from .studio import _find_project, _get_projects, _ensure_studio, _studio_alive, STUDIO_URL
from .studio import studio_control
# A raiz vem do pipeline para haver UMA fonte de verdade: ela respeita
# AI_PROJECT_ROOT, e ter duas constantes divergindo fazia o leitor de notas
# procurar num caminho e a pesquisa gravar em outro.
from .pipeline import AI_PROJECT_ROOT, pipeline_criatura
from . import apagar as _apagar
from . import leitura as _leitura
from . import imagens as _imagens
from . import navegador as _navegador
from .projetos import frase_de_ajuda as _ajuda_projeto
from .projetos import resolver as _resolver_projeto

# Os nomes de comando são escolhidos para serem TRANSCRITOS bem, não para
# serem bonitos. Palavra estrangeira ("dossiê", "prompts", "short") sai
# deformada do reconhecimento — "dossiê" já virou "torcedor" e "doce e do
# lixo". A forma preferida é sempre a portuguesa comum; as estrangeiras
# continuam valendo para quem digita.
NOTE_ALIASES = {
    # dossiê -> diga "pesquisa"
    "pesquisa": "dossie",
    "pesquisas": "dossie",
    "dossie": "dossie",
    "dossier": "dossie",
    "dossiê": "dossie",
    # roteiro (palavra portuguesa, transcreve bem)
    "roteiro": "roteiro",
    "narracao": "roteiro",
    "narração": "roteiro",
    "texto": "roteiro",
    # prompts -> diga "cenas"
    "cenas": "prompts",
    "cena": "prompts",
    "imagens": "prompts",
    "prompts": "prompts",
    "prompt": "prompts",
}

AJUDA = """# Comandos (funcionam sem créditos)

> **`Ctrl+Espaço` é um interruptor: aperte, fale à vontade, aperte de novo.**
> Enquanto estiver travado ele **não te interrompe** — nada chega ao modelo
> até você soltar, então pode pensar no meio da frase. Funciona de qualquer
> programa. Duas palmas soltam também, para quando você estiver longe do
> teclado. O nome "Ômega" continua valendo para falar sem travar.

> **Fale as palavras em NEGRITO.** Elas foram escolhidas por serem
> portuguesas e comuns — o reconhecimento de voz erra feio em palavra
> estrangeira ("dossiê" já virou *torcedor*). As formas em inglês continuam
> valendo quando você digita.

**As seis fases** — *se você lembrar só disto, já dá para tocar o canal*

Todo vídeo passa pelas mesmas seis etapas. Diga a fase e a criatura; ao
terminar uma, **ele mesmo anuncia a próxima** e o que ela precisa de você.

- **`fase 0 da <criatura>`** — Pesquisa: o dossiê, com fontes
- **`fase 1`** — Model sheets: roteiro + a cara de cada personagem, e **para
  aí** para você aprovar antes dos storyboards
- **`fase 2`** — Storyboards e prompts de vídeo
- **`fase 3`** — Vídeos *(o MCP de geração ainda não está ligado: ele entrega
  os prompts e diz que está esperando você)*
- **`fase 4`** — Edição: narração, trilha, mapa de corte
- **`fase 5`** — Publicação: pacote de SEO e o formulário aberto. **Ele nunca
  aperta publicar**
- **`pode seguir`** — avança de onde parou, sem você dizer a fase
- **`em que pé estamos`** — todas as criaturas e a fase de cada uma

**Ver conteúdo**
- **`pesquisa <criatura>`** — exibe a pesquisa na tela *(= dossiê)*
- **`roteiro <criatura>`** — exibe o roteiro de narração
- **`cenas <criatura>`** — exibe as descrições de imagem *(= prompts)*
- **`video <criatura>`** — toca o último vídeo renderizado
- **`ler <criatura>`** — **lê a pesquisa em voz alta** com a voz do Windows:
  seca, mas grátis e sem limite; vale também "me lê o roteiro de X"
- **`narrar <criatura>`** — o mesmo com a **voz boa** (ElevenLabs). Custa ~1
  crédito por caractere de uma cota de 10 mil por mês, então em texto longo
  ele diz o preço primeiro e espera **`confirmar`** *(= recitar)*
- **`parar`** — interrompe a leitura (ou duas palmas)
- **`esquece`** — troca de assunto. Ele lembra das últimas conversas para você
  poder dizer "e o roteiro *dela*?"; isto zera essa memória
- **`revisar`** — mostra como ele está te entendendo e quais palavras você
  repete que ele ainda não conhece
- **`ensinar <o que ouvi> é <o que era>`** — corrige de vez. Ex.: *"ensinar
  peni wase é Pennywise"*. Vale na hora, e passa a guiar a escuta
- **`imagem <descrição>`** — gera uma imagem pela OpenAI e exibe
  *(precisa de saldo na conta OpenAI)*
- **`projetos`** — lista os projetos encontrados
- **`voltar`** — volta para o núcleo do OMEGA *(= hud)*
- **`diagnostico`** — o que esta máquina tem e o que falta

**Agir — edição**
- **`analisar <criatura>`** — monta o plano de edição
- **`montar <criatura>`** — renderiza o vídeo completo *(= renderizar)*
- **`corte <criatura>`** — renderiza a versão curta *(= short)*
- **`progresso`** — como estão os renders *(= status)*

**Agir — pesquisa e roteiro (dispara o Claude Code)**
- **`pesquisar <criatura>`** — produz a pesquisa (fase 0)
- **`produzir <criatura>`** — roteiro e cenas (fases 1–2)
- **`andamento`** — como vai a pesquisa em curso *(= pipeline)*
- **`cancelar pesquisa`** — aborta o trabalho em andamento. Vale também por
  voz: "não precisa, pode parar"

**Redes sociais** (YouTube, Instagram, TikTok, X)
- **`login <rede>`** — abre a rede para **você** entrar. O OMEGA nunca digita
  nem guarda senha; depois do seu login a sessão fica salva no perfil dele
- **`postar <criatura> no <rede>`** — abre o formulário com o vídeo já
  anexado e **para ali**. Quem aperta publicar é você — publicação é
  irreversível e um comando mal transcrito não pode subir vídeo sozinho
- **`ver navegador`** — print da tela do navegador aqui dentro, para você
  acompanhar sem procurar a janela do Chrome

**Modo de conversa** (o padrão é o econômico)
- **`modo conversa`** — liga a voz em tempo real: ele ouve o áudio direto, dá
  para interromper, é bem mais fluido. **Gasta bastante cota** do Gemini
- **`modo econômico`** — volta ao local: menos fluido, mas a cota rende muito
  mais, e os comandos funcionam igual
- **`qual motor`** — diz em qual dos dois você está

**Escolher a próxima criatura**
- **`tendências`** — o que está sendo buscado no YouTube e o que está em
  ascensão no Google, já separando o que o canal ainda não tem. Vale também
  perguntar por voz: *"sobre o que eu faço o próximo vídeo?"*

**Curso** (assistir junto e virar regra do canal)
- **`vamos assistir a aula de <assunto>`** — grava o som do PC e tira print da
  tela. Fale natural: "começa a aula", "bora assistir aula 4" também valem.
  Ele avisa **de 2 em 2 minutos** que continua gravando, e diz **"PAREI DE
  GRAVAR"** com todas as letras quando você encerrar
- **`pausa a aula`** — quando você pausar o vídeo. Ele para junto e **congela
  o relógio**, para o minuto da transcrição continuar batendo com o do vídeo;
  **`continuar a aula`** volta
- **`parar aula`** / *"pode parar de gravar"* — encerra
- **`como está a aula`** — confirma se ainda está gravando e há quanto tempo
- **`guarda essa tela`** — print na hora, quando aparecer algo que importa
- durante a aula: *"Ômega, o que ele acabou de dizer?"*
- **`assistir o curso inteiro`** — eu abro aula por aula sozinho, dou play,
  gravo e passo para a próxima. Você precisa estar logado no curso na minha
  janela (`login curso`). Enquanto rodar, não toque outro áudio no PC: eu
  gravo o som que SAI daqui. **`como está o curso`** / **`parar o curso`**
- **`processar curso`** — transcreve e extrai as regras *(demora; avisa no fim)*
- **`consolidar regras`** — junta as 38 extrações num arquivo só, agrupado por
  DECISÃO (título, thumb, descrição, quando postar...), funde o que se repete
  guardando todas as fontes, e separa numa seção à parte o que as aulas
  **contradizem** — para você decidir, não eu
- **`revisar regras`** — mostra as regras propostas com a aula e o minuto;
  **`aprovar todas`** / **`aprovar 1 3`** / **`descartar 2`**
- **`apagar a aula 2`** → depois **`confirmar`**. Serve para quando você teve
  que interromper no meio e vai regravar: sem apagar, ficam duas pastas do
  mesmo assunto e a extração de regras lê as duas como aulas diferentes.
  Vai para a lixeira, dá para voltar atrás
- **`curso <nome>`** — troca o curso atual
- Depois de aprovadas, elas guiam o SEO do canal — e ele **discorda** de você
  citando a aula quando você propuser algo contra

**Apagar** (sempre em dois passos, e vai para a lixeira)
- **`apagar projeto <criatura>`** → depois **`confirmar`** ou **`cancelar`**

> Repare na diferença: **`pesquisa X`** *lê* o que já existe;
> **`pesquisar X`** *produz* do zero (leva minutos).
"""


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFD", text.strip().lower())
    return "".join(c for c in text if unicodedata.category(c) != "Mn")


def _slugify(value: str) -> str:
    text = _norm(value)
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def _pasta_da_criatura(creature: str) -> Path | None:
    """A pasta da criatura a partir de um nome possivelmente mal falado.

    Delega ao resolvedor tolerante: "e a coisas" e "it" chegam em
    "IT A Coisa". Continua devolvendo None (em vez de estourar) quando não
    dá para decidir — este módulo responde por frases faladas, e um
    traceback viraria silêncio na cara do usuário.
    """
    pasta, _ = _resolver_projeto(creature)
    return pasta


# Verbos que revelam intenção de OUVIR, não de ver. Vêm antes da
# palavra-chave na frase: "me lê a pesquisa da Medusa".
_VERBOS_DE_LEITURA = {"ler", "leia", "le", "lê", "leiame", "narrar", "narre",
                      "narra", "recitar", "recite", "ouvir", "escutar", "conta",
                      "conte", "fala", "fale", "interpretar", "interprete"}

# Dentro da leitura há duas vozes, e a diferença é dinheiro. "Ler" usa a voz
# do Windows: seca, mas grátis e ilimitada. "Narrar" usa a ElevenLabs: tem
# emoção, e queima ~1 crédito por caractere de uma cota de 10 mil por mês.
# Por isso o verbo escolhe — e não um padrão silencioso que gasta sem avisar.
_VERBOS_DE_NARRACAO = {"narrar", "narre", "narra", "recitar", "recite",
                       "interpretar", "interprete"}

# Verbos de leitura que também são palavras comuníssimas. Eles valem para
# decidir "ler ou exibir" (`_quer_ouvir`), mas NÃO podem disparar um comando
# sozinhos: "me conta uma piada" ia procurar uma criatura chamada "uma piada".
# É o mesmo erro do "amiga" na palavra de ativação — chave de comando que
# também é fala do dia a dia vira armadilha.
_LEITURA_AMBIGUA = {"conta", "conte", "fala", "fale", "le", "lê"}


# Abaixo disto a semelhança vira coincidência e o comando errado dispara.
_LIMIAR_VERBO = 0.82
# Palavra curta colide fácil ("ler" x "ver", "cena" x "cara"): exige exata.
_MINIMO_PARA_APROXIMAR = 5


def _casar_verbo(palavra: str, aceitas: set[str]) -> str | None:
    """Casa a palavra falada com um verbo de comando, tolerando erro.

    O transcritor entrega "pesquiza", "montá", "analizar". Listar todas as
    grafias erradas é enxugar gelo; comparar por semelhança cobre as que
    ninguém previu — que são a maioria.
    """
    if palavra in aceitas:
        return palavra
    if len(palavra) < _MINIMO_PARA_APROXIMAR:
        return None
    melhor, nota_melhor = None, 0.0
    for candidato in aceitas:
        if len(candidato) < _MINIMO_PARA_APROXIMAR:
            continue
        nota = SequenceMatcher(None, palavra, candidato).ratio()
        if nota > nota_melhor:
            melhor, nota_melhor = candidato, nota
    return melhor if nota_melhor >= _LIMIAR_VERBO else None


def _quer_ouvir(raw: str) -> bool:
    return any(_casar_verbo(_norm(p), _VERBOS_DE_LEITURA) for p in raw.split())


# Verbos que abrem uma gravação de aula. "ver"/"vendo" ficam de fora de
# propósito: "vendo a aula" é ambíguo com só olhar, e disparar gravação por
# engano enche o disco em silêncio.
_VERBOS_DE_AULA = {"assistir", "assiste", "assistindo", "gravar", "grava",
                   "gravando", "comecar", "começar", "comeca", "começa",
                   "iniciar", "inicia", "abrir"}

# Frases que ENCERRAM, e que também contêm "aula": precisam ser reconhecidas
# antes, senão "parar a aula" abriria outra gravação.
_FIM_DE_AULA = ("parar", "para", "pare", "terminar", "termina", "acabou",
                "encerrar", "encerra", "fim", "chega")


# "modo conversa", "muda para o modo conversa", "entra no modo conversa"...
# A palavra "modo" (ou "motor") é obrigatória: sem ela, "vamos conversar"
# viraria troca de motor em vez de conversa.
def _disse(baixo: str, *chaves: str) -> bool:
    """A frase contém alguma destas palavras-chave, em qualquer posição?

    Substitui o `low in (...)` que estava espalhado por vinte comandos. Ele
    exigia a frase EXATA, e por isso "me mostra os projetos" caía no modelo
    em vez de ser atendido aqui — medido: 18 de 20 formas naturais de falar
    escapavam. Com o Gemini sem cota, escapar significa não funcionar.

    Chave de uma palavra casa por palavra inteira (para "para" não casar
    dentro de "separar"); chave com espaço casa como trecho.
    """
    normal = _norm(baixo)
    palavras = set(normal.split())
    for chave in chaves:
        alvo = _norm(chave)
        if (" " in alvo and alvo in normal) or alvo in palavras:
            return True
    return False


def _quer_modo(baixo: str, alvos: tuple[str, ...]) -> bool:
    palavras = [_norm(p) for p in baixo.split()]
    if not any(p in ("modo", "motor") for p in palavras):
        return False
    return any(_norm(a) in palavras for a in alvos)


# Pausar o vídeo e ENCERRAR a aula são coisas opostas, e a fala é parecida
# ("pausa" x "para"). Estas listas ficam separadas de propósito.
_PAUSA = ("pausar", "pausa", "pause", "pausei", "pausado", "espera", "espere")
_RETOMADA = ("continuar", "continua", "continue", "retomar", "retoma",
             "retome", "voltei", "voltar", "volta", "segue", "seguir")


def _sobre_a_aula(baixo: str) -> bool:
    """A frase é sobre a gravação da aula, e não sobre outra coisa?"""
    palavras = [_norm(p) for p in baixo.split()]
    return any(p in ("aula", "aulas", "gravacao", "gravando", "gravar",
                     "grava", "video") for p in palavras)


def _e_pausa_de_aula(baixo: str) -> bool:
    palavras = [_norm(p) for p in baixo.split()]
    return _sobre_a_aula(baixo) and any(p in _PAUSA for p in palavras)


def _e_retomada_de_aula(baixo: str) -> bool:
    palavras = [_norm(p) for p in baixo.split()]
    return _sobre_a_aula(baixo) and any(p in _RETOMADA for p in palavras)


def _e_fim_de_aula(baixo: str) -> bool:
    """"pode parar de gravar a aula 1" tem que encerrar tanto quanto "parar aula"."""
    palavras = [_norm(p) for p in baixo.split()]
    # "gravar"/"grava" entram aqui porque "pode parar de gravar" — sem dizer
    # "aula" — é como se fala de verdade, e não casava com nada. Não há
    # conflito com o lado de ABRIR: lá os verbos de encerramento são
    # excluídos, então "gravar aula 2" abre e "parar de gravar" fecha.
    if not any(p in ("aula", "aulas", "gravacao", "gravando", "gravar", "grava")
               for p in palavras):
        return False
    return any(p in _FIM_DE_AULA for p in palavras)


# Assistir O CURSO é diferente de assistir UMA aula, e a diferença é a
# palavra que ele usa. "assistir aula 2" grava o que está na tela agora;
# "assistir o curso" é a maratona — o OMEGA abre aula por aula sozinho.
# Por isso a regra é a presença de "curso" SEM "aula": é assim que ele fala,
# e evita que um pedido de gravar uma aula dispare três horas de navegação.
_TUDO = ("inteiro", "inteira", "todo", "toda", "todos", "todas", "completo",
         "sozinho", "sozinha", "tudo", "maratona", "maratonar", "seguido")


def _e_maratona(baixo: str) -> bool:
    palavras = [_norm(p) for p in baixo.split()]
    if any(p in ("maratona", "maratonar") for p in palavras):
        return True
    if "curso" not in palavras:
        return False
    if any(p in _FIM_DE_AULA for p in palavras):
        return False
    if not any(_casar_verbo(p, _VERBOS_DE_AULA) for p in palavras):
        return False
    # "assistir o curso" já basta; "aula" no meio devolve para a gravação
    # avulsa, que é o comando mais específico.
    return not any(p in ("aula", "aulas") for p in palavras) or \
        any(p in _TUDO for p in palavras)


def _e_parar_maratona(baixo: str) -> bool:
    palavras = [_norm(p) for p in baixo.split()]
    return (any(p in ("curso", "maratona") for p in palavras)
            and any(p in _FIM_DE_AULA for p in palavras))


# As seis fases do canal. Isto é o que o Samuel pediu para não precisar
# decorar quarenta comandos: um vocabulário só, "vamos começar a fase 0".
#
# "fase" é obrigatória e o número também — sem os dois, "vamos começar" e
# "pode seguir" ficariam ambíguos com meia dúzia de outras coisas que ele diz.
_NUMERO_DA_FASE = re.compile(r"\bfase\s+(\d)\b", re.I)

# "zero" falado costuma sair como palavra, e o Whisper varia entre as duas
# formas na mesma sessão.
_FALADOS = {"zero": 0, "um": 1, "uma": 1, "dois": 2, "duas": 2, "tres": 3,
            "três": 3, "quatro": 4, "cinco": 5}


def _fase_pedida(baixo: str) -> int | None:
    achado = _NUMERO_DA_FASE.search(baixo)
    if achado:
        return int(achado.group(1))
    palavras = [_norm(p) for p in baixo.split()]
    if "fase" not in palavras:
        return None
    for i, p in enumerate(palavras):
        if p == "fase" and i + 1 < len(palavras):
            return _FALADOS.get(palavras[i + 1])
    return None


# Palavras que dizem O QUE FAZER com a fase, e não DE QUEM é ela.
_LIXO_NA_FASE = {
    "fase", "vamos", "vamo", "comecar", "começar", "comeca", "começa",
    "iniciar", "inicia", "rodar", "roda", "fazer", "faz", "da", "do", "de",
    "a", "o", "as", "os", "na", "no", "pra", "para", "quero", "queria",
    "pode", "podemos", "bora", "agora", "omega", "ômega", "senhor", "por",
    "favor", "criatura", "ja", "já", "e", "entao", "então",
    "zero", "um", "uma", "dois", "duas", "tres", "três", "quatro", "cinco",
}


def _criatura_da_fase(raw: str) -> str:
    palavras = [p for p in raw.split()
                if _norm(p.strip(",.!?")) not in _LIXO_NA_FASE
                and not p.strip(",.!?").isdigit()]
    return " ".join(palavras).strip(" ,.")


def _e_seguir(baixo: str) -> bool:
    """"pode seguir" — avança de onde parou, sem precisar dizer a fase.

    Não conflita com a retomada de aula, e a exclusão usa o MESMO detector
    (`_sobre_a_aula`) em vez de uma lista própria: a primeira versão listava
    "aula/gravacao/curso" à mão e deixava passar "voltei, pode continuar
    GRAVANDO" — que avançaria uma fase em vez de retomar a gravação, no meio
    de uma aula. Duas listas para o mesmo conceito divergem sempre.
    """
    palavras = [_norm(p) for p in baixo.split()]
    if _sobre_a_aula(baixo) or "curso" in palavras:
        return False
    return any(p in ("seguir", "segue", "prosseguir", "prossiga", "continuar",
                     "continua", "avancar", "avanca", "avance") for p in palavras)


def _e_pedido_de_aula(baixo: str) -> bool:
    palavras = [_norm(p) for p in baixo.split()]
    if not any(p in ("aula", "aulas", "curso") for p in palavras):
        return False
    if any(p in _FIM_DE_AULA for p in palavras):
        return False
    return any(_casar_verbo(p, _VERBOS_DE_AULA) for p in palavras)


# Palavras que dizem COMO fazer, e não O QUE é a aula. Tirá-las é o que
# transforma "vamos começar a assistir a aula de miniatura" em "miniatura".
# Palavras que dizem O QUE FAZER, não QUAL aula. Tirá-las é o que
# transforma "vamos apagar a aula 2" em "aula 2".
_LIXO_AO_APAGAR = {
    "apagar", "apaga", "apague", "deletar", "deleta", "delete", "excluir",
    "exclui", "exclua", "remover", "remove", "descartar", "descarta",
    "jogar", "fora", "lixo", "vamos", "quero", "queria", "pode", "podemos",
    "por", "favor", "a", "o", "as", "os", "da", "do", "de", "essa", "esse",
    "aquela", "aquele", "toda", "todo", "inteira", "omega", "senhor",
}

_LIXO_NO_TITULO = _VERBOS_DE_AULA | {
    "vamos", "vou", "quero", "queria", "agora", "ai", "aí", "entao", "então",
    "a", "o", "as", "os", "de", "do", "da", "uma", "um", "essa", "esse",
    "aula", "aulas", "curso", "sobre", "por", "favor", "ja", "já", "pode",
    "podemos", "bora", "la", "lá", "e", "que", "com", "no", "na",
    # O nome dele: no fluxo de voz o `_extrair_comando` já o remove, mas
    # digitado ele chega inteiro e viraria o título da aula.
    "omega", "ômega", "senhor",
}


def _titulo_da_aula(raw: str) -> str:
    palavras = [p for p in raw.split()
                if _norm(p.strip(",.!?")) not in _LIXO_NO_TITULO]
    titulo = " ".join(palavras).strip(" ,.")
    # "assistir aula 4" deixaria só "4" como nome de pasta, que não diz nada
    # numa lista de vinte aulas.
    if titulo.isdigit():
        titulo = f"aula {titulo}"
    # Sem título dito, o nome vem da hora — a pasta já é datada, e inventar
    # nome seria pior do que admitir que ele não deu um.
    return titulo or "aula sem nome"


def _quer_narrar(raw: str) -> bool:
    """True quando o pedido foi 'narrar' e não apenas 'ler' — voz cara."""
    return any(_casar_verbo(_norm(p), _VERBOS_DE_NARRACAO) for p in raw.split())


_VERBOS_DE_IMAGEM = {"imagem", "imagina", "desenha", "desenhar",
                     "ilustra", "ilustrar", "gerar-imagem"}


# Toda palavra-chave que inicia um comando com alvo. A ordem não importa:
# vence a que aparecer primeiro na frase.
_VERBOS_COM_ALVO = (
    (_VERBOS_DE_LEITURA - _LEITURA_AMBIGUA)
    | _VERBOS_DE_IMAGEM
    | set(NOTE_ALIASES)
    | {"video", "vídeo", "assistir", "analisar", "analise", "analisa",
       "montar", "monta", "gerar", "gera", "renderizar", "renderiza", "render",
       "corte", "corta", "resumo", "short", "abrir", "abre",
       "apagar", "apaga", "deletar", "deleta", "remover", "remove",
       "pesquisar", "pesquise", "investigar", "investigue",
       "produzir", "produza", "roteirizar", "roteirize",
       "postar", "posta", "publicar", "publica", "subir", "sobe",
       "login", "entrar", "logar"}
)

# Preposições, artigos e substantivos genéricos que sobram grudados no alvo
# ("do it a coisa", "o video da medusa").
_LIXO_INICIAL = {"o", "a", "os", "as", "do", "da", "dos", "das", "de", "no",
                 "na", "em", "sobre", "para", "pra", "meu", "minha",
                 "video", "vídeo", "projeto", "arquivo", "pasta"}



# Frases que o OMEGA não entendeu, guardadas para o vocabulário crescer com
# base no que o Samuel REALMENTE diz — e não no que imaginamos que ele diria.
NAO_ENTENDIDAS = Path(__file__).resolve().parent.parent / "nao-entendidas.txt"


def _anotar_incompreensao(texto: str) -> None:
    try:
        with NAO_ENTENDIDAS.open("a", encoding="utf-8") as f:
            f.write(texto.strip() + "\n")
    except OSError:
        pass  # registrar é conveniência; nunca pode derrubar um comando


def _extrair_verbo_e_alvo(raw: str) -> tuple[str, str] | None:
    """Acha a palavra-chave na frase e devolve (verbo, alvo).

    "me mostra a pesquisa do it a coisa" -> ("pesquisa", "it a coisa")
    Devolve None quando não há palavra-chave alguma — aí quem chama manda
    para o modelo de linguagem.
    """
    palavras = raw.split()

    def varrer(aceitas: set[str]) -> tuple[str, str] | None:
        for i, palavra in enumerate(palavras):
            verbo = _casar_verbo(_norm(palavra), aceitas)
            if verbo is None:
                continue
            resto = palavras[i + 1:]
            # Tira artigos/preposições do começo do alvo, senão "do it a
            # coisa" e "it a coisa" viram buscas diferentes.
            while resto and _norm(resto[0]) in _LIXO_INICIAL:
                resto = resto[1:]
            alvo = " ".join(resto).strip()
            if alvo:
                return verbo, alvo
        return None

    # O QUE ele quer ver ganha de COMO ("abrir a pesquisa da Medusa" é pedido
    # de ver a pesquisa, não de abrir o navegador). Sem esta prioridade o
    # verbo genérico, por vir antes na frase, sequestrava o comando.
    return varrer(set(NOTE_ALIASES)) or varrer(_VERBOS_COM_ALVO)



def _postar(pedido: str, ui) -> str:
    """"postar a Medusa no youtube" -> leva o render até o formulário.

    O OMEGA para no formulário de propósito: publicar é irreversível e um
    comando de voz mal transcrito não pode subir vídeo no canal sozinho.
    """
    baixo = _norm(pedido)
    rede = next((r for r in ("youtube", "instagram", "tiktok", "twitter", "x")
                 if r in baixo), None)
    if rede is None:
        return ("Em qual rede, senhor? YouTube, Instagram, TikTok ou X. "
                "Diga por exemplo: postar a Medusa no YouTube.")
    # O que sobra depois de tirar a rede e as preposições é o nome do projeto.
    criatura = baixo
    for termo in (rede, "no", "na", "em", "para", "pro"):
        criatura = re.sub(rf"{re.escape(termo)}", " ", criatura)
    criatura = " ".join(criatura.split())

    caminho = _latest_render(criatura) if criatura else None
    if caminho is None:
        return (f"Não achei vídeo renderizado para {criatura or 'esse projeto'}. "
                "Monte o vídeo antes de postar.")
    return _navegador.preparar_postagem(rede, str(caminho), ui=ui)


def _read_note(creature: str, note: str) -> tuple[str, str] | str:
    """Devolve (titulo, conteudo) ou uma frase de erro."""
    pasta, candidatos = _resolver_projeto(creature)
    if pasta is None:
        # Melhor dizer quais existem do que só negar: o nome quase sempre
        # chegou deformado pelo reconhecimento de voz.
        return _ajuda_projeto(creature, candidatos)
    # Daqui em diante usa o nome REAL do projeto, não o que foi falado: se
    # "e a coisas" virou "IT A Coisa", o usuário precisa ver isso na tela
    # para confiar que abriu o certo.
    nome = pasta.name
    rotulos = {"dossie": "pesquisa", "roteiro": "roteiro", "prompts": "cenas"}
    caminho = pasta / f"{_slugify(nome)}-video" / "notes" / f"{note}.md"
    if caminho.exists():
        return (f"{rotulos[note]} — {nome}", caminho.read_text(encoding="utf-8"))
    return (
        f"Ainda não existe {rotulos[note]} para {nome}. "
        f"Peça a pesquisa primeiro (ou gere pelo Claude)."
    )


def _latest_render(creature: str) -> Path | None:
    base = _pasta_da_criatura(creature)
    if base is None:
        return None
    renders = base / f"{_slugify(base.name)}-video" / "renders"
    if not renders.exists():
        return None
    videos = sorted(
        renders.glob("*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True
    )
    return videos[0] if videos else None


def _diagnostico() -> tuple[str, str, str]:
    """Estado de cada peça de que o OMEGA depende, nesta máquina.

    Existe porque as duas máquinas do projeto têm capacidades diferentes e a
    falha silenciosa é o padrão: sem CLI, a pesquisa não roda; sem Studio, o
    render não roda; sem modelo Vosk, o microfone não roda. Melhor uma linha
    dizendo qual peça falta do que descobrir depois de esperar dez minutos.
    """
    from .pipeline import AI_PROJECT_ROOT as RAIZ_PIPELINE, _resolver_claude

    linhas: list[str] = ["# Diagnóstico do OMEGA", ""]
    problemas = 0

    def item(rotulo: str, ok: bool, detalhe: str) -> None:
        nonlocal problemas
        if not ok:
            problemas += 1
        linhas.append(f"- {'✅' if ok else '❌'} **{rotulo}** — {detalhe}")

    item(
        "Pasta dos projetos",
        RAIZ_PIPELINE.is_dir(),
        f"`{RAIZ_PIPELINE}`" + ("" if RAIZ_PIPELINE.is_dir() else " (defina AI_PROJECT_ROOT)"),
    )

    claude = _resolver_claude()
    item(
        "Claude Code CLI",
        claude is not None,
        f"`{claude}`" if claude else "não encontrado — `npm install -g @anthropic-ai/claude-code`",
    )

    estudio_vivo = _studio_alive()
    item(
        "Alpha Studio",
        estudio_vivo,
        f"respondendo em {STUDIO_URL}" if estudio_vivo else f"offline em {STUDIO_URL}",
    )

    if estudio_vivo:
        try:
            projetos = _get_projects()
            item("Projetos", bool(projetos), f"{len(projetos)} encontrado(s)")
        except Exception as e:  # noqa: BLE001
            item("Projetos", False, f"erro ao listar: {str(e)[:60]}")

    modelo = Path(__file__).resolve().parent.parent / "models" / "pt-br"
    item(
        "Modelo de voz (Vosk pt-BR)",
        modelo.is_dir(),
        f"`{modelo}`" if modelo.is_dir() else "ausente — só comandos digitados",
    )

    catalogo = RAIZ_PIPELINE / "Trilhas" / "catalogo.json"
    if catalogo.exists():
        try:
            import json as _json

            dados = _json.loads(catalogo.read_text(encoding="utf-8"))
            faixas = dados if isinstance(dados, list) else dados.get("faixas", [])
            item("Biblioteca de trilha", bool(faixas), f"{len(faixas)} faixa(s)")
        except Exception:  # noqa: BLE001
            item("Biblioteca de trilha", False, "catalogo.json ilegível")
    else:
        item(
            "Biblioteca de trilha",
            False,
            "sem catálogo — rode `npm run trilhas` no studio",
        )

    linhas.append("")
    linhas.append(
        "Tudo pronto." if problemas == 0 else f"{problemas} peça(s) faltando."
    )
    resumo = (
        "Diagnóstico na tela: tudo pronto."
        if problemas == 0
        else f"Diagnóstico na tela: {problemas} peça(s) faltando."
    )
    return ("diagnóstico", "\n".join(linhas), resumo)


def handle(text: str, ui) -> str | None:
    """Executa um comando local. Devolve a frase de resposta, ou None se o
    texto não for um comando local reconhecido."""
    raw = text.strip()
    low = _norm(raw)
    if not low:
        return None

    if _disse(low, "ajuda", "help", "comandos"):
        ui.show_document("ajuda", AJUDA)
        return "Comandos exibidos na tela."

    if _disse(low, "voltar", "volta", "inicio", "hud", "rosto"):
        ui.show_hud()
        return "De volta ao HUD."

    if _disse(low, "projetos"):
        err = _ensure_studio()
        if err:
            return err
        projetos = _get_projects()
        if not projetos:
            return "Nenhum projeto encontrado."
        linhas = [
            f"| {p['creatureName']} | {p['clipCount']} | "
            f"{'sim' if p['hasAudio'] else 'não'} | "
            f"{'sim' if p['hasEditPlan'] else 'não'} |"
            for p in projetos
        ]
        doc = (
            "# Projetos\n\n"
            "| Projeto | Clipes | Áudio | Plano |\n|---|---|---|---|\n"
            + "\n".join(linhas)
        )
        ui.show_document("projetos", doc)
        return f"{len(projetos)} projeto(s) na tela."

    if _disse(low, "progresso", "status"):
        return studio_control({"action": "status"})

    # Confirmação de exclusão: vem antes de tudo para que um "confirmar" solto
    # nunca seja interpretado como outra coisa.
    if low in ("parar", "para", "chega", "silencio", "silêncio", "cala"):
        return _leitura.parar()

    # ----- trocar o motor de voz em pleno voo -----
    #
    # O padrão é o local, que é econômico. O Live é mais gostoso de usar e
    # gasta bem mais cota, então sobe só quando ele pedir.
    if _quer_modo(low, ("conversa", "conversar", "live", "tempo real",
                        "natural", "fluido")):
        from . import motor as _motor

        return _motor.pedir("live")

    if _quer_modo(low, ("economico", "econômico", "economia", "local",
                        "poupar", "economizar", "normal")):
        from . import motor as _motor

        return _motor.pedir("free")

    if _disse(low, "qual motor", "que motor", "modo atual", "qual modo"):
        from . import motor as _motor

        atual = _motor.atual()
        return (f"Estou no {_motor.NOMES.get(atual, atual)}. "
                + ("Diga 'modo econômico' para poupar cota."
                   if atual == "live" else
                   "Diga 'modo conversa' para a voz em tempo real."))

    # ----- o que esta em alta -----
    if _disse(low, "tendencias", "em alta", "trends", "google trends"):
        from . import tendencias as _tend

        ui.write_log("SYS: buscando tendências...")
        material = _tend.pesquisar()
        ui.show_document("O que está em alta", material)
        return ("Está na tela. Me pergunte o que fazer com isso que eu "
                "analiso — sozinho eu só trouxe os números.")

    # ----- processar o curso e aprovar as regras -----
    if _disse(low, "processar", "processa", "transcrever") and _disse(low, "curso", "aulas", "aula"):
        from . import curso as _curso

        return _curso.processar(ui)

    if _disse(low, "cancelar", "cancela", "parar") and _disse(low, "processamento") or _disse(low, "cancelar curso"):
        from . import curso as _curso

        return _curso.cancelar()

    if _disse(low, "curso") and _disse(low, "andamento", "situacao", "status", "como vai"):
        from . import curso as _curso

        return _curso.andamento()

    if _disse(low, "consolidar", "consolida", "juntar", "junta") and             _disse(low, "regras"):
        from . import curso as _curso

        ui.write_log("SYS: consolidando as regras das aulas...")
        return _curso.consolidar()

    if _disse(low, "regras"):
        from . import curso as _curso

        return _curso.revisar(ui)

    if low.startswith(("aprovar ", "aprova ", "descartar ", "descarta ",
                       "aprovar", "descartar")):
        from . import curso as _curso

        return _curso.decidir(raw)

    # ----- AS SEIS FASES: a espinha de tudo -----
    #
    # Vem cedo, e antes do curso, porque "fase 0" é a entrada que ele quer
    # usar no lugar de decorar comando. Só dispara com a palavra "fase" e um
    # número junto — sem os dois, nada aqui é acionado.
    _n_fase = _fase_pedida(low)
    if _n_fase is not None:
        from . import fases as _fases

        alvo = _criatura_da_fase(raw)
        if not alvo:
            return ("De qual criatura, senhor? Diga por exemplo "
                    f"'fase {_n_fase} da Medusa'.")
        pasta, candidatos = _resolver_projeto(alvo)
        if not pasta and candidatos:
            return _ajuda_projeto(alvo, candidatos)
        nome = pasta.name if pasta else alvo
        return _fases.comecar(nome, _n_fase, ui)

    if _disse(low, "em que pe estamos", "em que pé estamos", "onde estamos",
              "como esta a producao", "como está a produção", "as fases",
              "situacao das fases", "situação das fases"):
        from . import fases as _fases

        return _fases.situacao()

    if _e_seguir(low):
        from . import fases as _fases

        alvo = _criatura_da_fase(raw)
        pasta, _ = _resolver_projeto(alvo) if alvo else (None, [])
        if pasta is None:
            # Sem nome, seguir a única que está no meio do caminho.
            emcurso = _fases.em_andamento()
            if len(emcurso) != 1:
                return ("De qual criatura eu sigo? " + _fases.situacao())
            return _fases.seguir(emcurso[0], ui)
        return _fases.seguir(pasta.name, ui)

    # ----- assistir o CURSO INTEIRO sozinho -----
    #
    # Vem antes de tudo que mexe com aula: as frases se parecem ("assistir o
    # curso" x "assistir a aula 2") e o efeito é muito diferente — uma grava o
    # que está na tela, a outra navega por horas de vídeo.
    if _e_parar_maratona(low):
        from . import maratona as _mar

        if _mar.rodando():
            return _mar.parar()
        # Não está maratonando: o pedido é sobre outra coisa, segue adiante.

    if _disse(low, "curso", "maratona") and _disse(
            low, "como esta", "como vai", "situacao", "status", "andamento"):
        from . import maratona as _mar

        if _mar.rodando():
            return _mar.situacao()

    if _e_maratona(low):
        from . import maratona as _mar

        # Se ele colar o link junto, aproveito e guardo.
        achado = re.search(r"https?://\S+", raw)
        return _mar.iniciar(achado.group(0) if achado else "", ui)

    # ----- assistir aula do curso junto com ele -----
    #
    # Ninguém fala "assistir aula". Fala "vamos começar a assistir a aula de
    # miniatura". A primeira versão exigia que a frase COMEÇASSE com o verbo e
    # ignorava tudo isso — o mesmo erro que `_extrair_verbo_e_alvo` existe para
    # não cometer. Aqui o verbo é procurado em qualquer posição.
    #
    # A palavra "aula" (ou "curso") é OBRIGATÓRIA, e é ela que desfaz a
    # ambiguidade com "assistir o vídeo da Medusa", que toca um render e não
    # tem nada a ver com gravar aula.
    if _e_pedido_de_aula(low):
        from . import aula as _aula

        return _aula.iniciar(_aula.curso_atual(), _titulo_da_aula(raw),
                             avisar=ui.write_log)

    if low.startswith(("curso ", "novo curso ")) and "processar" not in low:
        from . import aula as _aula

        return _aula.definir_curso(
            re.sub(r"^(novo )?curso\s*", "", raw, flags=re.I))

    # Encerrar também tem que aceitar fala natural. Isto era uma lista de
    # frases EXATAS, e o Samuel disse "pode parar de gravar a aula 1" — que
    # não casava com nenhuma delas. A aula ficou gravando enquanto ele
    # repetia o pedido de quatro formas diferentes. Eu já tinha corrigido o
    # lado de ABRIR e deixei o de FECHAR com o mesmo defeito.
    # Apagar aula vem ANTES de tudo que mexe com aula: "apagar a aula 2"
    # contém "aula", e sem esta ordem viraria início ou fim de gravação.
    if _disse(low, "aula", "aulas") and _disse(
            low, "apagar", "apaga", "deletar", "deleta", "excluir", "exclui",
            "remover", "remove", "jogar fora", "descartar"):
        from . import aula as _aula

        # Sobra o que identifica a aula ("aula 2"). Palavra INTEIRA: sem os
        # limites, o "a" da lista casaria dentro de "aula" e sobraria "ul 2".
        alvo = " ".join(x for x in low.split()
                        if _norm(x.strip(",.!?")) not in _LIXO_AO_APAGAR)
        return _aula.preparar_exclusao(" ".join(alvo.split()) or "aula")

    # PAUSA vem antes de ENCERRAR: "pausa a aula" contém "aula", e sem esta
    # ordem cairia no encerramento e perderia o resto do vídeo.
    if _e_pausa_de_aula(low):
        from . import aula as _aula

        return _aula.pausar_aula()

    if _e_retomada_de_aula(low):
        from . import aula as _aula

        return _aula.retomar_aula()

    if _e_fim_de_aula(low):
        from . import aula as _aula

        return _aula.parar()

    if _disse(low, "print", "printa") or (_disse(low, "tela") and _disse(low, "guarda", "guarde", "salva", "anota")):
        from . import aula as _aula

        return _aula.print_agora()

    if _disse(low, "aula") and _disse(low, "como esta", "situacao", "ainda", "status"):
        from . import aula as _aula

        return _aula.situacao()

    # Abortar a pesquisa/produção em curso. Vem cedo para que um "cancelar"
    # dito no meio de um trabalho longo não seja lido como outra coisa.
    if low in ("cancelar pesquisa", "cancela pesquisa", "cancelar producao",
               "cancelar produção", "cancelar roteiro", "parar pesquisa",
               "para a pesquisa", "abortar", "cancelar tudo"):
        from .pipeline import cancelar as _cancelar_pipeline

        return _cancelar_pipeline()

    # "O que você está vendo?" — pedido do Samuel para acompanhar a postagem
    # sem ter que caçar a janela do Chrome no meio das outras.
    if _disse(low, "navegador") or _disse(low, "o que voce esta vendo"):
        return _navegador.ver(ui)

    # Como ele está te entendendo, e o que ainda falta ensinar. É a saída do
    # diário de aprendizado — a resposta prática ao "como se treina isso".
    if _disse(low, "revisar", "revisa", "revisao", "aprendizado",
              "me entende", "me entendendo", "me entendeu"):
        from . import aprendizado as _aprendizado

        texto = _aprendizado.resumo()
        ui.show_document("Como estou te entendendo", texto)
        falhas = texto.count("\n- ")
        return ("Está na tela. " + (
            "Diga 'ensinar <o que ouvi> é <o que era>' para as palavras da lista."
            if falhas else "Nada de grave por ali."))

    # "ensinar peni wase é Pennywise" — a correção vem de quem sabe.
    if low.startswith(("ensinar ", "ensina ", "aprende ", "aprender ")):
        from . import aprendizado as _aprendizado

        resto = raw.split(" ", 1)[1] if " " in raw else ""
        # Aceita "é", "e", "eh" e "seria" como separador: é ditado em voz alta,
        # e o reconhecimento entrega qualquer um deles.
        partes = re.split(r"\s+(?:é|e|eh|seria|significa)\s+", resto, maxsplit=1)
        if len(partes) != 2:
            return ("Diga assim: 'ensinar peni wase é Pennywise' — "
                    "primeiro o que eu ouvi, depois o que era.")
        return _aprendizado.ensinar(partes[0], partes[1])

    # Trocar de assunto explicitamente. O OMEGA agora carrega as últimas
    # trocas para entender "e o roteiro dela?"; quando o assunto muda de
    # verdade, esse mesmo contexto atrapalha.
    if _disse(low, "esquece", "esquecer", "recomeca") or _disse(low, "assunto"):
        esquecer = getattr(ui, "esquecer", None)
        return esquecer() if esquecer else "Nada guardado por aqui."

    # "confirmar" e "cancelar" são compartilhados por três donos (narração
    # cara, exclusão de aula, exclusão de projeto). Cada um responde None
    # quando não tem nada pendente, e a ordem aqui é do mais leve ao mais
    # destrutivo — apagar projeto fica por último, de propósito.
    if _disse(low, "confirmar", "confirma", "confirmado", "pode apagar"):
        narracao = _leitura.confirmar_narracao()
        if narracao is not None:
            return narracao
        from . import aula as _aula

        aula_apagada = _aula.confirmar_exclusao()
        if aula_apagada is not None:
            return aula_apagada
        return _apagar.confirmar()
    if _disse(low, "cancelar", "cancela", "deixa", "nao apaga", "não apaga"):
        from . import aula as _aula

        cancelada = _aula.cancelar_exclusao()
        if cancelada is not None:
            return cancelada
        return _apagar.cancelar()

    if _disse(low, "andamento", "pipeline"):
        return pipeline_criatura({"action": "status"})

    if _disse(low, "diagnostico", "checar"):
        titulo, doc, resumo = _diagnostico()
        ui.show_document(titulo, doc)
        return resumo

    # Comandos com argumento. Ninguém fala "pesquisa medusa" — fala "me
    # mostra a pesquisa da Medusa". Procuramos a palavra-chave em QUALQUER
    # posição e tomamos o resto como alvo; sem isso a frase inteira ia parar
    # no Gemini (que vive estourando a cota gratuita).
    achado = _extrair_verbo_e_alvo(raw)
    if achado is None:
        # Nenhuma palavra-chave: registra para o vocabulário crescer com base
        # no que ele REALMENTE diz, e devolve None (quem chama manda ao modelo).
        _anotar_incompreensao(raw)
        return None
    verbo, alvo = achado

    if verbo in _VERBOS_DE_LEITURA:
        # "lê a Medusa" sem dizer o quê: assume a pesquisa.
        resultado = _read_note(alvo, "dossie")
        if isinstance(resultado, str):
            return resultado
        titulo, conteudo = resultado
        ui.show_document(titulo, conteudo)
        return _leitura.ler(titulo, conteudo, ui,
                            bonita=verbo in _VERBOS_DE_NARRACAO)

    if verbo in NOTE_ALIASES:
        nota = NOTE_ALIASES[verbo]
        resultado = _read_note(alvo, nota)
        if isinstance(resultado, str):
            return resultado
        titulo, conteudo = resultado
        ui.show_document(titulo, conteudo)
        # "ler a pesquisa da Medusa" exibe E lê; "pesquisa da Medusa" só
        # exibe. A intenção de ouvir vem do verbo dito antes da palavra-chave.
        if _quer_ouvir(raw):
            return _leitura.ler(titulo, conteudo, ui, bonita=_quer_narrar(raw))
        return f"{titulo} na tela."

    if verbo in ("postar", "posta", "publicar", "publica", "subir", "sobe"):
        return _postar(alvo, ui)

    if verbo in ("login", "entrar", "logar"):
        # O curso não é uma "rede" com URL fixa: é o link que ele me passou.
        # Sem este desvio, `login curso` cairia em "não conheço essa rede" e
        # ele não teria como deixar a sessão salva no meu perfil — que é a
        # única forma de eu assistir o curso, já que senha não passa por aqui.
        if _norm(alvo).strip() in ("curso", "kiwify", "aula", "aulas"):
            from . import maratona as _mar

            url = _mar.url_salva()
            if not url:
                return ("Não tenho o link do curso. Cole ele aqui uma vez que "
                        "eu guardo.")
            resposta = _navegador.abrir_url(url)
            return (resposta if resposta.startswith("Não consegui") else
                    "Curso aberto. Entre com a sua conta nessa janela — eu não "
                    "vejo nem guardo senha. Depois a sessão fica salva e eu já "
                    "abro logado.")
        return _navegador.login(alvo)

    if verbo in _VERBOS_DE_IMAGEM:
        # "imagem da Medusa em pedra" -> gera e exibe. Se o texto
        # citar um projeto conhecido, a imagem é salva junto dele.
        pasta, _ = _resolver_projeto(alvo)
        return _imagens.gerar(alvo, pasta.name if pasta else None, ui)

    if verbo in ("video", "vídeo", "assistir"):
        caminho = _latest_render(alvo)
        if caminho is None:
            return f"Nenhum vídeo renderizado ainda para {alvo}."
        ui.show_video(f"vídeo — {alvo}", str(caminho))
        return f"Reproduzindo {caminho.name}."

    if verbo in ("analisar", "analise", "analisa"):
        return studio_control({"action": "analyze", "project": alvo})

    if verbo in ("montar", "monta", "gerar", "gera", "renderizar", "renderiza", "render"):
        return studio_control({"action": "render_full", "project": alvo})

    if verbo in ("corte", "corta", "resumo", "short"):
        return studio_control({"action": "render_short", "project": alvo})

    if verbo in ("abrir", "abre"):
        return studio_control({"action": "open", "project": alvo})

    if verbo in ("apagar", "apaga", "deletar", "deleta", "remover", "remove"):
        return _apagar.preparar(alvo)

    # Verbo = AGIR, substantivo = LER. "dossie X" mostra a pesquisa que já
    # existe; "pesquisar X" dispara o Claude Code para produzi-la. Sem essa
    # separação, "pesquisa X" abria o arquivo e parecia que a pesquisa tinha
    # falhado, quando na verdade ela nunca tinha sido iniciada.
    if verbo in ("pesquisar", "pesquise", "investigar", "investigue"):
        return pipeline_criatura(
            {"action": "start", "creature": alvo, "phase": "pesquisa"}
        )

    if verbo in ("produzir", "produza", "roteirizar", "roteirize"):
        return pipeline_criatura(
            {"action": "start", "creature": alvo, "phase": "producao"}
        )

    # Não é comando conhecido: registra para podermos ampliar o
    # vocabulário depois, e devolve None (quem chama manda ao modelo).
    _anotar_incompreensao(raw)
    return None
