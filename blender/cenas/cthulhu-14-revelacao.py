# Cthulhu · Bloco 14 — a revelação: ele sai do rombo na montanha
#
# ⚫ PORTÃO 1 aberto pelo Samuel em 2026-09-09. PORTÃO 2 vale: entregar e PARAR.
#
# POR QUE ESTE BLOCO É CASO DE BLENDER (e o 1 não era)
#   O board de teste `THE RISING` provou uma coisa: a criatura saiu BOA — pele,
#   tentáculos, membrana, olho. O que falhou foi GEOMETRIA. O prompt pedia
#   `low knee-level angle looking up` e o modelo entregou altura do peito; pedia
#   árvore como escala e não deu régua nenhuma.
#   Instrução não venceu. Geometria em quadro vence — e é isso que o blockout dá.
#
#   Gatilhos: G1 (escala tem que ler) + G4 (tilt-up que não alcança o topo).
#   NÃO cobre a forma da criatura: os ECU de textura, olho e garra são folha de
#   personagem, não blockout. Ver _registros\BLENDER.md §7.
#
# AS TRÊS CORREÇÕES DO BOARD REPROVADO, TRADUZIDAS EM METROS
#   1. CÂMERA NO CHÃO: 1,5 m de altura. Nunca na altura dele, nunca de cima.
#   2. RÉGUA HUMANA EM QUADRO: dois marinheiros de 1,75 m no primeiro plano.
#      Árvore não serve — o modelo não sabe o tamanho da árvore. Humano ancora.
#   3. O PORTÃO É FRAÇÃO PEQUENA DA PAREDE: 30 m num maciço de 200 m. Sem isso
#      a pedra do bloco 12 não tem de onde cair.
#
# ⚫ Cthulhu = 45 m, FIXO (decisão de 2026-09-09). O conto nunca dá número.

import bpy, os, sys, time, argparse
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--lente", type=float, default=24.0)   # grande-angular: é plano de escala
p.add_argument("--altura-criatura", type=float, default=45.0)
a = p.parse_args(argv)
os.makedirs(a.out, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn, r = bpy.context.scene, bpy.context.scene.render
FPS = 24
F0, F_GARRA, F_TORSO, F1 = 1, 40, 80, 120            # 5 segundos

H = a.altura_criatura
CAM_Y, CAM_Z = -62.0, 1.5      # 62 m: a distancia MINIMA que mantem o chao no quadro
CAM_PERTO_Y = -24.0            # a segunda camera, onde ele excede o enquadramento

def cubo(nome, loc, esc, pai=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = nome; o.scale = esc
    if pai: o.parent = pai
    return o

# ------------------------------------------------------- chão e vegetação
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -60, 0))
ch = bpy.context.object; ch.name = "CHAO"; ch.scale = (400, 300, 1)

# Palmeiras de 18 m — régua SECUNDÁRIA. A primária é humana (ver abaixo).
for i, (x, y) in enumerate(((-38, -18), (34, -22), (-16, -30), (25, -34),
                            (-52, -12), (48, -14), (-8, -45), (14, -50))):
    cubo(f"PALMEIRA_{i:02d}", (x, y, 9.0), (1.6, 1.6, 18.0))

# ---------------------------------------------------- o maciço e o portão
# 200 m de parede. O portão ocupa 15% dela — é o que dá de onde a pedra cair.
cubo("MONTANHA", (0, 60, 100.0), (300, 120, 200.0))
cubo("PORTAO",   (0, -0.5, 15.0), (22, 2.0, 30.0))      # 30 m: fração pequena
cubo("SALIENCIA_QUE_CAI", (6, -1.0, 96.0), (14, 4.0, 10.0))   # o pagamento do bloco 12

# O ROMBO: o buraco que a pedra abriu. É de onde ele sai.
ROMBO_Z = 17.0
cubo("ROMBO", (2, 0.4, ROMBO_Z), (26, 3.0, 20.0))

# ------------------------------------------------------------- o Cthulhu
# Proxy: tronco + cabeça + dois braços + asas dobradas. "Cubos bastam."
# Tudo pendurado num empty na boca do rombo, que SOBE — assim o corpo inteiro
# emerge junto sem eu recalcular posição de cada peça.
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(2, 2, -H * 0.55))
base = bpy.context.object; base.name = "BASE_CRIATURA"

TORSO_H = H * 0.52
cubo("C_TORSO",  (0, 0, TORSO_H / 2), (H * 0.30, H * 0.22, TORSO_H), pai=base)
cubo("C_CABECA", (0, 0, TORSO_H + H * 0.09), (H * 0.15, H * 0.15, H * 0.18), pai=base)
cubo("C_BRACO_E", (-H * 0.22, -H * 0.04, TORSO_H * 0.62), (H * 0.09, H * 0.09, TORSO_H * 0.75), pai=base)
cubo("C_BRACO_D", ( H * 0.22, -H * 0.04, TORSO_H * 0.62), (H * 0.09, H * 0.09, TORSO_H * 0.75), pai=base)
cubo("C_ASA_E", (-H * 0.26, H * 0.10, TORSO_H * 0.80), (H * 0.06, H * 0.02, TORSO_H * 0.55), pai=base)
cubo("C_ASA_D", ( H * 0.26, H * 0.10, TORSO_H * 0.80), (H * 0.06, H * 0.02, TORSO_H * 0.55), pai=base)

