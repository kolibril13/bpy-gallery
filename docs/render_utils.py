import bpy
from IPython.display import Image, display
from mathutils import Vector
from pathlib import Path
# from typst_importer.curve_utils import get_curve_collection_bounds
import tempfile
from math import radians

def fresh_scene(keep_cube=False):
    bpy.ops.object.select_all(action='DESELECT')
    # Keep only Plane, Camera and Sun
    for obj in bpy.context.scene.objects:
        if obj.name not in ['PlaneBG', 'Camera', 'Sun']:
            obj.select_set(True)
    bpy.ops.object.delete()
    for collection in bpy.data.collections:
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)
    
    # Add a light source if it doesn't exist
    if 'Sun' not in bpy.context.scene.objects:
        bpy.ops.object.light_add(type='SUN')
        sun = bpy.context.active_object
        sun.location = (0, 0, 0)
        sun.rotation_euler = (radians(204), radians(-133), radians(-67))
        sun.data.energy = 3


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
        if isinstance(collection, list):
            # Merge collections temporarily for rendering
            temp_collection = bpy.data.collections.new("TempRenderCollection")
            bpy.context.scene.collection.children.link(temp_collection)
            
            for c in collection:
                for obj in c.objects:
                    temp_collection.objects.link(obj)
            
            adjust_camera_to_collection(temp_collection, padding_factor)
            
            # Clean up after rendering
            bpy.context.scene.collection.children.unlink(temp_collection)
            bpy.data.collections.remove(temp_collection)
        else:
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
