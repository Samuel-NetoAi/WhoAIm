# Cthulhu · Bloco 1 — o despertar do pesadelo e a passagem de navio
#
# ⚫ PORTÃO 1 aberto pelo Samuel em 2026-09-08 ("faça um teste no Blender agora").
# ⚫ PORTÃO 2 continua valendo: entregar frame01.png + driver.mp4 e PARAR.
#
# O QUE ESTE BLOCKOUT COBRE, E O QUE NÃO
#   Cobre a metade GEOMÉTRICA da cena: a cama, as três posições do Francis
#   (deitado -> torso erguido -> sentado na beirada) e o movimento que é o
#   ponto do bloco — a câmera larga o Francis e viaja até a passagem de navio.
#   Isso é o gatilho G4 (movimento que o texto descreve mal) somado a G1 (a
#   passagem é pequena e precisa de tamanho legível no quadro).
#
#   NÃO cobre os vislumbres do Cthulhu em névoa. Blockout não dá forma nem
#   silhueta — ver _registros\BLENDER.md §7. Aquilo é folha de personagem.
#
# MEDIDAS — tudo em METROS, escala real (é o que dá leitura de tamanho)
#   quarto 4,0 x 5,0 · pé-direito 2,8 · cama 1,0 x 2,0 x 0,55
#   Francis 1,75 · criado-mudo 0,45 x 0,40 x 0,65 · passagem 0,20 x 0,09
#
# O ALVO É QUE CONTA: um empty que começa na cabeça do Francis e termina na
# passagem. A câmera segue o alvo, então a TRANSFERÊNCIA DE ATENÇÃO é o
# movimento — não é corte, é a câmera mudando de assunto na frente do
# espectador. Era isso que o Samuel descreveu.

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
F_ACORDA, F_TORSO, F_SENTA, F_FIM = 1, 48, 108, 192      # 8 segundos

def cubo(nome, loc, esc, pai=None):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object; o.name = nome; o.scale = esc
    if pai: o.parent = pai
    return o

# ---------------------------------------------------------------- o quarto
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, 0))
ch = bpy.context.object; ch.name = "CHAO"; ch.scale = (4.0, 5.0, 1)
cubo("PAREDE_FUNDO",  (0.0,  2.5, 1.4), (4.0, 0.1, 2.8))
cubo("PAREDE_ESQ",   (-2.0,  0.0, 1.4), (0.1, 5.0, 2.8))

# ------------------------------------------------------- cama e criado-mudo
cubo("CAMA", (-1.20, -0.20, 0.275), (1.00, 2.00, 0.55))
MESA_X, MESA_Y, MESA_Z = -0.35, 0.75, 0.325
cubo("CRIADO_MUDO", (MESA_X, MESA_Y, MESA_Z), (0.45, 0.40, 0.65))

# A passagem: pequena de propósito. É ela que obriga a câmera a chegar perto,
# e é a chegada que revela o navio desenhado e as letras miúdas.
PASSAGEM = Vector((MESA_X, MESA_Y - 0.02, 0.655))
cubo("PASSAGEM_NAVIO", PASSAGEM, (0.20, 0.09, 0.002))

# ------------------------------------------------------------- o Francis
# Dois volumes com um empty no quadril: é o mínimo que mostra o tronco subindo
# sem virar exercício de modelagem. "Cubos bastam" — seis fontes concordam.
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(-1.20, -0.15, 0.62))
quadril = bpy.context.object; quadril.name = "QUADRIL"

torso = cubo("FRANCIS_TORSO", (0, 0, 0.45), (0.45, 0.26, 0.90), pai=quadril)
pernas = cubo("FRANCIS_PERNAS", (-1.20, -0.62, 0.68), (0.40, 0.95, 0.24))
cabeca = cubo("FRANCIS_CABECA", (0, 0, 1.02), (0.20, 0.24, 0.26), pai=quadril)

# O alvo VIVE na cabeca: ele acompanha o tronco subindo sem eu recalcular nada.
# Antes eu chutava a posicao da cabeca a cada keyframe — e errava.
bpy.ops.object.empty_add(type='PLAIN_AXES', radius=0.05, location=(0, 0, 1.02))
foco_cabeca = bpy.context.object; foco_cabeca.name = "FOCO_CABECA"
foco_cabeca.parent = quadril

# deitado (-88°) -> torso erguido (-30°) -> sentado (0°)
for f, ang in ((F_ACORDA, -1.535), (F_TORSO, -0.524), (F_SENTA, 0.0)):
    scn.frame_set(f)
    quadril.rotation_euler = (ang, 0, 0)
    quadril.keyframe_insert("rotation_euler", frame=f)

# as pernas saem da cama junto com o tronco: é o gesto que define "sentado"
for f, loc, rot in ((F_ACORDA, (-1.20, -0.62, 0.68), (0, 0, 0)),
                    (F_TORSO,  (-1.20, -0.62, 0.68), (0, 0, 0)),
                    (F_SENTA,  (-0.90, -0.30, 0.42), (0.9, 0, -0.6))):
    scn.frame_set(f)
    pernas.location, pernas.rotation_euler = loc, rot
    pernas.keyframe_insert("location", frame=f)
    pernas.keyframe_insert("rotation_euler", frame=f)

