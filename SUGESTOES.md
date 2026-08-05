# SUGESTÕES — caminhos que decidi NÃO tomar sozinho

> Você pediu liberdade total, então executei o que tinha resposta clara.
> Estes são os pontos onde havia mais de um caminho razoável e a escolha é
> sua. Cada item diz o que eu faria, alternativas, e o custo aproximado.

## 1. Upscale/interpolação com IA (recomendo: sim, quando tiver créditos)
O que fiz: upscale lanczos 2x (nítido, mas não cria detalhe novo) e
interpolação minterpolate (boa, mas borra em movimento rápido).
Alternativa melhor: **Real-ESRGAN** (upscale) e **RIFE** (interpolação),
ambos com binários Windows gratuitos que usam sua GPU NVIDIA. Não instalei
porque são +600MB de downloads e o ganho só aparece em cena com muito
detalhe — teste primeiro o que já está pronto. Roteiro exato de instalação
está no PLANO-ALPHA.md (Próximos passos 2–3).

## 2-A. Publicação no YouTube pelo Jarvis — PEDIDO PELO SAMUEL, bloqueado em credenciais

Ele quer: "Jarvis, publica o vídeo da Medusa" → sobe o render do Studio para
o canal, com título/descrição/tags/thumb ditados por voz (estratégia a ser
definida após um curso de algoritmo do YouTube que ele fará).

**O que trava:** a YouTube Data API v3 exige OAuth2 próprio, que só o dono da
conta cria. Passos (10 min, no navegador):
1. console.cloud.google.com → criar projeto (ex. "Alpha Studio")
2. "APIs e serviços" → Ativar APIs → **YouTube Data API v3** → Ativar
3. Tela de consentimento OAuth → tipo **Externo** → preencher nome/e-mail →
   adicionar o próprio e-mail em "Usuários de teste"
4. Credenciais → Criar credenciais → **ID do cliente OAuth** → tipo
   **App para computador**
5. Baixar o JSON e salvar como `C:\Ai-Project\Alpha\voice\config\youtube_client.json`

Com esse arquivo, dá para construir + testar a ferramenta de upload (fluxo
`InstalledAppFlow`, abre o navegador uma vez para autorizar, guarda o token).
Cota: upload custa 1600 unidades de 10.000/dia → ~6 uploads/dia, suficiente.
**Recomendação:** subir sempre como **"não listado"** e você revisar antes de
tornar público — o Jarvis nunca deve publicar direto sem sua confirmação.

## 2-B. Publicação automática (TikTok) — decisão 100% sua
Existe conexão MCP com TikTok disponível no ambiente (publicação direta).
NÃO toquei nisso: publicar automaticamente é irreversível e envolve a conta
do canal. Se quiser, o fluxo seria: render pronto → botão "Publicar" no
Studio → confirmação manual sempre.

## 3. Geração de vídeo/imagem DENTRO do Studio
Você mencionou que APIs de vídeo/áudio/narração podem ser atualizações
futuras — concordo e não implementei. Quando quiser: os conectores
(Higgsfield/Freepik/ElevenLabs) já existem como MCP na sua conta Claude;
o caminho mais barato é continuar gerando pela conversa (skills whoiam)
e usar o Studio só pra montagem. Integrar direto no Studio exigiria
guardar chaves de API em .env local — funciona, mas cada geração custa
créditos dessas plataformas de qualquer forma.

## 4. Migração automática das criaturas antigas
BabaYaga (zip), Cthullhu (VideoSeeDance1/2), Sobek (PNGs soltos) etc. não
seguem o formato `<nome>-video\public\videos\`. NÃO migrei automaticamente
porque envolve decidir o que é clipe final vs. rascunho em cada pasta — você
conhece o material, eu não. Quando quiser, peça: "padroniza a pasta do
Cthullhu pro formato do Studio" (é mecânico e rápido).

## 5. Mark-XXXIX (o Jarvis por voz)
Mantive como está em Alpha\Mark-XXXIX-OR-main — é um projeto Python que usa
OpenRouter (pago, chave própria). Integração que recomendo SE você quiser
seguir: o Mark chama as rotas HTTP do Studio por voz ("renderiza o short da
Medusa"). Não misturar os dois códigos. Custo: médio (1 sessão de trabalho).
Alternativa mais simples que talvez te atenda: continuar usando a mim como
"voz" do sistema — as skills já cobrem pesquisa→prompts, e o Studio cobre
edição sem gastar tokens.

## 6. Aba Notas usa markdown puro (sem editor rico)
Decidi textarea simples pra economizar créditos. Se quiser visual melhor
(preview de markdown, imagens), é upgrade fácil de pedir depois.

## 7. Backup
Nada em C:\Ai-Project tem backup automático. Sugestão barata: transformar
C:\Ai-Project num repositório git (sem os vídeos — .gitignore em renders/,
public/videos/, node_modules/) e/ou sincronizar a pasta com um drive na
nuvem. Não fiz porque envolve sua conta/preferência de serviço.
