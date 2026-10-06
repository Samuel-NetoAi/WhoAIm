# Exemplo aplicado — Cthulhu (não é a regra, é uma aplicação dela)

> Este arquivo é o mapeamento Camera/Lens/Aperture/Lighting/Color palette que eu fiz manualmente
> pro projeto Cthulhu em 15/08/2026, ANTES de existir a tabela genérica. Preservado aqui como
> prova de conceito e gabarito de conferência — a regra de verdade agora vive em
> `higgsfield-presets.md`. Se os dois divergirem num caso, a tabela genérica vence; volte aqui só
> pra ver como uma aplicação real ficou.

## CÂMERA — aba "Setup" (Camera / Lens / Aperture)

Confirmado nos prints: cada coluna tem pelo menos 3 opções visíveis + Auto. Pode haver mais
rolando pra baixo — não confirmado.

### Camera (corpo)
| Botão visto | Quando usar | Por quê |
|---|---|---|
| **Modern** | Padrão pra quase todo bloco do canal | Bate com a âncora de realismo ("cinema camera") que todo prompt já usa — imagem limpa, contemporânea |
| **DV Camcorder** | Só se algum dia o canal quiser um registro "encontrado"/amador — não é o caso do Cthulhu | Textura de vídeo doméstico, verité — contradiz o "ultra-realista cinematográfico" que é o padrão do canal |
| **Auto** | Blocos puramente atmosféricos sem ênfase de câmera (ex.: Bloco 1, 21, 22 — R'lyeh) | Deixa o sistema decidir quando o corpo da câmera não é o que carrega a cena |

### Lens (lente)
| Botão visto | Quando usar | Por quê |
|---|---|---|
| **Clean Sharp** | Padrão — a maioria dos blocos, especialmente 50mm/documental (Bloco 9, 12, 25, 30) | Neutro, sem estilização — o mesmo espírito do "50mm, olho humano" da nossa tabela |
| **Halation Vintage** | Usar com cautela — só se algum bloco pedir memória/lenda em vez de registro direto (nenhum bloco do Cthulhu pede isso hoje) | Halo de luz nos brilhos = onírico/nostálgico. Bate com "registro de lenda" da `pesquisa-seres`, mas conflita com a âncora "RAW photo" que todo prompt já carrega — **não usar em blocos de ação ou revelação de Cthulhu** |
| **Auto** | Blocos onde a lente não é o ponto (a maioria dos contemplativos) | — |

### Aperture (abertura)
| Botão visto | Quando usar | Por quê | Blocos do Cthulhu |
|---|---|---|---|
| **f/1.4 Wide Open** | Todo close-up/reação/presságio — bate 1:1 com "Shallow DOF = isolar, só isto importa" | Blocos 2 (ECU pés/boca), 7 (água mudando de cor), 32 (brilhos vermelhos), 36 (o amigo enlouquecendo), 38 (Johansen assume o leme) |
| **f/11 Deep Focus** | Todo wide de ambiente onde o fundo precisa continuar ameaçador — bate 1:1 com "Deep focus = a ameaça mora no ambiente inteiro" | Blocos 21, 22, 26, 27 (R'lyeh), 37 (emergência completa) |
| **Auto** | Blocos de transição/estabelecimento sem ênfase de profundidade | Blocos 3, 5, 11, 19 |

## LIGHTING

| Botão visto | Quando usar | Blocos do Cthulhu |
|---|---|---|
| **Practicals** | Toda cena com fonte de luz visível na própria cena | Blocos 1-9 (lampiões a gás de Londres), 10 (lâmpada da biblioteca), 20 (lâmpada da cabine do capitão do culto), 42 (biblioteca de Francis) |
| **Silhouette** | Toda revelação de criatura como forma antes de ser corpo | Bloco 37 (primeira emergência de Cthulhu), Bloco 1 (a cidade em contraluz noturno) |
| **Window** | Interior com uma fonte direcional forte vinda de abertura | Testar em Bloco 10/42 (biblioteca) se a referência de ambiente tiver janela |
| **Overhead fall** | Luz dramática vinda de cima | Testar no Bloco 29 (a rocha caindo do céu) e Bloco 32 (aproximação do brilho vermelho) |
| **Auto** | Blocos de névoa densa sem fonte pontual clara | Blocos 21, 22, 26 (R'lyeh, névoa dominando) |

## COLOR PALETTE — aplicação por ambiente do Cthulhu

| Ambiente/momento do Cthulhu | Blocos | 1ª opção | 2ª opção |
|---|---|---|---|
| Londres, cais noturno, chuva | 1-9 | **Industrial Fog** | Twilight Fable |
| Doca/navio visto de longe | 3, 5 | **The Investigation** | Industrial Fog |
| Biblioteca (navio de Thurston, e Bloco 42) | 10, 42 | **Oil & Ochre** | The Mountain Convent |
| O Alert na tempestade | 11-19 | **Breakfast on Schedule** | Home Is the Next Gas Station |
| Cabine ritual do navio do culto | 20 | **The Circus** | Crimson Vigil |
| R'lyeh — ilha, névoa, ruínas | 21-27, 37 | **The Emerald Ambush** | The Morning After Rain |
| Portão, tentáculos, brilho vermelho | 28-34 | **Stairs Go Up** | Ghost in the Code |
| Regeneração/glow sobrenatural | 32, 43 | **Bioluminescent Night** | Ghost in the Code |
| Confronto/clímax com Cthulhu | 36-40 | **A Hotel for One** | After Dark |
| Epílogo — o culto aparece | 42 | **The Grey Channel** | — |

Descartadas de cara (tom quente/diurno/vibrante, fora do registro do canal): Static Noon, Back Row
Kissing Seats, On the Other Side of the Port, Highway Standoff, The Faded Fresco, Pink Velvet, Two
Days to the Horizon, Field Post, Glossy Flesh, The Crimson Ballet, Neon Rain at Midnight, The Iron
Borough, The Ground, Turquoise Mirage, A Dream in Color, Favela Gold, The Neighbors Saw
Everything, Mirage at Noon, Bubblegum Boulevard, Yellow Room, The Earth Keeps Things, Tropic Fever
Dream, The Butterfly, Wallpaper Romance, The Way Home Is Longer, Runaway Summer, Amber Wasteland,
Gasoline Sunset, Don't Turn It Off I'm Watching, The Silk Curtain Falls, Playtime, Overtime,
Everyone Speaks in Whispers.
