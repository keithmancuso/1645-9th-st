"""Export house.blend to 3d/house.glb with simplified (flat-color) materials for the web viewer.
Run: Blender -b render/house.blend -P render/export_gltf.py"""
import bpy, os
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, '..', '3d', 'house.glb')

# flatten materials: keep Principled base color / roughness / metallic / emission, drop procedural inputs
for m in bpy.data.materials:
    if not m.use_nodes: continue
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf: continue
    out = next((n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL'), None)
    for sock in ('Base Color', 'Roughness', 'Normal', 'Metallic'):
        for l in list(bsdf.inputs[sock].links): nt.links.remove(l)
    # ensure the principled node drives the output directly
    for l in list(out.inputs['Surface'].links): nt.links.remove(l)
    nt.links.new(bsdf.outputs[0], out.inputs['Surface'])
    if bsdf.inputs['Transmission Weight'].default_value > 0.5:
        bsdf.inputs['Transmission Weight'].default_value = 0
        bsdf.inputs['Base Color'].default_value = (0.75, 0.85, 0.9, 1)
        bsdf.inputs['Alpha'].default_value = 0.25
        m.blend_method = 'BLEND'
        m.surface_render_method = 'BLENDED' if hasattr(m, 'surface_render_method') else None
    if m.name == 'floor': bsdf.inputs['Base Color'].default_value = (0.62, 0.42, 0.24, 1)
    if m.name == 'lawn': bsdf.inputs['Base Color'].default_value = (0.25, 0.42, 0.15, 1)
    if m.name == 'roof': bsdf.inputs['Base Color'].default_value = (0.16, 0.16, 0.17, 1)
    if m.name == 'brick': bsdf.inputs['Base Color'].default_value = (0.5, 0.22, 0.15, 1)
    if m.name == 'tile': bsdf.inputs['Base Color'].default_value = (0.92, 0.92, 0.9, 1)
    if m.name == 'quartz': bsdf.inputs['Base Color'].default_value = (0.9, 0.9, 0.88, 1)

# tag objects with their collection, drop lights/cameras/portals
for ob in list(bpy.data.objects):
    if ob.type != 'MESH':
        bpy.data.objects.remove(ob); continue
    ob['coll'] = ob.users_collection[0].name if ob.users_collection else ''
    if ob.name.startswith('portal'): bpy.data.objects.remove(ob)

bpy.ops.export_scene.gltf(filepath=OUT, export_format='GLB', export_apply=True, export_extras=True,
                          export_lights=False, export_cameras=False, export_yup=True, export_animations=False)
print('exported', OUT, os.path.getsize(OUT) // 1024, 'KB')
