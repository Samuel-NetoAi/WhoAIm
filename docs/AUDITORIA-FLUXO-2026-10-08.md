# Auditoria e consolidação — 2026-10-08

Escopo: produção visual WhoIAm, roteamento do Omega e fontes que poderiam reativar
o método antigo. Não houve geração de imagens/vídeos, operação de conta externa ou
alteração dos prompts experimentais ATUAL/NOVO. O acervo de criaturas não está nesta
cópia e nenhuma criatura foi escolhida para produção.

## Conflitos encontrados e decisão

| Encontrado | Melhor eliminar | Aplicado |
|---|---|---|
| Skill produzia roteiro; usuário entrega roteiro aprovado | Escrita automática a partir do dossiê | Skill recebe 20 partes; pesquisa encerra no dossiê |
| Omega oferecia model sheets, storyboard e vídeo Kairogen | Executor de produção visual do CLI | Removidos prompts, parâmetros e ferramentas Kairogen; aliases antigos apenas orientam |
| Skill/guia/regras/estudos continham vários templates concorrentes | Templates antigos e suas cópias | Um contrato em `references/prompt-video.md`; caminhos antigos são redirecionamentos |
| Grades obrigatórias, pisos de painéis, storyboard opcional e referência por corte conviviam | Obrigação de grade e quantidades fixas | Referências individuais por função e necessidade do bloco |
| Texto antigo mandava usar/evitar Elements conforme limitações do MCP | Regras de UI inferidas do MCP | Extensão lê UI real, registra label e vínculo; GPT gera imagens |
| Âncora ultra-realista universal versus experimento naturalistic | Obrigação universal de âncora antiga | Âncora por componente; experimentos intactos e identificados como testes |
| Exceção de diálogo na geração contradizia decisão atual | Delivery, sotaque, falas e exceção de áudio para voz | Nenhuma voz/legenda na geração; pós separada |
| `.skill` não correspondia às pastas: WhoIAm tinha 8 arquivos divergentes e 10 ausentes | Pacote tratado como fonte independente | Empacotamento reproduzível e comando de conferência |
| Número de fase antigo podia significar tarefa diferente no fluxo novo | Reuso automático de aprovação legada | Omega usa `etapas-omega.json`; produção usa manifesto/estado versionados |
| Arquivo antigo podia ser relatado como resultado de nova execução | Sucesso só pela existência | Pesquisa confere arquivo criado/atualizado e não vazio |
| Preços e plano históricos embutidos na calculadora | Tabela apresentada como vigente e presets mistos | Preço informado explicitamente, padrão 20 blocos; sem custo de imagem Higgsfield |
| Nomes de arquivo e Elements não tinham contrato único de retorno | Correspondências implícitas e handles inventados | ID, label planejado/real, token real, versão, arquivo e conferência |

A recomendação é manter somente o lado aplicado da tabela. Os redirecionamentos
não contêm o modelo antigo; existem para links e nomes usados anteriormente ainda
levarem ao contrato novo. Estudos operacionais antigos da raiz foram substituídos
por redirecionamento; suas transcrições não permanecem como receitas concorrentes.
Lições empíricas relevantes foram condensadas em `avaliacao-e-aprendizado.md`.

## O que entrou dos estudos

- Cane Man: contexto que não deve ser reencenado; momento explícito de revelação;
  ordem causal; corte ligado à ação; poucas travas específicas da cena.
- Detour: função e exclusão por referência; reverso e escala quando necessários;
  início/chegada por shot; versão de estado; detalhe concentrado no evento difícil.
- Nosso conhecimento preservado: gatilho e atuação corporal, câmera com percurso
  e término, peso e consequência, referência por necessidade, legibilidade em baixa
  resolução, diagnóstico e aprovação do bom sem perseguir perfeição.
- Não incorporados: falas, legendas, CAPS excessivo, quota de caracteres, número
  fixo de imagens, plano longo obrigatório, alegações de superioridade não medidas.

## Fluxo final

Omega/pesquisa → Samuel lê e escreve com GPT → entrega roteiro aprovado em 20
partes → inventário global → extensão gera componentes no GPT e cataloga Elements
→ para cada B01…B20: documento de componentes → prompts e imagens de referência
no GPT → conferência → prompt de vídeo → execução Higgsfield → retorno e avaliação
→ pós-produção separada → publicação sob pedido.

Só o contrato de vídeo está estabilizado nesta revisão. A estética de imagens
continua em avaliação: criatura ultra-realista e humano/ambiente naturalistic são
a tendência informada, não um resultado universal comprovado. O executor deve
usar a âncora escolhida para aquele componente e harmonizar a cena composta.

30 s, 480p e 16:9 ficaram como padrões herdados até nova decisão. A escolha entre
SFX/ambiente gerado e vídeo mudo ficou pendente de resposta; nenhum dos modos é
inventado pelo executor. Isso não impede preparar documentos; impede apenas
executar vídeo sem a configuração de som definida. Vozes seguem desativadas.

## Arquivos centrais e ferramentas

- `whoiam/whoiam/SKILL.md`: entrada e etapas.
- `references/prompt-video.md`: único formato de vídeo.
- `references/componentes-e-execucao.md`: pastas, manifesto, tarefas e retorno.
- `references/avaliacao-e-aprendizado.md`: critérios e correções.
- `scripts/projeto.py` dentro da skill: criação idempotente e validação local.
- `scripts/sincronizar_skills.py` na raiz: pacotes `.skill` derivados das fontes.
- `voice/tools/pipeline.py` e `fases.py`: retirada do executor antigo e encaminhamento.

Código de edição, alinhamento, narração da pós e upload foi preservado. Regras de
publicação foram ajustadas apenas na fronteira de produção de imagens/roteiro.
Skills instaladas fora deste repositório não foram sobrescritas. O Omega agora
aponta explicitamente para a pesquisa local para evitar carregar uma cópia antiga.

## Verificação e limites

**26 testes locais passaram** (fluxo, comandos, guardas e diagnóstico). Cobrem: aliases antigos sem geração, pesquisa sem ferramentas de
mídia, estado legado isolado, roteiro sem aprovação, catálogo sem assets, 20 blocos,
reentrada sem sobrescrita, nomes/caminhos, inconsistências de manifesto e resultado
antigo não apresentado como novo. Validação de skill e dos pacotes também executada.

Os testes de integração do motor gratuito exigem `sounddevice`, ausente aqui;
o módulo de testes de narração/interface exige `PyQt6`, também ausente. Não houve
validação de ponta a ponta do aplicativo de voz ou da extensão/navegador.

## Recuperação

Sem Git nesta pasta. Antes de editar, foi criada uma cópia externa integral:
`/home/sami/Downloads/WhoAIm-backup-antes-fluxo-2026-10-08-071835.tar.gz`.
É recuperação manual, não contexto de produção. Não deve ser instalada nem lida
como skill corrente. Nenhuma instalação pessoal foi alterada.
