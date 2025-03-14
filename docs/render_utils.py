import bpy
from IPython.display import Image, display
from mathutils import Vector
from pathlib import Path
from typst_importer.curve_utils import get_curve_collection_bounds
import tempfile

def fresh_scene(keep_cube=False):
    bpy.ops.object.select_all(action='DESELECT')
    # Keep only Plane, Camera and Sun
    for obj in bpy.context.scene.objects:
        if obj.name not in ['Plane', 'Camera', 'Sun']:
            obj.select_set(True)
    bpy.ops.object.delete()
    for collection in bpy.data.collections:
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)

def adjust_camera_to_collection(c, padding_factor=-0.2):
    min_p, max_p = get_curve_collection_bounds(c)
    center = (min_p + max_p) / 2
    size = max_p - min_p
    padded_size = size * (1 + padding_factor)
    padded_max_dim = max(padded_size.x, padded_size.y, padded_size.z)

    if 'Camera' not in bpy.data.objects:
        bpy.ops.object.camera_add()
        camera = bpy.data.objects['Camera']
    else:
        camera = bpy.data.objects['Camera']
    
    bpy.context.scene.camera = camera
    camera.location = (center.x, center.y, center.z + padded_max_dim*2)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = padded_max_dim * 2
    aspect_ratio = padded_size.x / padded_size.y
    bpy.context.scene.render.resolution_x = 960
    bpy.context.scene.render.resolution_y = int(960 / aspect_ratio)

def render_result(width="300pt", collection=None, padding_factor=-0.2):
    if collection is not None:
        adjust_camera_to_collection(collection, padding_factor)
        
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = str(Path(tmpdir) / 'img.png')
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(filepath=output_path)
        display(Image(filename=output_path, width=width, height="auto"))

def load_paper_background():
    path = Path.home() / "projects/bpy-gallery/docs/paper_background.blend"
    filepath = str(path)
    
    with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)