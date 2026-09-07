# blockout.py — greybox de um plano, para referência do Seedance 2.5
#
# ⚫ OS DOIS PORTÕES (Samuel, 2026-09-06) — valem acima deste arquivo:
#   Portão 1: AVISAR o Samuel antes de rodar isto. Qual plano, qual gatilho, o que vai ser blocado.
#   Portão 2: entregar `frame01.png` + `driver.mp4` e PARAR. Só com a palavra dele vai para geração.
#   Gatilhos (lista fechada): §0 de D:\Agentes\_registros\BLENDER.md
#
# Uso:
#   "C:\Program Files\Blender Foundation\Blender 5.2\blender.exe" -b -P blockout.py -- \
#       --out "C:\Ai-Project\Criaturas\Medusa\medusa-video\blockout\plano07" \
#       --frames 120 --lente 35 --criatura 4.0
#
# Saídas: frame01.png (start frame) · driver.mp4 (referência de movimento) · cena.blend
#
# Medido nesta máquina em 2026-09-06 (RTX 3050 8GB): Workbench ~0,3 s/frame, EEVEE ~9,8 s/frame
# com world. Por isso o driver sai em Workbench e só o start frame em EEVEE.
#
# ARMADILHAS DA API 5.x já resolvidas aqui (custaram três execuções):
#   - o engine é 'BLENDER_EEVEE', NÃO 'BLENDER_EEVEE_NEXT' (que não existe mais)
#   - action.fcurves morreu; Actions são slotted (layers -> strips -> channelbags)
#   - scene.view_layer não existe; use bpy.context.view_layer
#   - media_type ANTES de file_format, sempre

import bpy, os, sys, time, argparse

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
p = argparse.ArgumentParser()
p.add_argument("--out", required=True, help="pasta de saída do plano")
p.add_argument("--frames", type=int, default=120, help="duração em frames (24fps). 120 = 5 s")
p.add_argument("--lente", type=float, default=35.0, help="distância focal em mm")
p.add_argument("--criatura", type=float, default=4.0, help="altura da criatura em metros")
p.add_argument("--largura", type=int, default=854)
p.add_argument("--altura", type=int, default=480)
a = p.parse_args(argv)

os.makedirs(a.out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
scn, vl, r = bpy.context.scene, bpy.context.view_layer, bpy.context.scene.render

def box(nome, loc, escala):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = nome; o.scale = escala
    return o

# --- a cena. Escala em METROS: é o que dá o plano de escala (gatilho G1). ---
from mathutils import Vector

CAM0   = Vector((9.0, -12.0, 1.6))    # posição inicial da câmera
ALVO   = Vector((-1.5, 2.5, 0.0))     # onde a criatura fica

bpy.ops.mesh.primitive_plane_add(size=80); bpy.context.object.name = "CHAO"
c = a.criatura
box("CRIATURA", (ALVO.x, ALVO.y, c / 2), (c * 0.55, c * 0.40, c))    # proporção mantida

# O humano é a régua do plano. Se ele ficar OCLUSO pela criatura, o gatilho G1 não se
# cumpre — então ele é posicionado PERPENDICULAR ao eixo câmera→criatura, e um pouco à
# frente, em vez de numa coordenada fixa que some quando a criatura cresce.
eixo = (ALVO.xy - CAM0.xy).normalized()
perp = Vector((-eixo.y, eixo.x))
folga = c * 0.55 + 1.4                       # meia-largura da criatura + respiro
pos = ALVO.xy + perp * folga + (CAM0.xy - ALVO.xy) * 0.30   # afasta e traz para frente
box("HUMANO", (pos.x, pos.y, 0.875), (0.45, 0.25, 1.75))     # referência: 1,75 m

box("MASSA_A", (-6.0, 6.0, 3.00), (1.20, 1.20, 6.00))
box("MASSA_B", ( 6.0, 9.0, 4.00), (1.50, 1.50, 8.00))

bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sol = bpy.context.object; sol.rotation_euler = (0.9, 0.2, -0.6); sol.data.energy = 4.0
w = bpy.data.worlds.new("W"); scn.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.28, 0.33, 1)

# --- câmera: lente real, dolly animado, travada na criatura ---
cd = bpy.data.cameras.new("CAM"); cd.lens = a.lente
cam = bpy.data.objects.new("CAM", cd); scn.collection.objects.link(cam); scn.camera = cam
trk = cam.constraints.new(type='TRACK_TO'); trk.target = bpy.data.objects["CRIATURA"]
trk.track_axis = 'TRACK_NEGATIVE_Z'; trk.up_axis = 'UP_Y'

F0, F1 = 1, max(2, a.frames)
scn.frame_start, scn.frame_end = F0, F1
for f, loc in ((F0, tuple(CAM0)), (F1, (3.0, -6.0, 2.4))):
    scn.frame_set(f); cam.location = loc; cam.keyframe_insert("location", frame=f)

r.resolution_x, r.resolution_y, r.fps = a.largura, a.altura, 24
t0 = time.time()

# --- 1) start frame em EEVEE (1 frame só: qualidade vale o custo) ---
r.engine = 'BLENDER_EEVEE'
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'
scn.frame_set(F0); r.filepath = os.path.join(a.out, "frame01")
bpy.ops.render.render(write_still=True)

# --- 2) driver.mp4 em Workbench (rápido: é referência de movimento, não de luz) ---
r.engine = 'BLENDER_WORKBENCH'
r.image_settings.media_type = 'VIDEO'; r.ffmpeg.format = 'MPEG4'; r.ffmpeg.codec = 'H264'
scn.frame_start, scn.frame_end = F0, F1
r.filepath = os.path.join(a.out, "driver")
bpy.ops.render.render(animation=True)

# Blender carimba o intervalo de frames no nome do vídeo (driver0001-0048.mp4).
# O Portão 2 entrega nome fixo, então renomeia.
import glob, shutil
alvo = os.path.join(a.out, "driver.mp4")
for f in glob.glob(os.path.join(a.out, "driver0*.mp4")):
    if os.path.abspath(f) != os.path.abspath(alvo):
        if os.path.exists(alvo): os.remove(alvo)
        shutil.move(f, alvo)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(a.out, "cena.blend"))

print("\n" + "=" * 60)
print(f"BLOCKOUT PRONTO em {time.time() - t0:.1f}s  ->  {a.out}")
print(f"  frame01.png   start frame ({a.largura}x{a.altura}, lente {a.lente}mm)")
print(f"  driver.mp4    {F1} frames = {F1/24:.1f}s de referência de movimento")
print(f"  cena.blend    criatura {a.criatura}m contra humano de 1,75m")
print("PORTAO 2: mostrar os dois ao Samuel e PARAR. Nao gerar sem a palavra dele.")
print("=" * 60)
