# Conversão de mídia — ffmpeg (absorvido da antiga skill producao-audiovisual-youtube)

Operações técnicas sobre arquivos de vídeo/imagem/áudio. Só funcionam sobre arquivo que o
usuário ENVIOU no chat (fica em /mnt/user-data/uploads/) — nunca prometer operação sobre
arquivo que não está aqui. O ffmpeg está disponível no container do Claude.ai.

Regras invariáveis:
- NUNCA sobrescrever o original. Saídas sempre em /home/claude/ e entregues via /mnt/user-data/outputs/.
- Conversão é etapa técnica, não decisão criativa.
- Nomes de saída padronizados e informar exatamente o que foi feito.

## Comandos de referência

Extrair 1 frame a cada N frames (ex.: a cada 30):
```bash
ffmpeg -i entrada.mp4 -vf "select=not(mod(n\,30))" -vsync vfr frames/frame_%04d.jpg
```

Extrair frame de um instante específico (ex.: 00:01:23):
```bash
ffmpeg -ss 00:01:23 -i entrada.mp4 -frames:v 1 frame_0123.jpg
```

Imagens → vídeo (24 fps):
```bash
ffmpeg -framerate 24 -pattern_type glob -i 'frames/*.jpg' -c:v libx264 -pix_fmt yuv420p saida.mp4
```

Vídeo → GIF (12 fps, largura 640, com paleta para qualidade):
```bash
ffmpeg -i entrada.mp4 -vf "fps=12,scale=640:-1:flags=lanczos,split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse" saida.gif
```

Cortar trecho (para Shorts):
```bash
ffmpeg -ss 00:00:42 -to 00:01:12 -i entrada.mp4 -c copy corte_01.mp4
```

Reenquadrar para vertical 9:16 (crop central):
```bash
ffmpeg -i corte_01.mp4 -vf "crop=ih*9/16:ih" -c:a copy corte_01_vertical.mp4
```

Padronizar FPS:
```bash
ffmpeg -i entrada.mp4 -filter:v fps=30 saida_30fps.mp4
```

Extrair áudio:
```bash
ffmpeg -i entrada.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3
```

## Transcrição de áudio/vídeo local

Se o usuário enviar o arquivo de áudio/vídeo, a transcrição pode rodar aqui com Whisper
(`pip install openai-whisper --break-system-packages`; modelo `small` costuma bastar para PT-BR).
Avisar que é lento para arquivos longos e que a transcrição é RASCUNHO (nomes próprios e termos
podem sair errados). Transcrição de vídeos do YouTube (sem arquivo) é assunto da skill
`pesquisa-seres`, não desta referência.
