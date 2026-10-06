# Publicar no YouTube — o que só o Samuel pode fazer

> O código está pronto e testado. O que falta são **seis passos no navegador**, todos
> na sua conta. Depois disso o Omega sobe vídeo sozinho.
>
> **Nada aqui passa pelo chat.** Você baixa um arquivo e salva numa pasta. Chave que
> passa pelo chat fica em texto puro no transcript para sempre — é lição registrada.
>
> O porquê de cada regra está em `D:\Agentes\_registros\YOUTUBE.md`.

---

## Antes de começar: o que esperar

**O primeiro vídeo vai nascer privado, e isso é o certo.** Regra oficial do YouTube:
projeto de API não auditado sobe vídeo travado em privado. Não é erro do código — o
código inclusive avisa quando isso acontece, em vez de dizer que publicou.

**Isso não impede nada agora.** Você sobe pelo Omega, o vídeo chega na sua conta como
privado, e você abre o YouTube Studio e troca para público com dois cliques. O ganho já
é real: título, descrição, tags e a flag de IA vão certos e sem digitação.

Automatizar **até o vídeo sair público** exige a auditoria, que pede domínio próprio e
política de privacidade. Isso é decisão sua, depois, e não bloqueia nada disto.

---

## Os seis passos

### 1. Criar o projeto
https://console.cloud.google.com → seletor de projeto → **Novo projeto**.
Nome sugerido: `omega-whoiam`.

### 2. Ligar a API
Menu → **APIs e serviços → Biblioteca** → buscar **"YouTube Data API v3"** → **Ativar**.

### 3. Tela de consentimento OAuth
**APIs e serviços → Tela de permissão OAuth**.
- Tipo: **Externo**
- Preencha nome do app, seu e-mail de suporte e seu e-mail de contato
- **Deixe o status de publicação em "Teste"** — não clique em "Publicar app"
- Em **Usuários de teste**, adicione **o seu próprio e-mail**

> **Por que ficar em "Teste":** o Google dispensa a verificação de escopo sensível
> (que leva 3 a 5 dias úteis) quando *"você é o único usuário do app"*. Ficar em Teste
> é justamente essa exceção. Publicar o app te joga na fila sem precisar.

### 4. Criar a credencial
**APIs e serviços → Credenciais → Criar credenciais → ID do cliente OAuth**
- Tipo de aplicativo: **App para computador** (*Desktop app*)
- Nome: `omega-uploader`

### 5. Baixar e salvar
Clique em **Fazer o download do JSON**. Salve o arquivo como:

```
C:\Ai-Project\Omega\youtube\client_secret.json
```

O nome tem que ser exatamente esse. **Não abra o conteúdo no chat comigo** — ele já está
no `.gitignore` e não vai para o git.

### 6. Autorizar, uma vez só

```
python C:\Ai-Project\Omega\youtube\publicar.py autorizar
```

Abre o navegador. Escolha a conta do canal. Vai aparecer um aviso de **"app não
verificado"** — é esperado, é o seu próprio app: **Avançado → Acessar (não seguro)**.
Terminado isso, o token fica guardado cifrado por **DPAPI** (só descriptografa com a sua
conta do Windows, nesta máquina).

---

## Conferir

```
python C:\Ai-Project\Omega\youtube\publicar.py verificar
```

Diz em que passo você está, sem subir nada e sem gastar cota. Se der certo, mostra o
nome do canal.

## Subir

```
python C:\Ai-Project\Omega\youtube\publicar.py subir "video.mp4" ^
    --titulo "..." --descricao "..." --tags "mitologia,creepy" ^
    --privacidade private --sintetico
```

`--sintetico` é **obrigatório para este canal** e não tem default: o YouTube exige
declarar mídia sintética desde 2024-10-30, e "cena realista que não aconteceu" é
exatamente o que produzimos. O comando recusa rodar se você não declarar um dos dois.

---

## Dois avisos honestos

⚠️ **Refresh token em app "em Teste" pode expirar em ~7 dias.** É um comportamento
conhecido do OAuth do Google para apps não publicados. **Não consegui confirmar se ainda
vale em 2026** — nenhuma fonte do levantamento fala disso. Se a publicação periódica
parar de funcionar depois de uma semana, é quase certo que seja isto, e o conserto é
rodar `autorizar` de novo. **Vamos descobrir medindo, não supondo.**

⚠️ **Cartão:** nenhuma página oficial menciona cobrança para a Data API — o modelo é
cota, não dinheiro. Mas também nenhuma página oficial afirma "não pede cartão". **Se o
Cloud Console pedir cartão em algum passo, pare e me chame** — cadastrar cartão é
decisão sua, e a regra da casa é que isso nunca é ação de agente.

---

## Limites que já valem hoje

| | |
|---|---|
| Uploads por dia | **100** (balde próprio, 1 unidade cada) |
| Zera | meia-noite do Pacífico |
| Limite por canal | existe, separado da cota — erro `uploadLimitExceeded`, esperar 15+ min |
| Escopo usado | `youtube.upload` — sobe o vídeo e nada mais |

**Thumbnail e playlist NÃO entram por aqui**, de propósito: exigiriam o escopo largo
`youtube`, que é mais difícil de passar em revisão. Continuam manuais, com o pacote que
a skill `postagem` já monta.
