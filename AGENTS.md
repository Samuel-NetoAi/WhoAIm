# WhoIAm — instruções do repositório

Para produção visual, ler `whoiam/whoiam/SKILL.md`, única entrada canônica.
Pesquisa Omega entrega dossiê; o Samuel escreve o roteiro com GPT e devolve 20
partes. Componentes e imagens dos blocos são gerados no GPT pela extensão Claude;
Elements e vídeos ficam no Higgsfield. Não usar o CLI/Kairogen para produção visual.

Narração, diálogo e legendas não entram na geração de vídeo. Pós-produção é separada.
`TESTE-ANCORA/` contém experimentos ainda não aprovados como padrão universal.
Não restaurar templates a partir de backups, estudos antigos ou skills instaladas
em outra máquina. Redirecionamentos antigos existem só para não quebrar links.

Ao editar uma skill, executar `python scripts/sincronizar_skills.py` e depois
`python scripts/sincronizar_skills.py --check`. Pacotes `.skill` são derivados.
Não instalar ou sobrescrever skills pessoais automaticamente.

O acervo real das criaturas vive em `AI_PROJECT_ROOT/Criaturas`, fora desta cópia
quando não configurado. Não inventar que os renders ou Elements existem.
Blender só é executado quando solicitado; revisão de código não abre nem renderiza cenas.
