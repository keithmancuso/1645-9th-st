"""Build and render a 3D model of 1645 9th St as proposed (kitchen swapped to the rear-left, opening onto the deck).
Run:  /Applications/Blender.app/Contents/MacOS/Blender -b -P render/scene.py -- [view ...] [--samples N] [--scale S]
Plan coordinates are in feet, matching floor-plan/generate.py (x 0..26 west->east, y 0 rear .. 30 front).
World: X = x ft, Y = -y ft (street at -Y), Z up, in meters."""
import bpy, bmesh, math, sys, os
from mathutils import Vector

F = 0.3048
Z0 = 2.0            # finished floor above grade, ft
CEIL = Z0 + 9.0     # ceiling, ft
ROOT = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAMPLES = 256; SCALE = 100
views = []
i = 0
while i < len(argv):
    if argv[i] == '--samples': SAMPLES = int(argv[i+1]); i += 2
    elif argv[i] == '--scale': SCALE = int(argv[i+1]); i += 2
    else: views.append(argv[i]); i += 1

# ---------------------------------------------------------------- scene reset
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
COLL = {}
def coll(name):
    if name not in COLL:
        c = bpy.data.collections.new(name); scene.collection.children.link(c); COLL[name] = c
    return COLL[name]

# ---------------------------------------------------------------- materials
MATS = {}
def mat(name, color=(0.8,0.8,0.8), rough=0.5, metallic=0.0, spec=0.5, emit=None, glass=False, nodes_fn=None):
    if name in MATS: return MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = spec
    if emit:
        bsdf.inputs['Emission Color'].default_value = (*emit[0], 1); bsdf.inputs['Emission Strength'].default_value = emit[1]
    if glass:
        bsdf.inputs['Transmission Weight'].default_value = 1.0; bsdf.inputs['Roughness'].default_value = 0.0
        bsdf.inputs['IOR'].default_value = 1.5
        out = nt.nodes['Material Output']; lp = nt.nodes.new('ShaderNodeLightPath'); tr = nt.nodes.new('ShaderNodeBsdfTransparent')
        mx = nt.nodes.new('ShaderNodeMixShader')
        nt.links.new(lp.outputs['Is Camera Ray'], mx.inputs['Fac']); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(bsdf.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs['Surface'])
    if nodes_fn: nodes_fn(nt, bsdf)
    MATS[name] = m; return m

def tex_coord(nt):
    tc = nt.nodes.new('ShaderNodeTexCoord'); return tc