for f, z in ((F0, -H * 0.55), (F_GARRA, -H * 0.42), (F_TORSO, -H * 0.10), (F1, 0.0)):
    scn.frame_set(f); base.location = (2, 2, z)
    base.keyframe_insert("location", frame=f)

# ------------------------------------- A RÉGUA: dois humanos de 1,75 m
# Esta é a correção que mais importa. Sem figura humana o gigante lê como
# maquete — foi exatamente o que aconteceu no board reprovado.
for nome, x, y in (("HUMANO_REGUA_A", -14.0, -7.0), ("HUMANO_REGUA_B", -10.5, -5.5)):
    cubo(nome, (x, y, 0.875), (0.45, 0.26, 1.75))

# ------------------------------------------------- valores (separação)
def valor(nome, v):
    m = bpy.data.materials.new(nome + "_M"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (v, v, v, 1)
    m.diffuse_color = (v, v, v, 1)
    o = bpy.data.objects[nome]; o.data.materials.clear(); o.data.materials.append(m)

valor("CHAO", 0.20); valor("MONTANHA", 0.38); valor("PORTAO", 0.30)
valor("SALIENCIA_QUE_CAI", 0.46); valor("ROMBO", 0.06)      # o rombo é o mais escuro
for i in range(8): valor(f"PALMEIRA_{i:02d}", 0.28)
for n in ("C_TORSO", "C_CABECA", "C_BRACO_E", "C_BRACO_D", "C_ASA_E", "C_ASA_D"):
    valor(n, 0.62)
valor("HUMANO_REGUA_A", 0.95); valor("HUMANO_REGUA_B", 0.95)   # a régua é o mais claro

bpy.ops.object.light_add(type='SUN', location=(60, -80, 160))
sol = bpy.context.object
sol.rotation_euler, sol.data.energy = (0.85, 0.15, 0.6), 3.5
w = bpy.data.worlds.new("W"); scn.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.42, 0.44, 0.48, 1)

# ------------------------------------------------ câmera: tilt que NÃO alcança
# O alvo sobe até o PEITO dele, nunca até a cabeça. É assim que o topo escapa do
# quadro: a câmera tenta acompanhar e fica para trás. A escala não vem de dizer
# "gigantesco" — vem da câmera admitir que não dá conta.
bpy.ops.object.empty_add(type='PLAIN_AXES', radius=2.0, location=(2, 2, ROMBO_Z))
alvo = bpy.context.object; alvo.name = "ALVO"
for f, z in ((F0, ROMBO_Z), (F_GARRA, ROMBO_Z + 2.0),
             (F_TORSO, H * 0.30), (F1, H * 0.46)):     # peito baixo: tilt de ~18 graus
    scn.frame_set(f); alvo.location = (2, 2, z)
    alvo.keyframe_insert("location", frame=f)

cd = bpy.data.cameras.new("CAM"); cd.lens = a.lente
cam = bpy.data.objects.new("CAM", cd); scn.collection.objects.link(cam); scn.camera = cam
cam.location = (0.0, CAM_Y, CAM_Z)          # NÃO se move: só inclina
t = cam.constraints.new(type='TRACK_TO'); t.target = alvo
t.track_axis, t.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'

scn.frame_start, scn.frame_end = F0, F1
r.resolution_x, r.resolution_y, r.fps = 854, 480, FPS
t0 = time.time()

r.engine = 'BLENDER_EEVEE'
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'

# SHOT A — wide com a regua humana: ele CABE, e o humano diz o tamanho
for f, nome in ((F0, "A1_rombo"), (F_TORSO, "A2_emergindo"), (F1, "A3_de_pe")):
    scn.frame_set(f); r.filepath = os.path.join(a.out, nome)
    bpy.ops.render.render(write_still=True)

# SHOT B — contra-plongee perto: ele EXCEDE o quadro. Camera fixa, sem tilt,
# apontada para o torso; o topo escapa por cima de proposito.
cdb = bpy.data.cameras.new("CAM_PERTO"); cdb.lens = a.lente
camb = bpy.data.objects.new("CAM_PERTO", cdb); scn.collection.objects.link(camb)
camb.location = (0.0, CAM_PERTO_Y, CAM_Z)
tb = camb.constraints.new(type='TRACK_TO'); tb.target = alvo
tb.track_axis, tb.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'
scn.camera = camb
scn.frame_set(F1); r.filepath = os.path.join(a.out, "B1_excede")
bpy.ops.render.render(write_still=True)
scn.camera = cam

r.engine = 'BLENDER_WORKBENCH'
scn.display.shading.color_type = 'MATERIAL'
r.image_settings.media_type = 'VIDEO'; r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'
r.filepath = os.path.join(a.out, "driver")
bpy.ops.render.render(animation=True)

import glob, shutil
destino = os.path.join(a.out, "driver.mp4")
for f in glob.glob(os.path.join(a.out, "driver0*.mp4")):
    if os.path.abspath(f) != os.path.abspath(destino):
        if os.path.exists(destino): os.remove(destino)
        shutil.move(f, destino)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "cena.blend"))
print("\n" + "=" * 64)
print(f"BLOCO 14 PRONTO em {time.time()-t0:.1f}s -> {a.out}")
print(f"  criatura {H:.0f} m · humano 1,75 m ({H/1.75:.0f}x) · palmeira 18 m")
print(f"  camera a {CAM_Z} m do chao, {abs(CAM_Y):.0f} m da parede, lente {a.lente:.0f}mm")
print("PORTAO 2: mostrar ao Samuel e PARAR.")
print("=" * 64)
