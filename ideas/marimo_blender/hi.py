import marimo

__generated_with = "0.9.10"
app = marimo.App(width="medium")


@app.cell
def __():
    import bpy
    import bpy
    from IPython.display import display, Image

    def fresh_scene(keep_cube=False):
        # Deselect all objects
        bpy.ops.object.select_all(action='DESELECT')

        # Select all objects except cameras and optionally the default cube
        for obj in bpy.context.scene.objects:
            if obj.type == 'CAMERA':
                obj.select_set(False)
            elif obj.name == 'Cube' and keep_cube:
                obj.select_set(False)
            else:
                obj.select_set(True)

        bpy.ops.object.delete()

        # Add light
        bpy.ops.object.light_add(type='SUN')
        sun = bpy.context.object

        sun.location = (0, 0, 0)
        from math import radians
        sun.rotation_euler = (radians(204), radians(-133), radians(-67))
        sun.data.energy = 5  


    def render_result():
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(filepath="img.png")
        return mo.image("img.png")


    bpy.context.scene.render.resolution_x = 500
    bpy.context.scene.render.resolution_y = 200

    import marimo as mo
    return Image, bpy, display, fresh_scene, mo, render_result


@app.cell
def __(bpy, fresh_scene, render_result):
    fresh_scene()
    bpy.ops.mesh.primitive_torus_add(major_radius=2, minor_radius=0.3, location=(0,0, 0))
    render_result()
    return


@app.cell
def __(bpy, fresh_scene, render_result):
    fresh_scene()
    bpy.ops.mesh.primitive_ico_sphere_add(radius=1, location=(0, 0, 0)) 
    render_result()
    return


@app.cell
def __(bpy, fresh_scene, render_result):
    fresh_scene()
    bpy.ops.object.text_add(location=(-4, 0, 0))
    bpy.context.object.data.body = "Hello 😄"
    bpy.context.object.scale = (2, 2, 2)
    render_result()
    return


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