def wood_floor(nt, bsdf):
    tc = tex_coord(nt)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1, 1, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1.0
    br.inputs['Mortar Size'].default_value = 0.004; br.inputs['Mortar Smooth'].default_value = 0.2
    br.inputs['Bias'].default_value = 0.0; br.inputs['Brick Width'].default_value = 1.2; br.inputs['Row Height'].default_value = 0.09
    br.offset = 0.5; br.offset_frequency = 2; br.squash = 1.0
    br.inputs['Color1'].default_value = (0.62, 0.38, 0.19, 1); br.inputs['Color2'].default_value = (0.50, 0.29, 0.13, 1)
    br.inputs['Mortar'].default_value = (0.25, 0.14, 0.06, 1)
    nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    # grain
    mp2 = nt.nodes.new('ShaderNodeMapping'); mp2.inputs['Scale'].default_value = (1, 40, 1)
    nt.links.new(tc.outputs['Object'], mp2.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 8
    nt.links.new(mp2.outputs['Vector'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].position = 0.35; ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[0].color = (0.75, 0.55, 0.35, 1); ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'; mix.inputs['Factor'].default_value = 0.6
    nt.links.new(br.outputs['Color'], mix.inputs[6]); nt.links.new(ramp.outputs['Color'], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.15
    nt.links.new(br.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.28
    if 'Coat Weight' in bsdf.inputs: bsdf.inputs['Coat Weight'].default_value = 0.3

def siding(nt, bsdf):
    tc = tex_coord(nt)
    wave = nt.nodes.new('ShaderNodeTexWave'); wave.wave_type = 'BANDS'; wave.bands_direction = 'Z'; wave.wave_profile = 'SAW'
    wave.inputs['Scale'].default_value = 1/(0.15); wave.inputs['Distortion'].default_value = 0.0
    nt.links.new(tc.outputs['Object'], wave.inputs['Vector'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.9; bump.inputs['Distance'].default_value = 0.03
    nt.links.new(wave.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 30; nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs['Factor'].default_value=0.12
    mix.inputs[6].default_value = (*SIDING_COLOR, 1)
    nt.links.new(nz.outputs['Color'], mix.inputs[7]); nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])

def shingles(nt, bsdf):
    tc = tex_coord(nt)
    br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = 1
    br.inputs['Brick Width'].default_value = 0.9; br.inputs['Row Height'].default_value = 0.16; br.inputs['Mortar Size'].default_value = 0.01
    br.inputs['Color1'].default_value = (0.09,0.09,0.09,1); br.inputs['Color2'].default_value = (0.12,0.12,0.12,1); br.inputs['Mortar'].default_value=(0.04,0.04,0.04,1)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (math.radians(90),0,0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 80; nz.inputs['Detail'].default_value = 6
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; mix.blend_type='MULTIPLY'; mix.inputs['Factor'].default_value=0.5
    nt.links.new(br.outputs['Color'], mix.inputs[6]); nt.links.new(nz.outputs['Color'], mix.inputs[7]); nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.6; bump.inputs['Distance'].default_value = 0.01
    nt.links.new(nz.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.9

def brick(nt, bsdf, c1=(0.45,0.18,0.12), c2=(0.38,0.15,0.10), mortar=(0.6,0.58,0.55), scale=1.0):
    tc = tex_coord(nt)
    br = nt.nodes.new('ShaderNodeTexBrick'); br.inputs['Scale'].default_value = scale
    br.inputs['Brick Width'].default_value = 0.2; br.inputs['Row Height'].default_value = 0.065; br.inputs['Mortar Size'].default_value = 0.008
    br.inputs['Color1'].default_value = (*c1,1); br.inputs['Color2'].default_value = (*c2,1); br.inputs['Mortar'].default_value=(*mortar,1)
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Rotation'].default_value = (math.radians(90),0,0)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], br.inputs['Vector'])
    nt.links.new(br.outputs['Color'], bsdf.inputs['Base Color'])
    bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.4
    nt.links.new(br.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.85

def subway(nt, bsdf):
    brick(nt, bsdf, c1=(0.93,0.93,0.91), c2=(0.90,0.90,0.88), mortar=(0.70,0.70,0.68))
    bsdf.inputs['Roughness'].default_value = 0.12
    if 'Coat Weight' in bsdf.inputs: bsdf.inputs['Coat Weight'].default_value = 0.5

def ground_noise(nt, bsdf, c1, c2, scale=20, bump=0.3):
    tc = tex_coord(nt)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 10; nz.inputs['Roughness'].default_value = 0.7
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (*c1,1); ramp.color_ramp.elements[1].color = (*c2,1)
    ramp.color_ramp.elements[0].position = 0.3; ramp.color_ramp.elements[1].position = 0.7
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    b = nt.nodes.new('ShaderNodeBump'); b.inputs['Strength'].default_value = bump
    nt.links.new(nz.outputs['Fac'], b.inputs['Height']); nt.links.new(b.outputs['Normal'], bsdf.inputs['Normal'])
    bsdf.inputs['Roughness'].default_value = 0.95

def quartz(nt, bsdf):
    tc = tex_coord(nt)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3; nz.inputs['Detail'].default_value = 12; nz.inputs['Roughness'].default_value = 0.8
    nt.links.new(tc.outputs['Object'], nz.inputs['Vector'])
    ramp = nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color = (0.80,0.80,0.78,1); ramp.color_ramp.elements[1].color = (0.96,0.96,0.95,1)
    ramp.color_ramp.elements[0].position = 0.4; ramp.color_ramp.elements[1].position = 0.6
    nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = 0.15
    if 'Coat Weight' in bsdf.inputs: bsdf.inputs['Coat Weight'].default_value = 0.6

SIDING_COLOR = (0.42, 0.50, 0.40)   # sage green (Valley St)
M = dict(
    siding   = mat('siding', SIDING_COLOR, 0.6, nodes_fn=siding),
    trim     = mat('trim', (0.92,0.92,0.88), 0.35),
    plaster  = mat('plaster', (0.90,0.89,0.85), 0.7),
    wainscot = mat('wainscot', (0.93,0.93,0.90), 0.35),
    accent   = mat('accent', (0.30,0.33,0.32), 0.7),     # deep gray-green walls above wainscot
    ceiling  = mat('ceiling', (0.96,0.96,0.95), 0.8),
    floor    = mat('floor', (0.6,0.4,0.2), 0.3, nodes_fn=wood_floor),
    roof     = mat('roof', (0.1,0.1,0.1), 0.9, nodes_fn=shingles),
    brick    = mat('brick', (0.45,0.18,0.12), 0.85, nodes_fn=brick),
    glass    = mat('glass', (1,1,1), 0.0, glass=True),
    door     = mat('door', (0.10,0.14,0.22), 0.3),       # navy
    deck     = mat('deck', (0.45,0.30,0.17), 0.7),
    concrete = mat('concrete', (0.62,0.61,0.58), 0.9, nodes_fn=lambda nt,b: ground_noise(nt,b,(0.55,0.54,0.52),(0.68,0.67,0.64),scale=8,bump=0.1)),
    asphalt  = mat('asphalt', (0.2,0.2,0.2), 0.95, nodes_fn=lambda nt,b: ground_noise(nt,b,(0.16,0.16,0.16),(0.24,0.24,0.24),scale=40,bump=0.2)),
    lawn     = mat('lawn', (0.2,0.35,0.12), 0.95, nodes_fn=lambda nt,b: ground_noise(nt,b,(0.16,0.30,0.08),(0.32,0.45,0.15),scale=60,bump=0.6)),
    mulch    = mat('mulch', (0.25,0.17,0.10), 0.95, nodes_fn=lambda nt,b: ground_noise(nt,b,(0.18,0.12,0.07),(0.35,0.25,0.15),scale=120,bump=0.8)),
    gravel   = mat('gravel', (0.6,0.58,0.52), 0.95, nodes_fn=lambda nt,b: ground_noise(nt,b,(0.45,0.43,0.38),(0.72,0.70,0.64),scale=200,bump=0.8)),
    fence    = mat('fence', (0.40,0.30,0.20), 0.8),
    leaf     = mat('leaf', (0.12,0.28,0.08), 0.8),
    leaf2    = mat('leaf2', (0.20,0.36,0.12), 0.8),
    bark     = mat('bark', (0.25,0.18,0.12), 0.9),
    neighbor1= mat('neighbor1', (0.55,0.62,0.72), 0.7),
    neighbor2= mat('neighbor2', (0.85,0.82,0.72), 0.7),
    cabinet  = mat('cabinet', (0.42,0.22,0.12), 0.35),    # warm cherry-ish wood
    cabinet2 = mat('cabinet2', (0.93,0.93,0.90), 0.3),    # white uppers
    quartz   = mat('quartz', (0.9,0.9,0.88), 0.15, nodes_fn=quartz),
    tile     = mat('tile', (0.93,0.93,0.91), 0.12, nodes_fn=subway),
    black    = mat('black', (0.02,0.02,0.02), 0.35, metallic=0.8),
    steel    = mat('steel', (0.7,0.7,0.7), 0.25, metallic=1.0),
    fabric   = mat('fabric', (0.55,0.30,0.16), 0.9),     # cognac leather sofa
    fabric2  = mat('fabric2', (0.85,0.82,0.75), 0.95),   # linen
    rug      = mat('rug', (0.78,0.74,0.66), 1.0),
    walnut   = mat('walnut', (0.28,0.17,0.10), 0.4),
    bulb     = mat('bulb', (1,0.9,0.7), 0.5, emit=((1.0,0.85,0.6), 25)),
    shade    = mat('shade', (0.05,0.05,0.05), 0.5),
    plant    = mat('plant', (0.15,0.35,0.12), 0.7),
    pot      = mat('pot', (0.85,0.83,0.78), 0.6),
    art      = mat('art', (0.2,0.22,0.25), 0.6),
    bedding  = mat('bedding', (0.92,0.92,0.90), 0.95),
)

# ---------------------------------------------------------------- geometry helpers
def add_mesh(name, verts, faces, m, cname='House', bevel=None, smooth=False):
    me = bpy.data.meshes.new(name); me.from_pydata(verts, [], faces); me.update()
    ob = bpy.data.objects.new(name, me); coll(cname).objects.link(ob)
    if m: ob.data.materials.append(m)
    if bevel:
        b = ob.modifiers.new('bevel', 'BEVEL'); b.width = bevel; b.segments = 3
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return ob

def box(name, x1, y1, x2, y2, z1, z2, m, cname='House', bevel=None):
    """Axis-aligned box in plan feet (x,y) and feet (z)."""
    X1, X2 = min(x1,x2)*F, max(x1,x2)*F; Y1, Y2 = -max(y1,y2)*F, -min(y1,y2)*F; Z1, Z2 = z1*F, z2*F
    v = [(X1,Y1,Z1),(X2,Y1,Z1),(X2,Y2,Z1),(X1,Y2,Z1),(X1,Y1,Z2),(X2,Y1,Z2),(X2,Y2,Z2),(X1,Y2,Z2)]
    f = [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    return add_mesh(name, v, f, m, cname, bevel)

def wall(name, x1, y1, x2, y2, t, z1, z2, m, openings=(), side=0, cname='House'):
    """Wall along a plan line, thickness t (ft) offset to `side` (-1/0/+1 of the line normal). openings: (a, b, sill, head) in ft along the axis."""
    horiz = (y1 == y2)
    a0, a1 = (min(x1,x2), max(x1,x2)) if horiz else (min(y1,y2), max(y1,y2))
    c = y1 if horiz else x1
    lo, hi = (c - t/2, c + t/2) if side == 0 else ((c, c + t) if side > 0 else (c - t, c))
    def seg(a, b, za, zb, k):
        if b - a <= 1e-6 or zb - za <= 1e-6: return
        if horiz: box(f'{name}.{k}', a, lo, b, hi, za, zb, m, cname)
        else: box(f'{name}.{k}', lo, a, hi, b, za, zb, m, cname)
    cur = a0; k = 0
    for (oa, ob_, sill, head) in sorted(openings):
        seg(cur, oa, z1, z2, k); k += 1
        seg(oa, ob_, z1, z1 + sill, k); k += 1
        seg(oa, ob_, z1 + head, z2, k); k += 1
        cur = ob_
    seg(cur, a1, z1, z2, k)

def ext_wall(name, x1, y1, x2, y2, out, openings=(), z1=0.0, z2=CEIL):
    """Exterior wall: plaster inside the line, siding skin outside. out = +1 if exterior is +x/+y (plan) else -1."""
    ops = [(a, b, Z0 + sill - z1, Z0 + head - z1) for (a, b, sill, head) in openings]
    wall(name+'.in', x1, y1, x2, y2, 0.5, z1, z2, M['plaster'], ops, side=-out)
    ops2 = [(a, b, Z0 + sill + 0.5, Z0 + head + 0.5) for (a, b, sill, head) in openings]
    wall(name+'.out', x1, y1, x2, y2, 0.25, -0.5, z2 + 0.5, M['siding'], ops2, side=out)

def window(name, x1, y1, x2, y2, sill, head, out, muntins=True, cname='House'):
    """Double-hung window in an exterior wall on the plan line (x1,y1)-(x2,y2)."""
    horiz = (y1 == y2); c = y1 if horiz else x1
    a0, a1 = (min(x1,x2), max(x1,x2)) if horiz else (min(y1,y2), max(y1,y2))
    zs, zh = Z0 + sill, Z0 + head
    tw, td = 0.35, 0.12   # trim width / projection
    def B(n, a, b, d1, d2, za, zb, m):
        if horiz: box(n, a, c + d1, b, c + d2, za, zb, m, cname)
        else: box(n, c + d1, a, c + d2, b, za, zb, m, cname)
    o1, o2 = (0.25, 0.25 + td) if out > 0 else (-0.25 - td, -0.25)
    # exterior casing
    B(name+'.ct', a0 - tw, a1 + tw, o1, o2, zh, zh + tw, M['trim']); B(name+'.cb', a0 - tw, a1 + tw, o1, o2, zs - tw*1.5, zs, M['trim'])
    B(name+'.cl', a0 - tw, a0, o1, o2, zs, zh, M['trim']); B(name+'.cr', a1, a1 + tw, o1, o2, zs, zh, M['trim'])
    # jamb liner (fills the wall thickness)
    B(name+'.jl', a0, a0 + 0.08, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jr', a1 - 0.08, a1, -0.5, 0.25, zs, zh, M['trim'])
    B(name+'.jt', a0, a1, -0.5, 0.25, zh - 0.08, zh, M['trim']); B(name+'.js', a0, a1, -0.5, 0.25, zs, zs + 0.08, M['trim'])
    # interior stool + casing
    i1, i2 = (-0.5 - td, -0.5) if out > 0 else (0.5, 0.5 + td)
    B(name+'.stool', a0 - tw, a1 + tw, i1 - 0.1, i2, zs - 0.08, zs + 0.06, M['trim'])
    B(name+'.icl', a0 - tw, a0, i1, i2, zs, zh + tw, M['trim']); B(name+'.icr', a1, a1 + tw, i1, i2, zs, zh + tw, M['trim'])
    B(name+'.ict', a0 - tw, a1 + tw, i1, i2, zh, zh + tw, M['trim'])
    # sash frames + glass
    mid = (zs + zh) / 2; s = 0.15
    for tag, za, zb, d in (('lo', zs, mid, -0.05), ('up', mid, zh, 0.05)):
        B(f'{name}.{tag}.l', a0, a0 + s, d - 0.06, d + 0.06, za, zb, M['trim']); B(f'{name}.{tag}.r', a1 - s, a1, d - 0.06, d + 0.06, za, zb, M['trim'])
        B(f'{name}.{tag}.b', a0, a1, d - 0.06, d + 0.06, za, za + s, M['trim']); B(f'{name}.{tag}.t', a0, a1, d - 0.06, d + 0.06, zb - s, zb, M['trim'])
        B(f'{name}.{tag}.g', a0 + s, a1 - s, d - 0.01, d + 0.01, za + s, zb - s, M['glass'])
        if muntins and tag == 'up':
            n = 2 if (a1 - a0) < 4 else 3
            for k in range(1, n):
                p = a0 + (a1 - a0) * k / n
                B(f'{name}.{tag}.m{k}', p - 0.04, p + 0.04, d - 0.05, d + 0.05, za, zb, M['trim'])

def french_door(name, x1, y1, x2, y2, out, head=7.0, cname='House'):
    horiz = (y1 == y2); c = y1 if horiz else x1
    a0, a1 = (min(x1,x2), max(x1,x2)) if horiz else (min(y1,y2), max(y1,y2))
    zs, zh = Z0, Z0 + head; tw = 0.35; td = 0.12
    def B(n, a, b, d1, d2, za, zb, m):
        if horiz: box(n, a, c + d1, b, c + d2, za, zb, m, cname)
        else: box(n, c + d1, a, c + d2, b, za, zb, m, cname)
    o1, o2 = (0.25, 0.25 + td) if out > 0 else (-0.25 - td, -0.25)
    B(name+'.ct', a0 - tw, a1 + tw, o1, o2, zh, zh + tw, M['trim']); B(name+'.cl', a0 - tw, a0, o1, o2, zs, zh, M['trim']); B(name+'.cr', a1, a1 + tw, o1, o2, zs, zh, M['trim'])
    B(name+'.jl', a0, a0 + 0.08, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jr', a1 - 0.08, a1, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jt', a0, a1, -0.5, 0.25, zh - 0.08, zh, M['trim'])
    B(name+'.sill', a0, a1, -0.5, 0.4, zs - 0.1, zs + 0.05, M['trim'])
    mid = (a0 + a1) / 2; s = 0.35
    for tag, p0, p1 in (('l', a0, mid), ('r', mid, a1)):
        for nm, a, b, za, zb in ((f'{tag}.a', p0, p0 + s, zs, zh), (f'{tag}.b', p1 - s, p1, zs, zh), (f'{tag}.c', p0, p1, zs, zs + 0.8), (f'{tag}.d', p0, p1, zh - s, zh)):
            B(f'{name}.{nm}', a, b, -0.08, 0.08, za, zb, M['trim'])
        B(f'{name}.{tag}.g', p0 + s, p1 - s, -0.01, 0.01, zs + 0.8, zh - s, M['glass'])
        for k in range(1, 4):
            z = zs + 0.8 + (zh - s - zs - 0.8) * k / 4
            B(f'{name}.{tag}.m{k}', p0 + s, p1 - s, -0.06, 0.06, z - 0.04, z + 0.04, M['trim'])
        B(f'{name}.{tag}.mv', (p0 + p1)/2 - 0.04, (p0 + p1)/2 + 0.04, -0.06, 0.06, zs + 0.8, zh - s, M['trim'])
    B(name+'.handle', mid - 0.35, mid - 0.25, -0.5, 0.35, zs + 3.0, zs + 3.1, M['black']); B(name+'.handle2', mid + 0.25, mid + 0.35, -0.5, 0.35, zs + 3.0, zs + 3.1, M['black'])

def slider_door(name, x1, y1, x2, y2, out, head=6.8, cname='House'):
    """Existing wood-framed sliding glass door: two full-glass panels on offset tracks, no muntins."""
    horiz = (y1 == y2); c = y1 if horiz else x1
    a0, a1 = (min(x1,x2), max(x1,x2)) if horiz else (min(y1,y2), max(y1,y2))
    zs, zh = Z0, Z0 + head; tw = 0.35; td = 0.12; wm = M['walnut']
    def B(n, a, b, d1, d2, za, zb, m):
        if horiz: box(n, a, c + d1, b, c + d2, za, zb, m, cname)
        else: box(n, c + d1, a, c + d2, b, za, zb, m, cname)
    o1, o2 = (0.25, 0.25 + td) if out > 0 else (-0.25 - td, -0.25)
    B(name+'.ct', a0 - tw, a1 + tw, o1, o2, zh, zh + tw, M['trim']); B(name+'.cl', a0 - tw, a0, o1, o2, zs, zh, M['trim']); B(name+'.cr', a1, a1 + tw, o1, o2, zs, zh, M['trim'])
    B(name+'.jl', a0, a0 + 0.08, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jr', a1 - 0.08, a1, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jt', a0, a1, -0.5, 0.25, zh - 0.08, zh, M['trim'])
    B(name+'.sill', a0, a1, -0.5, 0.4, zs - 0.1, zs + 0.1, M['trim'])
    mid = (a0 + a1) / 2; st = 0.3
    for tag, p0, p1, d in (('fix', a0, mid + 0.05, 0.06), ('sl', mid - 0.05, a1, -0.08)):
        for nm, a, b, za, zb in ((f'{tag}.a', p0, p0 + st, zs, zh), (f'{tag}.b', p1 - st, p1, zs, zh), (f'{tag}.c', p0, p1, zs, zs + 0.5), (f'{tag}.d', p0, p1, zh - st, zh)):
            B(f'{name}.{nm}', a, b, d - 0.07, d + 0.07, za, zb, wm)
        B(f'{name}.{tag}.g', p0 + st, p1 - st, d - 0.01, d + 0.01, zs + 0.5, zh - st, M['glass'])
    B(name+'.handle', mid - 0.05 + st - 0.05, mid - 0.05 + st + 0.12, -0.2, -0.05, zs + 2.9, zs + 3.6, M['black'])

def door_slab(name, x1, y1, x2, y2, out, head=6.8, m=None, glass_lite=True, cname='House'):
    horiz = (y1 == y2); c = y1 if horiz else x1
    a0, a1 = (min(x1,x2), max(x1,x2)) if horiz else (min(y1,y2), max(y1,y2))
    zs, zh = Z0, Z0 + head; tw = 0.35; td = 0.12; m = m or M['door']
    def B(n, a, b, d1, d2, za, zb, mm):
        if horiz: box(n, a, c + d1, b, c + d2, za, zb, mm, cname)
        else: box(n, c + d1, a, c + d2, b, za, zb, mm, cname)
    o1, o2 = (0.25, 0.25 + td) if out > 0 else (-0.25 - td, -0.25)
    B(name+'.ct', a0 - tw, a1 + tw, o1, o2, zh, zh + tw, M['trim']); B(name+'.cl', a0 - tw, a0, o1, o2, zs, zh, M['trim']); B(name+'.cr', a1, a1 + tw, o1, o2, zs, zh, M['trim'])
    B(name+'.jl', a0, a0 + 0.08, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jr', a1 - 0.08, a1, -0.5, 0.25, zs, zh, M['trim']); B(name+'.jt', a0, a1, -0.5, 0.25, zh - 0.08, zh, M['trim'])
    B(name+'.slab', a0 + 0.08, a1 - 0.08, -0.08, 0.08, zs, zh - 0.08, m)
    if glass_lite:
        B(name+'.lite', a0 + 0.6, a1 - 0.6, -0.09, 0.09, zs + 4.2, zh - 0.7, M['glass'])
    hx = a1 - 0.5
    B(name+'.knob', hx - 0.12, hx + 0.12, -0.2, 0.2, zs + 3.0, zs + 3.15, M['black'])

def hip_roof(name, x1, y1, x2, y2, eave_z, pitch=5/12, overhang=1.5, thick=0.5, cname='Roof', fascia=True, skip=''):
    """Hip roof over plan rectangle; ridge along the long axis. skip: sides (W/E/S/N, S = low plan y) that butt
    into another wall: no overhang, fascia or soffit there."""
    ov = {k: (0.2 if k in skip else overhang) for k in 'WESN'}
    x1, x2, y1, y2 = min(x1,x2), max(x1,x2), min(y1,y2), max(y1,y2)
    X1, X2 = x1 - ov['W'], x2 + ov['E']; Y1, Y2 = y1 - ov['S'], y2 + ov['N']
    w, d = X2 - X1, Y2 - Y1
    if d >= w:
        half = w / 2; rz = eave_z + pitch * half
        cx = (X1 + X2) / 2
        r1, r2 = (cx, Y1 + half, rz), (cx, Y2 - half, rz)
    else:
        half = d / 2; rz = eave_z + pitch * half
        cy = (Y1 + Y2) / 2
        r1, r2 = (X1 + half, cy, rz), (X2 - half, cy, rz)
    P = lambda x, y, z: (x * F, -y * F, z * F)
    v = [P(X1, Y1, eave_z), P(X2, Y1, eave_z), P(X2, Y2, eave_z), P(X1, Y2, eave_z), P(*r1), P(*r2)]
    if d >= w: f = [(0, 1, 4), (1, 2, 5, 4), (2, 3, 5), (3, 0, 4, 5)]
    else:      f = [(0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)]
    ob = add_mesh(name, v, f, M['roof'], cname)
    s = ob.modifiers.new('solid', 'SOLIDIFY'); s.thickness = thick * F; s.offset = 1.0
    if fascia:
        fz = eave_z - 0.6
        if 'S' not in skip: box(name+'.fs', X1, Y1, X2, Y1 + 0.15, fz, eave_z + 0.05, M['trim'], cname)
        if 'N' not in skip: box(name+'.fn', X1, Y2 - 0.15, X2, Y2, fz, eave_z + 0.05, M['trim'], cname)
        if 'W' not in skip: box(name+'.fw', X1, Y1, X1 + 0.15, Y2, fz, eave_z + 0.05, M['trim'], cname)
        if 'E' not in skip: box(name+'.fe', X2 - 0.15, Y1, X2, Y2, fz, eave_z + 0.05, M['trim'], cname)
        # soffit is a ring outside the wall line only -- a full slab here sits coplanar with the ceiling and
        # swallows every light ray leaving it (ceiling renders black)
        if 'S' not in skip: box(name+'.sof_s', X1, Y1, X2, y1, fz - 0.1, fz, M['trim'], cname)
        if 'N' not in skip: box(name+'.sof_n', X1, y2, X2, Y2, fz - 0.1, fz, M['trim'], cname)
        if 'W' not in skip: box(name+'.sof_w', X1, y1, x1, y2, fz - 0.1, fz, M['trim'], cname)
        if 'E' not in skip: box(name+'.sof_e', x2, y1, X2, y2, fz - 0.1, fz, M['trim'], cname)
    return ob

def shed_roof(name, x1, y1, x2, y2, z_high, z_low, high_side='y+', overhang=1.0, cname='Roof'):
    X1, X2 = min(x1,x2) - overhang, max(x1,x2) + overhang; Y1, Y2 = min(y1,y2) - overhang, max(y1,y2) + overhang
    if high_side == 'y+': Y2 = max(y1,y2) + 0.2   # high edge dies into the main wall
    else: Y1 = min(y1,y2) - 0.2
    P = lambda x, y, z: (x * F, -y * F, z * F)
    if high_side == 'y+': v = [P(X1,Y1,z_low), P(X2,Y1,z_low), P(X2,Y2,z_high), P(X1,Y2,z_high)]
    else: v = [P(X1,Y1,z_high), P(X2,Y1,z_high), P(X2,Y2,z_low), P(X1,Y2,z_low)]
    ob = add_mesh(name, v, [(0,1,2,3)], M['roof'], cname)
    s = ob.modifiers.new('solid', 'SOLIDIFY'); s.thickness = 0.5 * F; s.offset = 1.0
    box(name+'.f', X1, Y1, X2, Y1 + 0.15, z_low - 0.6, z_low + 0.05, M['trim'], cname)
    return ob

def cyl(name, x, y, z1, z2, r, m, cname='House', verts=24):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r * F, depth=(z2 - z1) * F, location=(x * F, -y * F, (z1 + z2) / 2 * F))
    ob = bpy.context.object; ob.name = name; ob.data.materials.append(m)
    for c in ob.users_collection: c.objects.unlink(ob)
    coll(cname).objects.link(ob)
    for p in ob.data.polygons: p.use_smooth = True
    return ob

def sphere(name, x, y, z, r, m, cname='Yard', scale=(1,1,1)):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3, radius=r * F, location=(x * F, -y * F, z * F))
    ob = bpy.context.object; ob.name = name; ob.data.materials.append(m); ob.scale = scale
    for c in ob.users_collection: c.objects.unlink(ob)
    coll(cname).objects.link(ob)
    d = ob.modifiers.new('disp', 'DISPLACE'); t = bpy.data.textures.new(name+'.t', 'CLOUDS'); t.noise_scale = 0.6; d.texture = t; d.strength = 0.5 * r * F
    for p in ob.data.polygons: p.use_smooth = True
    return ob

import random
def tree(name, x, y, h=25, r=9, cname='Yard', m=None):
    rnd = random.Random(hash(name) & 0xffff)
    cyl(name+'.trunk', x, y, 0, h * 0.6, 0.7, M['bark'], cname)
    for k in range(3):
        a = rnd.uniform(0, 6.28); cyl(f'{name}.br{k}', x + math.cos(a) * r * 0.25, y + math.sin(a) * r * 0.25, h * 0.45, h * 0.7, 0.3, M['bark'], cname)
    for k in range(14):
        a = rnd.uniform(0, 6.28); d = rnd.uniform(0, r * 0.75); zz = h * rnd.uniform(0.55, 0.95); rr = r * rnd.uniform(0.3, 0.55)
        sphere(f'{name}.c{k}', x + math.cos(a) * d, y + math.sin(a) * d, zz, rr, (m or M['leaf']) if k % 2 else M['leaf2'], cname, scale=(1, 1, rnd.uniform(0.6, 0.9)))

def shrub(name, x, y, r=1.5, cname='Yard'):
    sphere(name, x, y, r * 0.7, r, M['plant'], cname, scale=(1, 1, 0.8))

# ---------------------------------------------------------------- site
G = 'Yard'
box('ground', -60, -60, 90, 80, -1, 0, M['lawn'], G)
FY = 47   # front lot line / back of sidewalk
box('street', -60, FY + 5, 90, 80, -0.1, 0.02, M['asphalt'], G)
box('curb', -60, FY + 4.4, 90, FY + 5, -0.1, 0.5, M['concrete'], G)
box('sidewalk', -60, FY, 90, FY + 4.4, 0, 0.45, M['concrete'], G)
box('parkstrip', -60, FY - 1.5, 90, FY, 0, 0.35, M['lawn'], G)
# lot: 2,613 sq ft ~ 30 x 87 -> plan x -2..28, y -25..47 (front setback ~17 ft from sidewalk to porch)
# driveway: concrete apron off the street, parking pad on the east half of the front yard (in front of the porch), continuing as a strip down the east side to the back-yard gate
box('drive', 12.5, 30, 28, FY, 0, 0.42, M['concrete'], G)
box('drive_apron', 15, FY, 28, FY + 5, -0.05, 0.35, M['concrete'], G)      # curb cut through the park strip + sidewalk
box('drive_side', 26.25, 0, 28, 30, 0, 0.4, M['concrete'], G)
for k, y in enumerate((34, 38.5, 43)):   # control joints
    box(f'drive_j{k}', 12.5, y, 28, y + 0.08, 0.42, 0.44, M['asphalt'], G)
box('drive_jx', 20.2, 30, 20.28, FY, 0.42, 0.44, M['asphalt'], G)
box('frontbed', -2, 30, 12.5, FY, 0, 0.4, M['mulch'], G)         # planted front garden
cyl('treewell', 4.0, 42.5, 0.3, 0.42, 3.0, M['gravel'], G, verts=40)  # existing gravel circle
box('sidebed_w', -2, -25, 0, 30, 0, 0.3, M['gravel'], G)
box('sidebed_e', 26, -25, 28, 0, 0, 0.3, M['gravel'], G)
# EV charger: wall-mounted Level 2 unit on the east side of the porch, facing the pad, with a coiled cable and a holster
box('evse', 26.05, 31.3, 26.45, 32.3, 3.3, 4.9, M['trim'], G, bevel=0.03)
box('evse_face', 26.45, 31.45, 26.5, 32.15, 3.5, 4.7, M['black'], G)
box('evse_led', 26.5, 31.7, 26.52, 31.9, 4.45, 4.55, mat('led', (0.2,1,0.3), 0.3, emit=((0.2,1.0,0.3), 20)), G)
box('evse_holster', 26.45, 31.5, 26.75, 32.1, 2.3, 2.9, M['black'], G)
cyl('evse_plug', 26.6, 31.8, 2.9, 3.5, 0.12, M['black'], G)
for k in range(6):   # cable loop hanging beside the unit
    cyl(f'evse_cable{k}', 26.55, 31.4 + k * 0.08, 1.6 + (k % 2) * 0.05, 3.3, 0.05, M['black'], G, verts=8)
box('backyard', -2, -25, 28, 0, 0, 0.35, M['lawn'], G)
box('patio', 17, -20, 27, -8, 0, 0.42, M['gravel'], G)
# fences
for nm, x1, y1, x2, y2 in (('fence_w', -2.4, -25, -2, 30), ('fence_e', 28, -25, 28.4, 30), ('fence_n', -2.4, -25.4, 28.4, -25)):
    box(nm, x1, y1, x2, y2, 0, 6, M['fence'], G)
    # boards
for i in range(0, 55):
    y = -25 + i * 1.0
    box(f'fb_w{i}', -2.5, y, -2.4, y + 0.45, 0, 6, M['fence'], G)
for i in range(0, 55):
    y = -25 + i * 1.0
    box(f'fb_e{i}', 28.4, y, 28.5, y + 0.45, 0, 6, M['fence'], G)
box('gate', 26.25, 29.8, 28, 30.2, 0, 6, M['fence'], G)
box('gate_w', -2, 29.8, 0, 30.2, 0, 6, M['fence'], G)
# front fence (low picket) along the sidewalk except the driveway
# planting
for k, (x, y, r) in enumerate(((1, 33, 2.0), (4.5, 34.5, 1.6), (8, 33, 2.2), (10.5, 36, 1.5), (9, 41, 1.2), (8.5, 45.5, 1.3), (1, 38.5, 1.1))):
    shrub(f'shrub{k}', x, y, r)
tree('tree_street', -14, 46.3, h=26, r=8)
tree('tree_front', 4.0, 42.5, h=13, r=3.2)
tree('tree_across', 8, 60, h=30, r=10, m=M['leaf2'])
tree('tree_backW', -10, -16, h=36, r=12)
tree('tree_backE', 36, -16, h=32, r=11, m=M['leaf2'])
tree('tree_neighborE', 44, 12, h=30, r=11)
tree('tree_far', -16, -32, h=45, r=16)
for k, (x, y) in enumerate(((25, -9), (24.5, -22), (0, -22), (27, -3))):
    shrub(f'bshrub{k}', x, y, 1.6)
# parked EV on the pad, plugged in
def prism_x(name, x1, x2, profile, m, cname='Yard', bevel=None):
    """Profile of (y, z) plan-feet points extruded along x from x1 to x2."""
    n = len(profile)
    v = [(x1 * F, -y * F, z * F) for y, z in profile] + [(x2 * F, -y * F, z * F) for y, z in profile]
    f = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    return add_mesh(name, v, f, m, cname, bevel)

def car(name, x, y, L=14.8, W=6.0, cname='Yard'):
    """Low-poly EV hatchback, nose toward the house (y = nose)."""
    paint = mat('carpaint', (0.12, 0.16, 0.22), 0.25, metallic=0.6)
    cglass = mat('carglass', (0.05, 0.06, 0.08), 0.05, metallic=0.2)
    body = [(0, 1.0), (0, 2.1), (0.6, 2.5), (4.6, 2.9), (13.6, 3.0), (L, 2.7), (L, 1.0)]
    prism_x(name+'.body', x, x + W, [(y + py, z) for py, z in body], paint, cname, bevel=0.12)
    cab = [(4.3, 2.85), (6.6, 4.65), (10.4, 4.7), (12.8, 3.9), (13.7, 2.9)]
    prism_x(name+'.cabin', x + 0.35, x + W - 0.35, [(y + py, z) for py, z in cab], cglass, cname, bevel=0.08)
    box(name+'.roof', x + 0.5, y + 6.7, x + W - 0.5, y + 10.3, 4.68, 4.8, paint, cname, bevel=0.04)
    for k, (cx, cy) in enumerate(((x + 0.2, y + 2.7), (x + W - 0.2, y + 2.7), (x + 0.2, y + L - 2.7), (x + W - 0.2, y + L - 2.7))):
        bpy.ops.mesh.primitive_cylinder_add(vertices=24, radius=1.15 * F, depth=0.7 * F, location=(cx * F, -cy * F, 1.15 * F), rotation=(0, math.pi / 2, 0))
        ob = bpy.context.object; ob.name = f'{name}.wheel{k}'; ob.data.materials.append(M['black'])
        for c in ob.users_collection: c.objects.unlink(ob)
        coll(cname).objects.link(ob)
        for p in ob.data.polygons: p.use_smooth = True
    box(name+'.lights_f', x + 0.4, y - 0.02, x + W - 0.4, y + 0.1, 2.15, 2.4, M['trim'], cname)
    box(name+'.lights_r', x + 0.4, y + L - 0.1, x + W - 0.4, y + L + 0.02, 2.3, 2.6, mat('taillight', (0.7, 0.05, 0.05), 0.2), cname)
    box(name+'.port', x + W - 0.02, y + 3.6, x + W + 0.03, y + 4.3, 2.3, 2.8, M['black'], cname)
car('ev', 19.5, 31.5)
# charge cable: from the holster along the ground to the car's port
for k, (x1, y1, x2, y2) in enumerate(((26.6, 32.2, 26.6, 34.2), (26.6, 34.2, 25.6, 34.2))):
    box(f'evcable{k}', min(x1, x2) - 0.05, min(y1, y2) - 0.05, max(x1, x2) + 0.05, max(y1, y2) + 0.05, 0.42, 0.52, M['black'], G)
cyl('evcable_up', 25.55, 35.5, 0.42, 2.5, 0.05, M['black'], G, verts=8)
# neighbor houses (context only)
def neighbor(name, x1, y1, x2, y2, h, m):
    box(name, x1, y1, x2, y2, 0, h, m, G); hip_roof(name+'.roof', x1, y1, x2, y2, h, overhang=1.5, cname=G)
neighbor('nbW', -34, 0, -6, 34, 12, M['neighbor1'])
neighbor('nbE', 32, 2, 58, 30, 11, M['neighbor2'])
neighbor('nbBack', -10, -60, 40, -36, 12, M['neighbor2'])
neighbor('nbAcross1', -20, 68, 12, 96, 12, M['neighbor1'])
neighbor('nbAcross2', 18, 68, 50, 96, 13, M['neighbor2'])

# ---------------------------------------------------------------- house shell
H = 'House'
# foundation / skirt + floor + ceiling
box('foundation', -0.25, -0.25, 26.25, 30.25, -1, Z0, M['concrete'], H)
box('floor_main', 0, 0, 26, 30, Z0 - 0.5, Z0, M['floor'], H)
box('floor_porch', 16, 26, 26, 34, Z0 - 0.5, Z0, M['floor'], H)
box('found_porch', 16, 30, 26, 34.25, -1, Z0 - 0.4, M['concrete'], H)
box('floor_mud', 12, -6.5, 23, 0, Z0 - 0.5, Z0, M['floor'], H)
box('found_mud', 12, -6.75, 23.25, 0, -1, Z0 - 0.4, M['concrete'], H)
box('ceiling', 0, 0, 26, 30, CEIL, CEIL + 0.5, M['ceiling'], 'Roof')
box('ceiling_porch', 16, 30, 26, 34, CEIL - 1.6, CEIL - 1.1, M['ceiling'], 'Roof')
box('ceiling_mud', 12, -6.5, 23, 0, CEIL - 2.6, CEIL - 2.1, M['ceiling'], 'Roof')

# exterior walls (main box), openings (a, b, sill, head)
W_SILL, W_HEAD = 2.6, 7.2
ext_wall('w_west', 0, -0, 0, 30, -1, openings=[(3, 7, W_SILL, W_HEAD), (13, 15.5, 4.0, W_HEAD), (19, 22, W_SILL, W_HEAD)])
ext_wall('w_east', 26, 0, 26, 12, +1, openings=[(8, 10, 4.0, W_HEAD)])
ext_wall('w_east2', 26, 12, 26, 26, +1, openings=[(17, 21, W_SILL, W_HEAD)])
ext_wall('w_east3', 26, 26, 26, 34, +1)
ext_wall('w_front', 0, 30, 16, 30, +1, openings=[(3, 9, W_SILL, W_HEAD)])
ext_wall('w_front_porch', 16, 34, 26, 34, +1, openings=[(19, 22, 0, 6.8), (23, 25.5, W_SILL, W_HEAD)])
ext_wall('w_porch_w', 16, 30, 16, 34, -1, openings=[(30.5, 33.5, W_SILL, W_HEAD)])
ext_wall('w_rear', 0, 0, 12, 0, -1, openings=[(4.5, 10.5, 0, 6.8)])            # existing slider, kept
ext_wall('w_rear_mid', 12, 0, 23, 0, -1, openings=[(12.4, 14.9, 0, 6.8)])       # old back wall inside the porch; existing doorway -> laundry
ext_wall('w_rear_e', 23, 0, 26, 0, -1)
ext_wall('w_mud_w', 12, -6.5, 12, 0, -1, openings=[(-5, -2.5, W_SILL, W_HEAD)])
ext_wall('w_mud_n', 12, -6.5, 23, -6.5, -1, openings=[(13.5, 16, 3.2, W_HEAD), (16.5, 19, 3.2, W_HEAD), (19.5, 22, 3.2, W_HEAD)])
ext_wall('w_mud_e', 23, -6.5, 23, 0, +1, openings=[(-4.5, -2, 0, 6.8)])       # side door to the east yard
# interior wall between porch and living/bedroom: x=16 from y26..30 (inside line), y=26 x16..26
wall('w_porch_in', 16, 26, 16, 30, 0.5, 0, CEIL, M['plaster'], openings=[(26.5, 29, 0, 6.8)])
wall('w_bed1_s', 16, 26, 26, 26, 0.5, 0, CEIL, M['plaster'])

# windows / doors
window('win_w1', 0, 3, 0, 7, W_SILL, W_HEAD, -1)
window('win_w2', 0, 13, 0, 15.5, 4.0, W_HEAD, -1)
window('win_w3', 0, 19, 0, 22, W_SILL, W_HEAD, -1)
window('win_e1', 26, 8, 26, 10, 4.0, W_HEAD, +1)
window('win_e2', 26, 17, 26, 21, W_SILL, W_HEAD, +1)
window('win_front', 3, 30, 9, 30, W_SILL, W_HEAD, +1)
window('win_porch_f', 23, 34, 25.5, 34, W_SILL, W_HEAD, +1)
window('win_porch_w', 16, 30.5, 16, 33.5, W_SILL, W_HEAD, -1)
window('win_mud_n1', 13.5, -6.5, 16, -6.5, 3.2, W_HEAD, -1)
window('win_mud_n2', 16.5, -6.5, 19, -6.5, 3.2, W_HEAD, -1)
window('win_mud_n3', 19.5, -6.5, 22, -6.5, 3.2, W_HEAD, -1)
window('win_mud_w', 12, -5, 12, -2.5, W_SILL, W_HEAD, -1)
door_slab('front_door', 19, 34, 22, 34, +1)
door_slab('mud_door', 23, -4.5, 23, -2, +1, m=M['trim'], glass_lite=True)
door_slab('laundry_door', 12.4, 0, 14.9, 0, -1, m=M['trim'], glass_lite=True)
door_slab('living_porch_door', 16, 26.5, 16, 29, -1, m=M['door'], glass_lite=True)
slider_door('slider', 4.5, 0, 10.5, 0, -1)

# steps
for k in range(4):
    box(f'step{k}', 18.5, 34.25 + k * 1.0, 22.5, 34.25 + (k + 1) * 1.0, 0, Z0 - 0.4 - k * 0.5, M['concrete'], H)
box('step_landing', 18.5, 34.25, 22.5, 35.0, 0, Z0 - 0.35, M['concrete'], H)
for xx in (18.4, 22.5):
    for yy, zz in ((34.4, Z0 - 0.35), (38.2, 0.4)):
        box(f'rpost{xx}{yy}', xx, yy, xx + 0.1, yy + 0.1, zz, zz + 2.9, M['black'], H)
    v = [(xx * F + 0.015, -34.4 * F, (Z0 + 2.55) * F), (xx * F + 0.015, -38.3 * F, 3.3 * F), (xx * F + 0.015, -38.3 * F, 3.2 * F), (xx * F + 0.015, -34.4 * F, (Z0 + 2.45) * F)]
    add_mesh(f'rail{xx}', v, [(0, 1, 2, 3)], M['black'], H).modifiers.new('s', 'SOLIDIFY').thickness = 0.03

# roofs
hip_roof('roof_main', 0, 0, 26, 30, CEIL + 0.6, pitch=5/12, overhang=1.8)
hip_roof('roof_porch', 16, 30, 26, 34.2, CEIL - 1.0, pitch=4/12, overhang=1.5, skip='S')
shed_roof('roof_mud', 12, -6.5, 23, 0, CEIL - 0.2, CEIL - 2.2, high_side='y+', overhang=1.2)
# chimney
box('chimney', 14.2, 21, 16.6, 24.5, Z0, CEIL + 0.6 + 5/12 * 14.8 + 3, M['brick'], 'Roof')
box('chimney_cap', 14.0, 20.8, 16.8, 24.7, CEIL + 0.6 + 5/12 * 14.8 + 3, CEIL + 0.6 + 5/12 * 14.8 + 3.3, M['concrete'], 'Roof')

# ---------------------------------------------------------------- interior partitions (proposed plan)
IW = 0.45
wall('p_kit_hall', 15, 0, 15, 8, IW, Z0, CEIL, M['plaster'])   # hall walls removed: kitchen open to living
wall('p_hall_bed2', 17, 0, 17, 12, IW, Z0, CEIL, M['plaster'], openings=[(9, 11.5, 0, 6.8)])
wall('p_bed1_n', 15, 12, 26, 12, IW, Z0, CEIL, M['plaster'])
wall('p_bath_n', 0, 12, 9, 12, IW, Z0, CEIL, M['plaster'])
wall('p_bath_hall', 9, 12, 9, 17, IW, Z0, CEIL, M['plaster'], openings=[(13.5, 16, 0, 6.8)])
wall('p_living_n', 0, 17, 9, 17, IW, Z0, CEIL, M['plaster'])
wall('p_living_e', 15, 12, 15, 26, IW, Z0, CEIL, M['plaster'], openings=[(13, 15.5, 0, 6.8)])
wall('p_closet1', 21, 12, 21, 14.5, IW, Z0, CEIL, M['plaster']); wall('p_closet1b', 21, 14.5, 26, 14.5, IW, Z0, CEIL, M['plaster'], openings=[(22, 25, 0, 6.8)])
wall('p_closet2', 17, 3, 20, 3, IW, Z0, CEIL, M['plaster'], openings=[(17.3, 19.7, 0, 6.8)]); wall('p_closet2b', 20, 0, 20, 3, IW, Z0, CEIL, M['plaster'])

# door/opening casings (interior, white)
def casing(x1, y1, x2, y2, head, along_x):
    tw = 0.3
    if along_x:
        box(f'cs{x1}{y1}a', x1 - tw, y1 - 0.3, x1, y1 + 0.3, Z0, Z0 + head + tw, M['trim'], H); box(f'cs{x1}{y1}b', x2, y1 - 0.3, x2 + tw, y1 + 0.3, Z0, Z0 + head + tw, M['trim'], H)
        box(f'cs{x1}{y1}c', x1 - tw, y1 - 0.3, x2 + tw, y1 + 0.3, Z0 + head, Z0 + head + tw, M['trim'], H)
    else:
        box(f'cs{x1}{y1}a', x1 - 0.3, y1 - tw, x1 + 0.3, y1, Z0, Z0 + head + tw, M['trim'], H); box(f'cs{x1}{y1}b', x1 - 0.3, y2, x1 + 0.3, y2 + tw, Z0, Z0 + head + tw, M['trim'], H)
        box(f'cs{x1}{y1}c', x1 - 0.3, y1 - tw, x1 + 0.3, y2 + tw, Z0 + head, Z0 + head + tw, M['trim'], H)
casing(15, 13, 15, 15.5, 6.8, False); casing(9, 13.5, 9, 16, 6.8, False)
casing(17, 9, 17, 11.5, 6.8, False); casing(16, 26.5, 16, 29, 6.8, False)

# baseboard + picture rail + wainscot in the living room
def baseboard(x1, y1, x2, y2, h=0.55, m=None):
    m = m or M['trim']
    box(f'bb{x1}_{y1}_{x2}_{y2}', x1, y1, x2, y2, Z0, Z0 + h, m, H)
# living room (x 0..15, y 17..30) wainscot 3.3 ft, accent above
LR = ((0.5, 17.25, 0.57, 29.5, [(19, 22, W_SILL, W_HEAD)]), (0.5, 17.25, 9.0, 17.32, []), (14.68, 17.25, 14.75, 29.5, []), (0.5, 29.43, 15.75, 29.5, [(3, 9, W_SILL, W_HEAD)]))
def panel(name, x1, y1, x2, y2, z1, z2, m, holes):
    """Wall panel box, split around openings (a, b, sill, head) along the wall."""
    horiz = (x2 - x1) > (y2 - y1)
    a0, a1 = (x1, x2) if horiz else (y1, y2)
    segs, cur = [], a0
    for (a, b, sill, head) in sorted(holes):
        zs, zh = Z0 + sill, Z0 + head
        segs.append((cur, a, z1, z2))
        if z1 < zs: segs.append((a, b, z1, min(z2, zs)))
        if z2 > zh: segs.append((a, b, max(z1, zh), z2))
        cur = b
    segs.append((cur, a1, z1, z2))
    for k, (a, b, za, zb) in enumerate(segs):
        if b - a <= 0.01 or zb - za <= 0.01: continue
        if horiz: box(f'{name}.{k}', a, y1, b, y2, za, zb, m, H)
        else: box(f'{name}.{k}', x1, a, x2, b, za, zb, m, H)
for i, (x1, y1, x2, y2, holes) in enumerate(LR):
    panel(f'wains{i}', x1, y1, x2, y2, Z0, Z0 + 3.3, M['wainscot'], holes)
    panel(f'wcap{i}', x1 - 0.05, y1 - 0.05, x2 + 0.05, y2 + 0.05, Z0 + 3.3, Z0 + 3.4, M['trim'], holes)
    panel(f'accent{i}', x1, y1, x2, y2, Z0 + 3.4, CEIL - 0.9, M['accent'], holes)
    box(f'prail{i}', x1 - 0.05, y1 - 0.05, x2 + 0.05, y2 + 0.05, CEIL - 0.9, CEIL - 0.8, M['trim'], H)
    box(f'crown{i}', x1 - 0.15, y1 - 0.15, x2 + 0.15, y2 + 0.15, CEIL - 0.4, CEIL, M['trim'], H)
# stiles on wainscot (front + west walls), skipping window bays
for k in range(0, 8):
    y = 17.5 + k * 1.6
    if not (19 <= y <= 22): box(f'stile_w{k}', 0.57, y, 0.65, y + 0.15, Z0 + 0.5, Z0 + 3.3, M['trim'], H)
for k in range(0, 9):
    x = 0.6 + k * 1.6
    if not (3 <= x <= 9): box(f'stile_f{k}', x, 29.35, x + 0.15, 29.43, Z0 + 0.5, Z0 + 3.3, M['trim'], H)
# fireplace: white surround + brick firebox + mantel + built-in shelves to the left
box('fp_surround', 13.9, 20.7, 14.3, 24.8, Z0, Z0 + 4.6, M['wainscot'], H)
box('fp_hearth', 13.0, 20.5, 14.3, 25.0, Z0, Z0 + 0.15, M['brick'], H)
box('fp_firebox_back', 14.3, 21.6, 15.0, 23.9, Z0, Z0 + 2.6, M['brick'], H)
box('fp_face', 13.88, 21.3, 13.95, 24.2, Z0, Z0 + 3.2, M['brick'], H)
box('fp_open', 13.85, 21.6, 13.95, 23.9, Z0 + 0.15, Z0 + 2.6, mat('firebox', (0.02,0.02,0.02), 0.9), H)
box('fp_mantel', 13.6, 20.5, 14.3, 25.0, Z0 + 4.6, Z0 + 4.85, M['trim'], H)
box('fp_upper', 14.0, 20.7, 14.3, 24.8, Z0 + 4.85, CEIL, M['wainscot'], H)
box('builtin', 14.3, 18, 15.0, 20.5, Z0, Z0 + 7.5, M['wainscot'], H)
for k in range(5):
    box(f'shelf{k}', 14.35, 18.1, 15.0, 20.4, Z0 + 1.2 + k * 1.3, Z0 + 1.3 + k * 1.3, M['walnut'], H)
    box(f'book{k}', 14.45, 18.3 + (k % 3) * 0.3, 15.0, 19.6 + (k % 2) * 0.5, Z0 + 1.3 + k * 1.3, Z0 + 1.3 + k * 1.3 + 0.9, mat(f'book{k}', ((0.6,0.3,0.2),(0.2,0.3,0.5),(0.7,0.6,0.4),(0.3,0.5,0.4),(0.5,0.2,0.3))[k], 0.7), H)
# baseboards everywhere else (rough)
for (x1, y1, x2, y2) in ((0.25, 0.25, 0.32, 12), (0.25, 0.25, 15, 0.32), (14.68, 0.25, 14.75, 7.8), (17.25, 0.25, 17.32, 12), (9.25, 12.25, 9.32, 13.5), (9.25, 16, 9.32, 16.75), (25.68, 0.25, 25.75, 12), (17.25, 11.68, 26, 11.75), (15.25, 12.25, 15.32, 26), (15.25, 12.25, 26, 12.32), (25.68, 12.25, 25.75, 26)):
    baseboard(x1, y1, x2, y2)

# ---------------------------------------------------------------- kitchen (rear-left, eat-in)
K = 'Furniture'
CH = Z0 + 3.0   # counter height
# lower cabinets along west wall y 3..11.5 and rear wall x 0.5..14.5 (range wall)
SW = 12 - IW / 2   # inner face of the bath wall
box('kc_low_w', 0.32, 3, 2.3, SW - 2.0, Z0 + 0.35, CH - 0.1, M['cabinet'], K)
box('kc_toe_w', 0.32, 3, 2.0, SW - 2.0, Z0, Z0 + 0.35, M['black'], K)
box('kc_low_s', 0.32, SW - 2.0, 9.0, SW, Z0 + 0.35, CH - 0.1, M['cabinet'], K)
box('kc_toe_s', 0.32, SW - 2.0, 9.0, SW, Z0, Z0 + 0.35, M['black'], K)
box('kc_top_w', 0.32, 2.9, 2.4, SW - 2.0, CH - 0.1, CH, M['quartz'], K)
box('kc_top_s', 0.32, SW - 2.1, 9.05, SW, CH - 0.1, CH, M['quartz'], K)
# drawer/door lines + black bar pulls
for k in range(7):
    y = 3.2 + k * 0.92
    box(f'kd_w{k}', 2.3, y, 2.34, y + 0.06, Z0 + 0.4, CH - 0.15, M['black'], K)
    box(f'kh_w{k}', 2.34, y + 0.25, 2.42, y + 0.7, CH - 0.55, CH - 0.48, M['black'], K)
for k in range(8):
    x = 0.5 + k * 1.05
    if 3.3 < x < 6.2: continue   # range bay
    box(f'kd_s{k}', x, SW - 2.04, x + 0.06, SW - 2.0, Z0 + 0.4, CH - 0.15, M['black'], K)
    box(f'kh_s{k}', x + 0.3, SW - 2.12, x + 0.75, SW - 2.04, CH - 0.55, CH - 0.48, M['black'], K)
# backsplash tile to underside of uppers
box('ks_w', 0.28, 2.9, 0.36, SW, CH, CH + 1.6, M['tile'], K)
box('ks_s', 0.28, SW - 0.08, 9.0, SW, CH, CH + 1.6, M['tile'], K)
# uppers (white): west wall beside the window, bath wall either side of the hood, over the fridge
box('ku_w1', 0.32, 7.4, 1.4, SW - 0.9, CH + 1.6, Z0 + 7.6, M['cabinet2'], K)
box('ku_s1', 0.32, SW - 0.9, 3.3, SW, CH + 1.6, Z0 + 7.6, M['cabinet2'], K)
box('ku_s2', 6.2, SW - 0.9, 9.0, SW, CH + 1.6, Z0 + 7.6, M['cabinet2'], K)
box('ku_fr', 0.5, 0.32, 3.4, 1.6, Z0 + 6.7, Z0 + 7.6, M['cabinet2'], K)
# open shelves either side of the window
for z in (CH + 1.7, CH + 3.0):
    box(f'ks_sh{z}', 0.32, 2.9, 1.2, 7.3, z, z + 0.08, M['walnut'], K)
# sink under the west window (y 5..7 -> centered 5), faucet
box('sink', 0.55, 4.0, 2.1, 6.6, CH - 0.55, CH, M['steel'], K)
box('sink_hole', 0.6, 4.05, 2.05, 6.55, CH - 0.5, CH + 0.01, M['steel'], K)
cyl('faucet', 0.7, 5.3, CH, CH + 1.1, 0.06, M['black'], K); box('faucet_arm', 0.7, 5.25, 1.35, 5.35, CH + 1.05, CH + 1.13, M['black'], K)
# range + hood on the bath wall (x 3.5..6)
box('range', 3.5, SW - 2.1, 6.0, SW - 0.1, Z0, CH, M['steel'], K)
box('range_top', 3.5, SW - 2.1, 6.0, SW - 0.1, CH, CH + 0.05, M['black'], K)
for k in range(2):
    for j in range(2):
        cyl(f'burner{k}{j}', 4.1 + k * 1.25, SW - 1.6 + j * 1.0, CH + 0.05, CH + 0.12, 0.35, M['black'], K)
box('hood', 3.3, SW - 1.9, 6.2, SW - 0.05, Z0 + 5.8, Z0 + 6.3, M['steel'], K)
cyl('hood_duct', 4.75, SW - 1.0, Z0 + 6.3, CEIL, 0.5, M['steel'], K)
# fridge against the rear wall, west of the slider
box('fridge', 0.5, 0.35, 3.4, 2.9, Z0, Z0 + 6.6, M['steel'], K, bevel=0.01)
box('fridge_line', 0.5, 2.9, 3.4, 2.92, Z0 + 3.5, Z0 + 3.55, M['black'], K)
# island / table 5x3 at (5..10, 4..7) -> a walnut table with 4 chairs
box('table', 5, 4, 10, 7, Z0 + 2.4, Z0 + 2.55, M['walnut'], K, bevel=0.01)
for (x, y) in ((5.4, 4.4), (9.6, 4.4), (5.4, 6.6), (9.6, 6.6)):
    box(f'tleg{x}{y}', x - 0.15, y - 0.15, x + 0.15, y + 0.15, Z0, Z0 + 2.4, M['walnut'], K)
def chair(name, x, y, facing):
    box(name+'.seat', x - 0.8, y - 0.8, x + 0.8, y + 0.8, Z0 + 1.4, Z0 + 1.55, M['black'], K, bevel=0.01)
    for dx in (-0.65, 0.65):
        for dy in (-0.65, 0.65):
            box(f'{name}.l{dx}{dy}', x + dx - 0.06, y + dy - 0.06, x + dx + 0.06, y + dy + 0.06, Z0, Z0 + 1.4, M['black'], K)
    if facing == 'n': box(name+'.back', x - 0.8, y + 0.7, x + 0.8, y + 0.8, Z0 + 1.55, Z0 + 3.0, M['black'], K)
    else: box(name+'.back', x - 0.8, y - 0.8, x + 0.8, y - 0.7, Z0 + 1.55, Z0 + 3.0, M['black'], K)
chair('ch1', 6.2, 8.2, 'n'); chair('ch2', 8.8, 8.2, 'n'); chair('ch3', 6.2, 2.8, 's'); chair('ch4', 8.8, 2.8, 's')
# pendants over the table
for x in (6.3, 8.7):
    cyl(f'pend_cord{x}', x, 5.5, Z0 + 7.0, CEIL, 0.02, M['black'], K)
    cyl(f'pend_shade{x}', x, 5.5, Z0 + 6.2, Z0 + 7.0, 0.6, M['shade'], K)
    cyl(f'pend_bulb{x}', x, 5.5, Z0 + 5.85, Z0 + 6.6, 0.4, M['bulb'], K)
# a plant and a bowl
cyl('kpot', 1.3, 10.6, CH, CH + 0.5, 0.35, M['pot'], K); sphere('kplant', 1.3, 10.6, CH + 0.9, 0.6, M['plant'], K)
cyl('bowl', 7.5, 5.5, Z0 + 2.55, Z0 + 2.75, 0.6, M['pot'], K)

# ---------------------------------------------------------------- living room furniture
# sofa on the west wall facing the fireplace
box('sofa_base', 1.2, 20.5, 4.2, 27.5, Z0 + 0.6, Z0 + 1.5, M['fabric'], K, bevel=0.06)
box('sofa_back', 1.2, 20.5, 1.9, 27.5, Z0 + 1.5, Z0 + 2.7, M['fabric'], K, bevel=0.06)
box('sofa_arm1', 1.2, 20.5, 4.2, 21.1, Z0 + 1.5, Z0 + 2.1, M['fabric'], K, bevel=0.06)
box('sofa_arm2', 1.2, 26.9, 4.2, 27.5, Z0 + 1.5, Z0 + 2.1, M['fabric'], K, bevel=0.06)
box('sofa_legs', 1.4, 20.7, 4.0, 27.3, Z0, Z0 + 0.6, M['walnut'], K)
for i, y in enumerate((21.3, 23.3, 25.3)):
    box(f'cushion{i}', 1.9, y, 4.1, y + 1.8, Z0 + 1.5, Z0 + 2.0, M['fabric'], K, bevel=0.08)
box('pillow1', 1.9, 21.4, 2.4, 22.8, Z0 + 2.0, Z0 + 3.2, M['fabric2'], K, bevel=0.08)
box('rug', 1.0, 19.0, 12.5, 29.0, Z0, Z0 + 0.05, M['rug'], K)
cyl('coffee', 7.5, 24, Z0 + 1.2, Z0 + 1.32, 1.6, M['walnut'], K); cyl('coffee_leg', 7.5, 24, Z0, Z0 + 1.2, 0.25, M['black'], K)
# armchair by the front window
box('chair_base', 5.5, 27.8, 8.3, 30.0 - 0.6, Z0 + 0.5, Z0 + 1.5, M['fabric2'], K, bevel=0.08)
box('chair_back', 5.5, 28.8, 8.3, 29.4, Z0 + 1.5, Z0 + 2.9, M['fabric2'], K, bevel=0.08)
# floor lamp
cyl('lamp_pole', 12.5, 28.5, Z0, Z0 + 5.5, 0.05, M['black'], K); cyl('lamp_shade', 12.5, 28.5, Z0 + 5.0, Z0 + 6.2, 0.8, mat('shade2', (0.95,0.92,0.85), 0.9), K)
cyl('lamp_bulb', 12.5, 28.5, Z0 + 5.2, Z0 + 6.0, 0.3, M['bulb'], K)
# art over the fireplace + plant
box('art1', 13.66, 21.8, 13.8, 23.7, Z0 + 5.2, Z0 + 7.0, M['art'], K); box('art1f', 13.7, 21.7, 13.88, 23.8, Z0 + 5.1, Z0 + 7.1, M['walnut'], K)
cyl('lpot', 12.5, 18.5, Z0, Z0 + 1.2, 0.7, M['pot'], K); sphere('lplant', 12.5, 18.5, Z0 + 2.6, 1.1, M['plant'], K, scale=(1, 1, 1.5))
# ceiling fixture
cyl('lr_fix', 7.5, 23.5, CEIL - 0.6, CEIL, 0.9, mat('opal', (1,1,1), 0.3, emit=((1.0,0.9,0.75), 8)), 'Roof')

# bedroom 1 (x15..26, y12..26): bed against the east wall
box('bed', 18.0, 15.5, 25.5, 21.5, Z0 + 0.8, Z0 + 1.9, M['bedding'], K, bevel=0.08)
box('bed_frame', 18.0, 15.4, 25.5, 21.6, Z0 + 0.4, Z0 + 0.8, M['walnut'], K)
box('headboard', 25.3, 15.2, 25.6, 21.8, Z0, Z0 + 4.0, M['walnut'], K)
box('duvet', 18.2, 15.7, 23.5, 21.3, Z0 + 1.9, Z0 + 2.3, M['fabric2'], K, bevel=0.1)
for y in (16.2, 18.8):
    box(f'pillow{y}', 23.6, y, 25.2, y + 2.2, Z0 + 1.9, Z0 + 2.6, M['bedding'], K, bevel=0.15)
box('nightstand', 24.0, 22.2, 25.6, 23.8, Z0, Z0 + 2.0, M['walnut'], K)
# bedroom 2 (x17..26, y0..12): small bed
box('bed2', 20.5, 5.0, 25.5, 11.0, Z0 + 0.8, Z0 + 1.8, M['bedding'], K, bevel=0.08)
box('bed2_frame', 20.5, 4.9, 25.5, 11.1, Z0 + 0.4, Z0 + 0.8, M['walnut'], K)
# bath (x0..9, y12..17)
box('tub', 0.3, 15.0, 5.0, 16.7, Z0, Z0 + 1.8, M['cabinet2'], K, bevel=0.05)
box('vanity', 4.0, 12.3, 9 - 0.3, 13.9, Z0, CH - 0.2, M['cabinet'], K); box('vanity_top', 4.0, 12.3, 8.7, 14.0, CH - 0.2, CH, M['quartz'], K)
cyl('toilet', 1.5, 13.2, Z0, Z0 + 1.4, 0.7, M['cabinet2'], K)
# mudroom: washer/dryer + water heater
box('washer', 17.2, -6.15, 19.5, -3.9, Z0, Z0 + 3.0, M['cabinet2'], K, bevel=0.03); box('dryer', 19.7, -6.15, 22.0, -3.9, Z0, Z0 + 3.0, M['cabinet2'], K, bevel=0.03)
cyl('wh', 13.3, -1.3, Z0, Z0 + 4.5, 0.9, M['cabinet2'], K)
box('bench', 15.5, -1.0, 21.5, -0.35, Z0 + 1.4, Z0 + 1.55, M['walnut'], K)
for x in (15.7, 21.3): box(f'bench_l{x}', x - 0.1, -0.95, x + 0.1, -0.4, Z0, Z0 + 1.4, M['walnut'], K)
for x in (16.5, 18, 19.5, 21): box(f'hook{x}', x, -0.35, x + 0.1, -0.2, Z0 + 5.3, Z0 + 5.45, M['black'], K)

# ---------------------------------------------------------------- deck
D = 'Deck'
box('deck_frame', 2, -8, 12, 0, Z0 - 1.0, Z0 - 0.4, M['deck'], D)
for i in range(26):
    y = -8 + i * 0.31
    box(f'dk{i}', 2, y, 12, y + 0.26, Z0 - 0.4, Z0 - 0.25, M['deck'], D)
# railing (black metal, horizontal cable look)
for (x1, y1, x2, y2) in ((2, -8, 12, -8), (12, -8, 12, -6.5), (2, -6.5, 2, 0)):
    for k in range(8):
        f = k / 7
        box(f'rail_{x1}{y1}{k}', x1 - 0.03, y1 - 0.03, x2 + 0.03, y2 + 0.03, Z0 - 0.25 + 0.4 + f * 2.6, Z0 - 0.25 + 0.4 + f * 2.6 + 0.04, M['black'], D)
    n = int(max(abs(x2 - x1), abs(y2 - y1)) / 3.5) + 1
    for k in range(n + 1):
        px = x1 + (x2 - x1) * k / n; py = y1 + (y2 - y1) * k / n
        box(f'post_{x1}{y1}{k}', px - 0.1, py - 0.1, px + 0.1, py + 0.1, Z0 - 0.4, Z0 + 3.0, M['black'], D)
    box(f'cap_{x1}{y1}', x1 - 0.15, y1 - 0.15, x2 + 0.15, y2 + 0.15, Z0 + 3.0, Z0 + 3.15, M['walnut'], D)
# stairs off the west end of the deck (x -1..2), stepping down toward the front along the side yard
for k in range(4):
    box(f'dstep{k}', -1, -8 + k * 1.5, 2, -8 + (k + 1) * 1.5, -0.2, Z0 - 0.25 - (k + 1) * 0.44, M['deck'], D)
# outdoor furniture: small table + 2 chairs, planter
cyl('otable', 7, -4.5, Z0 + 2.2, Z0 + 2.3, 1.4, M['black'], D); cyl('otable_leg', 7, -4.5, Z0 - 0.25, Z0 + 2.2, 0.15, M['black'], D)
for x in (5.0, 9.0):
    box(f'ochair{x}', x - 0.8, -5.3, x + 0.8, -3.7, Z0 + 1.2, Z0 + 1.35, M['black'], D); box(f'ochairb{x}', x - 0.8, -5.3 if x > 7 else -3.85, x + 0.8, -5.15 if x > 7 else -3.7, Z0 + 1.35, Z0 + 2.8, M['black'], D)
box('planter', 10.2, -7.6, 11.8, -6.2, Z0 - 0.25, Z0 + 1.6, M['pot'], D); sphere('planter_plant', 11.0, -6.9, Z0 + 2.4, 1.2, M['plant'], D)

# ---------------------------------------------------------------- lighting + world
sun = bpy.data.objects.new('sun', bpy.data.lights.new('sun', 'SUN')); scene.collection.objects.link(sun)
sun.data.energy = 5.0; sun.data.angle = math.radians(1.0)
sun_elev, sun_rot = math.radians(48), math.radians(215)   # afternoon light from the south-west (street is -Y = south)
sun.rotation_euler = (math.pi/2 - sun_elev, 0, math.radians(-35))   # light travels toward +X,+Y: sun in the south-west
world = bpy.data.worlds.new('world'); scene.world = world; world.use_nodes = True
wn = world.node_tree; bg = wn.nodes['Background']
sky = wn.nodes.new('ShaderNodeTexSky')
for attr, val in (('sky_type', 'NISHITA'), ('sun_elevation', sun_elev), ('sun_rotation', sun_rot), ('sun_disc', False), ('altitude', 10), ('air_density', 1.0), ('dust_density', 1.5), ('ozone_density', 1.0)):
    try: setattr(sky, attr, val)
    except Exception as e: print('sky attr', attr, e)
wn.links.new(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = 0.25
# interior fill so windows don't blow out: portals at the big glass
def portal(name, x, y, z, sx, sz, rot):
    L = bpy.data.lights.new(name, 'AREA'); L.shape = 'RECTANGLE'; L.size = sx * F; L.size_y = sz * F; L.energy = 0
    try: L.cycles.is_portal = True
    except Exception: pass
    ob = bpy.data.objects.new(name, L); scene.collection.objects.link(ob); ob.location = (x * F, -y * F, z * F); ob.rotation_euler = rot
portal('portal_slider', 7.5, 0.6, Z0 + 3.4, 6, 6.8, (math.pi/2, 0, 0))
portal('portal_front', 6, 29.4, Z0 + 4.9, 6, 4.6, (math.pi/2, 0, 0))
portal('portal_w1', 0.6, 5, Z0 + 4.9, 4, 4.6, (math.pi/2, 0, math.pi/2))
portal('portal_w3', 0.6, 20.5, Z0 + 4.9, 3, 4.6, (math.pi/2, 0, math.pi/2))

# ---------------------------------------------------------------- render setup
scene.render.engine = 'CYCLES'
try:
    prefs = bpy.context.preferences.addons['cycles'].preferences
    prefs.compute_device_type = 'METAL'; prefs.get_devices()
    for d in prefs.devices: d.use = True
    scene.cycles.device = 'GPU'
except Exception as e:
    print('GPU setup failed, CPU:', e)
scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True; scene.cycles.use_adaptive_sampling = True
scene.cycles.max_bounces = 8; scene.cycles.diffuse_bounces = 4; scene.cycles.glossy_bounces = 4; scene.cycles.transmission_bounces = 8; scene.cycles.transparent_max_bounces = 8
scene.cycles.caustics_reflective = False; scene.cycles.caustics_refractive = False; scene.cycles.blur_glossy = 1.0
scene.render.resolution_x = 1800; scene.render.resolution_y = 1200; scene.render.resolution_percentage = SCALE
scene.render.image_settings.file_format = 'PNG'
try: scene.view_settings.view_transform = 'AgX'
except Exception: scene.view_settings.view_transform = 'Filmic'
for lk in ('AgX - Medium High Contrast', 'Medium High Contrast'):
    try: scene.view_settings.look = lk; break
    except Exception: pass

cam = bpy.data.objects.new('cam', bpy.data.cameras.new('cam')); scene.collection.objects.link(cam); scene.camera = cam
def look(cam, pos, target):
    cam.location = pos; d = Vector(target) - Vector(pos)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
def P(x, y, z): return (x * F, -y * F, z * F)

VIEWS = {
    # name: (camera pos, target, lens mm, exposure, hide_roof, sensor shift)
    'front':     (P(-4, 64, 6.0),  P(14, 24, 9.0),  24, 0.0, False),
    'rear':      (P(-1, -23, 6.5),  P(13, 2, 7.0),   24, 0.0, False),
    'living':    (P(1.2, 17.6, Z0 + 5.0), P(11.5, 27.5, Z0 + 4.3), 17, 1.2, False),
    'kitchen':   (P(14.3, 12.8, Z0 + 5.3), P(3.0, 2.5, Z0 + 3.9), 16, 1.2, False),
    'open':      (P(3.5, 27.5, Z0 + 5.2), P(11.5, 8.0, Z0 + 4.0), 18, 1.2, False),
    'kitchen2':  (P(1.6, 8.4, Z0 + 5.2), P(11.5, 1.0, Z0 + 4.0), 17, 1.2, False),
    'dollhouse': (P(-20, 68, 58),   P(13, 14, Z0),   35, 0.3, True),
    'drive':     (P(34, 55, 5.5),   P(20, 31, 5.0),  28, 0.0, False),
}
if not views: views = list(VIEWS)
os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
for v in views:
    pos, tgt, lens, expo, hide_roof = VIEWS[v]
    look(cam, pos, tgt); cam.data.lens = lens; cam.data.clip_start = 0.05
    scene.view_settings.exposure = expo
    coll('Roof').hide_render = hide_roof
    if hide_roof:
        for ob in coll('House').objects:
            if ob.name.startswith('roof') or ob.name.startswith('ceiling'): ob.hide_render = True
    scene.render.filepath = os.path.join(ROOT, 'out', f'{v}.png')
    print('rendering', v); bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, 'house.blend'))
print('done')
