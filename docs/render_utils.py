import bpy
from IPython.display import Image, display
from mathutils import Vector
from pathlib import Path
from typst_importer.curve_utils import get_curve_collection_bounds
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
    load_paper_background()




def get_curve_collection_bounds2(collection):
    # get_curve_collection_bounds was somehow broken in original, even it if looks the same as here https://github.com/kolibril13/blender_typst_importer/blob/2f4aaa54134ec00de6f7a5294e33ce46e9ebc792/typst_importer/curve_utils.py
    """
    Calculate the bounding box dimensions of a collection containing curves and/or meshes.

    Args:
        collection: Blender collection object containing curves and/or meshes

    Returns:
        tuple: ((min_x, min_y, min_z), (max_x, max_y, max_z))
        The minimum and maximum coordinates of the bounding box
    """
    # Initialize bounds
    min_x = min_y = min_z = float("inf")
    max_x = max_y = max_z = float("-inf")

    # Get the dependency graph
    depsgraph = bpy.context.evaluated_depsgraph_get()

    # Iterate through objects in collection
    for obj in collection.objects:
        if obj.type in ("CURVE", "MESH"):
            # Get evaluated version of the object
            eval_obj = obj.evaluated_get(depsgraph)

            # Create mesh from evaluated object
            temp_mesh = eval_obj.to_mesh()

            # Calculate bounds using mesh vertices in world space
            for vert in temp_mesh.vertices:
                world_vert = obj.matrix_world @ vert.co
                # Update bounds
                min_x = min(min_x, world_vert.x)
                min_y = min(min_y, world_vert.y)
                min_z = min(min_z, world_vert.z)
                max_x = max(max_x, world_vert.x)
                max_y = max(max_y, world_vert.y)
                max_z = max(max_z, world_vert.z)

            # Clean up temporary mesh data
            eval_obj.to_mesh_clear()

    # Check if any curves or meshes were found
    if min_x == float("inf"):
        # Return None to indicate no valid objects found
        return None

    return (Vector((min_x, min_y, min_z)), Vector((max_x, max_y, max_z)))


def adjust_camera_to_collection(c, padding_factor=-0.2):
    min_p, max_p = get_curve_collection_bounds2(c)
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



# Replace user with real username
def load_paper_background():
    blend_path = Path(r"C:\Users\%USER%\...\paper_background.blend")
    
    if not blend_path.exists():
        raise FileNotFoundError(f"Blend file not found: {blend_path}")
    
    with bpy.data.libraries.load(str(blend_path), link=False) as (data_from, data_to):
        data_to.objects = data_from.objects

    for obj in data_to.objects:
        if obj is not None:
            bpy.context.collection.objects.link(obj)
