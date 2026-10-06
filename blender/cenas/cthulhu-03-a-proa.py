# Cthulhu · Bloco 3 — "A proa": o cachimbo sob a chuva, o vulto atras, a
# silhueta no mar, o capitao chama.
#
# PORTAO 1 aberto pelo Samuel em 2026-09-10/11 ("faca com o blender para ter
# uma boa movimentacao de camera"). Gatilho: G4 (movimento que o texto
# descreve mal) — pedido explicito.
# PORTAO 2 continua valendo: entregar frame01.png + driver.mp4 e PARAR.
#
# O QUE ESTE BLOCKOUT COBRE, E O QUE NAO
#   Cobre a metade GEOMETRICA: o conves/amurada do navio (afunilando pra
#   proa), o Francis de pe junto a amurada, o vulto atras dele, e o
#   movimento de camera que e o ponto do bloco — sai perto do Francis e
#   empurra pra frente ate abrir o horizonte, trocando de alvo (dele pro
#   ponto no mar) sem corte. Isso e G4 puro, a mesma tecnica de ALVO do
#   bloco 1 (empty com influencia de constraint animada).
#
#   NAO cobre a chuva (textura/atmosfera — fica no prompt do Seedance) nem
#   a silhueta/nevoa do Cthulhu no mar (blockout nao da forma nem silhueta
#   — ver _registros\BLENDER.md §7). O marcador SILHUETA_NEVOA e um Empty:
#   nao renderiza, so guia a camera. A forma entra pela referencia de
#   imagem do bloco 1a na hora da geracao.
#
# MEDIDAS — METROS, escala real
#   conves 6,0 largura x ~16,0 comprimento (meia-nau ate a proa)
#   Francis 1,75 · vulto ~1,85 (mais largo, deliberadamente sem anatomia)
#   proa (ponta onde as amuradas convergem) em Y=8,0

import bpy, os, sys, time, argparse
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
p.add_argument("--lente", type=float, default=35.0)
a = p.parse_args(argv)
os.makedirs(a.out, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scn, vl, r = bpy.context.scene, bpy.context.view_layer, bpy.context.scene.render
FPS = 24
F_A, F_B, F_C, F_D = 1, 40, 84, 192      # ~8s: Francis -> vulto revelado -> capitao chama -> proa aberta

def cubo(nome, loc, esc, pai=None, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = nome; o.scale = esc; o.rotation_euler = rot
    if pai: o.parent = pai
    return o

# ---------------------------------------------------------------- o conves
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 2.0, 0))
ch = bpy.context.object; ch.name = "CONVES"; ch.scale = (3.0, 8.0, 1)

# amuradas convergindo pra proa (Y=8): dois cubos finos, angulados pra dentro
cubo("AMURADA_ESQ", (-1.5, 2.0, 1.0), (0.05, 4.2, 0.05), rot=(0, 0, 0.18))
cubo("AMURADA_DIR", ( 1.5, 2.0, 1.0), (0.05, 4.2, 0.05), rot=(0, 0, -0.18))
PROA_PONTA = Vector((0.0, 8.0, 1.0))

# --------------------------------------------------------------- o Francis
# de pe junto a amurada, olhando pra frente (nunca pra lente — ver DIRECAO.md)
FRANCIS_BASE = Vector((-0.8, 1.0, 0.0))
bpy.ops.object.empty_add(type='PLAIN_AXES', location=FRANCIS_BASE + Vector((0, 0, 0.9)))
tronco_f = bpy.context.object; tronco_f.name = "FRANCIS_QUADRIL"

cubo("FRANCIS_PERNAS", FRANCIS_BASE + Vector((0, 0, 0.45)), (0.40, 0.30, 0.90))
cubo("FRANCIS_TORSO", (0, 0, 0.35), (0.45, 0.26, 0.70), pai=tronco_f)
cubo("FRANCIS_CABECA", (0, 0, 0.80), (0.20, 0.24, 0.26), pai=tronco_f)

bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.05, location=(0, 0, 0.80))
foco_francis = bpy.context.object; foco_francis.name = "FOCO_FRANCIS"
foco_francis.parent = tronco_f

# ------------------------------------------------------------------ vulto
# Deliberadamente sem anatomia — um bloco de capa mais largo que o Francis e
# um pouco mais alto. E "vulto", nao personagem: a forma nao deve competir
# com a leitura do Francis nem antecipar rosto nenhum.
VULTO_BASE = Vector((-0.3, 0.35, 0.0))
cubo("VULTO_CORPO", VULTO_BASE + Vector((0, 0, 0.90)), (0.55, 0.40, 1.80))

