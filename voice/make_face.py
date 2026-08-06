"""Gera o face.png do HUD a partir do ícone do canal, no estilo OMEGA.

Tratamento: recorte quadrado → duotone violeta (sombras quase pretas,
luzes em violeta neon) → contraste → brilho externo (bloom). O resultado
combina com o HUD escuro em vez de brigar com ele.

Rodar de novo depois de trocar o ícone:  python make_face.py [caminho]
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter, ImageOps

ORIGEM_PADRAO = Path(r"C:\Ai-Project\IconePerfil.jpg")
DESTINO = Path(__file__).resolve().parent / "face.png"
LADO = 512

# Extremos do duotone: sombra roxo-escura, luz laranja-brasa (o --cyan do
# style.txt, deslocado para o fogo que o Samuel pediu).
SOMBRA = (30, 6, 2)
LUZ = (255, 176, 130)


def gerar(origem: Path) -> None:
    img = Image.open(origem).convert("RGB")

    lado = min(img.size)
    esq = (img.width - lado) // 2
    topo = (img.height - lado) // 2
    img = img.crop((esq, topo, esq + lado, topo + lado))
    img = img.resize((LADO, LADO), Image.LANCZOS)

    cinza = ImageOps.grayscale(img)
    cinza = ImageEnhance.Contrast(cinza).enhance(1.45)
    duotone = ImageOps.colorize(cinza, black=SOMBRA, white=LUZ)

    # Bloom: as áreas claras vazam luz, como no bloom do WebGL do style.txt.
    luzes = cinza.point(lambda v: 255 if v > 155 else 0)
    glow = Image.new("RGB", duotone.size, (0, 0, 0))
    glow.paste(Image.new("RGB", duotone.size, LUZ), mask=luzes)
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    final = ImageChops.add(duotone, glow, scale=1.7)

    final.convert("RGBA").save(DESTINO)
    print(f"face.png gerado a partir de {origem.name} ({LADO}x{LADO})")


if __name__ == "__main__":
    origem = Path(sys.argv[1]) if len(sys.argv) > 1 else ORIGEM_PADRAO
    if not origem.exists():
        sys.exit(f"Imagem de origem não encontrada: {origem}")
    gerar(origem)