# --------------------------------------------------- valores (separacao)
def valor(nome, v):
    """Cinza proprio por objeto. Nao e textura — e leitura de volume."""
    m = bpy.data.materials.new(nome + "_M"); m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (v, v, v, 1)
    m.diffuse_color = (v, v, v, 1)          # Workbench le daqui
    o = bpy.data.objects[nome]
    o.data.materials.clear(); o.data.materials.append(m)

for nome, v in (("CHAO", 0.22), ("PAREDE_FUNDO", 0.34), ("PAREDE_ESQ", 0.34),
                ("CAMA", 0.52), ("CRIADO_MUDO", 0.42),
                ("FRANCIS_TORSO", 0.82), ("FRANCIS_PERNAS", 0.78),
                ("FRANCIS_CABECA", 0.92),
                ("PASSAGEM_NAVIO", 0.97)):   # a passagem e o ponto mais claro do plano
    valor(nome, v)

# ------------------------------------------------------------------- luz
# Luz de LEITURA, nao de clima. O blockout existe para o modelo entender
# geometria; escuro aqui vira ambiguidade la. O luar entra na geracao.
bpy.ops.object.light_add(type='SUN', location=(2.0, -1.0, 2.6))
sol = bpy.context.object
sol.rotation_euler, sol.data.energy = (0.75, 0.25, -0.9), 3.5

w = bpy.data.worlds.new("W"); scn.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.30, 0.32, 0.36, 1)

# ------------------------------------------------ o ALVO e a câmera
# O alvo é o assunto do plano. Ele começa na cabeça do Francis e termina na
# passagem: a câmera "troca de assunto" sem corte.
bpy.ops.object.empty_add(type='SPHERE', radius=0.08, location=(-1.20, 0.55, 0.95))
alvo = bpy.context.object; alvo.name = "ALVO"
copia = alvo.constraints.new(type='COPY_LOCATION')
copia.target = foco_cabeca
for f, inf in ((F_ACORDA, 1.0), (F_SENTA, 1.0), (F_FIM, 0.0)):
    scn.frame_set(f); copia.influence = inf
    copia.keyframe_insert("influence", frame=f)
alvo.location = PASSAGEM        # para onde ele vai quando solta a cabeça

cd = bpy.data.cameras.new("CAM"); cd.lens = a.lente
cam = bpy.data.objects.new("CAM", cd); scn.collection.objects.link(cam); scn.camera = cam
t = cam.constraints.new(type='TRACK_TO'); t.target = alvo
t.track_axis, t.up_axis = 'TRACK_NEGATIVE_Z', 'UP_Y'

for f, loc in ((F_ACORDA, ( 0.55,  0.25, 1.35)),    # ~1,9 m — plano médio, leve plongée
               (F_TORSO,  ( 0.70, -0.40, 1.60)),    # recua e sobe quando o tronco levanta
               (F_SENTA,  ( 1.70, -1.60, 1.15)),    # ~3,2 m. A 35 mm e 2,1 m o campo vertical
                                                    # ia de z~0,8 a ~2,0 e a cama (z 0,55)
                                                    # ficava FORA — ele flutuava na parede.
                                                    # Recuar foi o unico jeito de caber cama,
                                                    # chao e figura no mesmo quadro.
               (F_FIM,    ( 0.15,  0.45, 0.88))):   # ~0,6 m da passagem: ela toma 1/3 do quadro
    scn.frame_set(f); cam.location = loc; cam.keyframe_insert("location", frame=f)

scn.frame_start, scn.frame_end = F_ACORDA, F_FIM
r.resolution_x, r.resolution_y, r.fps = 854, 480, FPS
t0 = time.time()

# start frame em EEVEE (1 quadro, vale a luz) — driver em Workbench (rápido)
r.engine = 'BLENDER_EEVEE'
r.image_settings.media_type = 'IMAGE'; r.image_settings.file_format = 'PNG'
for f, nome in ((F_ACORDA, "frame01_acorda"), (F_SENTA, "frame02_sentado"),
                (F_FIM, "frame03_passagem")):
    scn.frame_set(f); r.filepath = os.path.join(a.out, nome)
    bpy.ops.render.render(write_still=True)

r.engine = 'BLENDER_WORKBENCH'
scn.display.shading.color_type = 'MATERIAL'    # sem isto o driver sai chapado
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
print(f"BLOCO 1 PRONTO em {time.time()-t0:.1f}s -> {a.out}")
print(f"  {(F_FIM-F_ACORDA)/FPS:.1f}s · lente {a.lente}mm · 854x480")
print("  frame01_acorda · frame02_sentado · frame03_passagem · driver.mp4")
print("PORTAO 2: mostrar ao Samuel e PARAR.")
print("=" * 62)