# ------------------------------------------------------- marcador do mar
# So orienta a camera. Nao tem material, nao aparece no render — a forma da
# silhueta vem da referencia de imagem do bloco 1a, nunca do blockout.
bpy.ops.object.empty_add(type='SPHERE', radius=0.3, location=(0.0, 45.0, 1.2))
silhueta_marca = bpy.context.object; silhueta_marca.name = "SILHUETA_NEVOA"

# --------------------------------------------------- valores (separacao)
def valor(nome, v):
    m = bpy.data.materials.new(nome + "_M"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (v, v, v, 1)
    m.diffuse_color = (v, v, v, 1)
    o = bpy.data.objects[nome]
    o.data.materials.clear(); o.data.materials.append(m)

for nome, v in (("CONVES", 0.28), ("AMURADA_ESQ", 0.40), ("AMURADA_DIR", 0.40),
                ("FRANCIS_PERNAS", 0.78), ("FRANCIS_TORSO", 0.82), ("FRANCIS_CABECA", 0.92),
                ("VULTO_CORPO", 0.18)):   # o vulto e o mais escuro do quadro, de proposito
    valor(nome, v)

# ------------------------------------------------------------------- luz
bpy.ops.object.light_add(type='SUN', location=(2.0, -1.0, 3.0))
sol = bpy.context.object
sol.rotation_euler, sol.data.energy = (0.9, 0.15, -1.1), 3.0

w = bpy.data.worlds.new("W"); scn.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.24, 0.26, 0.30, 1)

# ------------------------------------------------ o ALVO e a camera
# Mesma tecnica do bloco 1: o alvo comeca no Francis (copiando FOCO_FRANCIS)
# e solta pra SILHUETA_NEVOA — a camera troca de assunto na frente do
# espectador, sem corte.
bpy.ops.object.empty_add(type='SPHERE', radius=0.08, location=FRANCIS_BASE + Vector((0, 0, 0.80)))
alvo = bpy.context.object; alvo.name = "ALVO"
copia = alvo.constraints.new(type='COPY_LOCATION')
copia.target = foco_francis
for f, inf in ((F_A, 1.0), (F_C, 1.0), (F_D, 0.0)):
    scn.frame_set(f); copia.influence = inf
    copia.keyframe_insert("influence", frame=f)
alvo.location = silhueta_marca.location

cd = bpy.data.cameras.new("CAM"); cd.lens = a.lente
cam = bpy.data.objects.new("CAM", cd); scn.collection.objects.link(cam); scn.camera = cam
t = cam.constraints.new(type='TRACK_TO'); t.target = alvo
t.track_axis, t.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'

for f, loc in ((F_A, (-0.30,  0.30, 1.55)),   # perto do Francis, quase por tras do ombro
               (F_B, ( 0.45,  0.15, 1.60)),   # arco leve — revela o vulto atras dele
               (F_C, ( 0.10,  3.20, 1.40)),   # comeca a empurrar pra proa (o capitao chama)
               (F_D, ( 0.00,  6.80, 1.25))):  # chegou perto da ponta da proa, olhando pro mar
    scn.frame_set(f); cam.location = loc; cam.keyframe_insert("location", frame=f)

scn.frame_start, scn.frame_end = F_A, F_D
r.resolution_x, r.resolution_y, r.fps = 854, 480, FPS
t0 = time.time()

# start/mid/end frame em EEVEE (vale a luz) — driver em Workbench (rapido)
r.engine = 'BLENDER_EEVEE'
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'
for f, nome in ((F_A, "frame01_francis"), (F_C, "frame02_vulto_capitao"),
                (F_D, "frame03_horizonte")):
    scn.frame_set(f); r.filepath = os.path.join(a.out, nome)
    bpy.ops.render.render(write_still=True)

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
print("\n" + "=" * 62)
print(f"BLOCO 3 PRONTO em {time.time()-t0:.1f}s -> {a.out}")
print(f"  {(F_D-F_A)/FPS:.1f}s · lente {a.lente}mm · 854x480")
print("  frame01_francis · frame02_vulto_capitao · frame03_horizonte · driver.mp4")
print("PORTAO 2: mostrar ao Samuel e PARAR.")
print("=" * 62)
