# GIT E SINCRONIA — como as duas máquinas conversam

> O problema: o Samuel trabalha no PC Windows de casa e numa máquina Linux
> secundária. Uma pesquisa feita no Linux ficava presa lá — ao chegar em casa,
> o conteúdo não existia. E nada tinha backup: se o HD do Windows morresse,
> todas as pesquisas e roteiros do canal iam junto.
> Criado 2026-08-05.

## A regra: **texto sincroniza, mídia não**

| Sincroniza (KBs) | Fica na máquina (GBs) |
|---|---|
| `notes/` — dossiê, roteiro, prompts | `public/videos/` — clipes |
| `scenes.json`, `edit-plan.json` | `public/audio/` — narração |
| `analysis/alignment.json`, `captions.*` | `renders/` — vídeos prontos |
| `Trilhas/catalogo.json` | `Trilhas/**/*.mp3` — as faixas |
| todo o código do `Alpha/` | `node_modules`, `.venv`, modelos |

Os clipes e renders só interessam à máquina que gera e renderiza — o Windows.
Fazê-los viajar custaria horas de upload para resolver um problema que não
existe. O que precisa viajar é o **trabalho intelectual**: pesquisa, roteiro,
prompts, decisões de edição. Isso cabe em alguns KB.

Por isso git, e não uma pasta sincronizada: além de resolver o transporte, ele
**versiona**. Dá para ver como o dossiê estava antes de você reescrever e
voltar atrás. Nenhum Drive faz isso.

## Dois repositórios

**1. `Alpha/` — o código.** É este repositório. Studio, ALPHA, alinhador,
documentação, diário. Já está pronto e commitado.

**2. Conteúdo — as criaturas.** Ainda não existe; precisa ser criado no
Windows, onde as pastas moram. Cobre `Criaturas/`, `Animes/` e o
`Trilhas/catalogo.json`, ignorando toda a mídia.

Separados de propósito: código e conteúdo mudam em ritmos diferentes, e um
`git log` cheio de "dossiê da Medusa revisado" no meio de mudanças de código
atrapalha os dois.

## Subir o `Alpha/` (uma vez)

O repositório local já está criado com o primeiro commit. Falta só apontá-lo
para o GitHub — **crie o repositório como PRIVADO**:

```bash
# 1. github.com/new  →  nome: alpha-whoiam  →  Private  →  criar vazio
#    (sem README, sem .gitignore — já temos os dois)

# 2. aqui no Linux:
cd ~/Downloads/Alpha
git remote add origin git@github.com:<seu-usuario>/alpha-whoiam.git
git push -u origin main
```

Se preferir HTTPS em vez de SSH, troque a URL por
`https://github.com/<seu-usuario>/alpha-whoiam.git` — o GitHub vai pedir um
**token de acesso pessoal** no lugar da senha (Settings → Developer settings →
Personal access tokens).

### No Windows, para pegar o que já existe lá

O código no Windows é o mesmo, mas com histórico próprio (nenhum). O caminho
limpo é clonar por cima:

```powershell
cd C:\Ai-Project
ren Alpha Alpha-antigo
git clone https://github.com/<seu-usuario>/alpha-whoiam.git Alpha
copy Alpha-antigo\voice\config\api_keys.json Alpha\voice\config\
xcopy /E /I Alpha-antigo\studio\bin Alpha\studio\bin
xcopy /E /I Alpha-antigo\voice\models Alpha\voice\models
cd Alpha\studio && npm install
```

`Alpha-antigo` fica ali até você confirmar que tudo funciona. Não apague antes.

## Criar o repositório de conteúdo (no Windows)

```powershell
cd C:\Ai-Project
git init -b main
# grave o .gitignore abaixo, depois:
git add -A
git commit -m "Conteúdo do canal — notas, planos e catálogo"
git remote add origin https://github.com/<seu-usuario>/whoiam-conteudo.git
git push -u origin main
```

`.gitignore` do repositório de conteúdo:

```gitignore
# O código tem repositório próprio.
Alpha/

# Mídia: pesada e só necessária aqui.
**/public/videos/
**/public/audio/
**/public/music/
**/renders/
**/analysis/*.wav
*.mp4
*.mov
*.webm
*.mp3
*.wav
*.m4a
*.png
*.jpg
*.jpeg

# Trilhas: o catálogo sincroniza, as faixas não.
Trilhas/**/*.mp3
Trilhas/**/*.wav

# Cache do Windows
Thumbs.db
desktop.ini
```

Repare que ele **mantém** `notes/*.md`, `scenes.json`, `edit-plan.json`,
`analysis/*.json` e `Trilhas/catalogo.json` — exatamente a coluna da esquerda
da tabela lá em cima.

## O ritual do dia a dia

```bash
git pull      # ao começar
git add -A && git commit -m "o que mudou" && git push     # ao terminar
```

O diário em `DIARIO/` continua sendo o resumo legível do dia; o git é o
histórico exato. Os dois servem para coisas diferentes: o diário conta o
porquê, o git guarda o quê.

## Nunca commitar

`voice/config/api_keys.json` tem a chave real da OpenAI e do Gemini. Está no
`.gitignore`, e existe um `api_keys.example.json` ao lado mostrando o formato.

Se um dia uma chave escapar para um commit: **trocar a chave** é a única
correção real. Remover do histórico não basta — ela já esteve exposta.
