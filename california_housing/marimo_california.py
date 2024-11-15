import marimo

__generated_with = "0.9.19"
app = marimo.App()


@app.cell
def __():
    #run with
    #cd california_housing
    #uv run marimo edit marimo_california.py 
    import marimo as mo
    import numpy as np
    import polars as pl
    import quak
    import bpy

    blend_file_path = "housing_data_igor.blend"
    bpy.ops.wm.open_mainfile(filepath=blend_file_path)

    bpy.context.scene.render.engine = "BLENDER_EEVEE_NEXT"
    bpy.context.scene.render.resolution_x = 800
    bpy.context.scene.render.resolution_y = 500

    df = pl.read_csv("a_df.csv")
    reference_frame = pl.read_csv("b_reference_frame.csv")

    vertices = [(row["longitude_normalized"], row["latitude_normalized"], 0) for row in reference_frame.iter_rows(named=True)]

    mesh = bpy.data.meshes.new("NormalizedMesh")
    obj = bpy.data.objects.new("CaliforninaNormalizedObject", mesh)
    bpy.context.collection.objects.link(obj)

    mesh.from_pydata(vertices, [], [])
    mesh.update()
    obj.modifiers.new(name="GeometryNodes", type='NODES').node_group = bpy.data.node_groups["geo_house"]
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    reference_frame.head()

    def render_result():

        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(filepath="img.png")
        return mo.image(src="img.png")
    return (
        blend_file_path,
        bpy,
        df,
        mesh,
        mo,
        np,
        obj,
        pl,
        quak,
        reference_frame,
        render_result,
        vertices,
    )


@app.cell
def __(df, mo, quak):
    widget = mo.ui.anywidget(quak.Widget(df))
    widget
    return (widget,)


@app.cell
def __(np, obj, pl, reference_frame, render_result, widget):
    widget_df = widget.data().pl()

    plotting_frame = reference_frame.with_columns(
        pl.lit(0).alias("custom_plotting")
    ).join(
        widget_df.select(["short_id", "median_house_value"]), 
        on="short_id", 
        how="left"
    ).with_columns(
        pl.when(pl.col("median_house_value").is_not_null())
        .then(pl.col("median_house_value"))
        .otherwise(pl.col("custom_plotting"))
        .alias("custom_plotting")
    ).select(["short_id", "custom_plotting"])

    custom_plotting_list = plotting_frame["custom_plotting"].to_list()
    normalized_values = list(np.interp(custom_plotting_list, 
                                       (min(custom_plotting_list), max(custom_plotting_list)), 
                                       (0.1, 3)))

    attr_name = 'median_house_value'
    attr = obj.data.attributes.get(attr_name) or obj.data.attributes.new(
        name=attr_name,
        type='FLOAT',
        domain='POINT'
    )
    attr.data.foreach_set('value', normalized_values)
    obj.data.update()

    render_result()
    return (
        attr,
        attr_name,
        custom_plotting_list,
        normalized_values,
        plotting_frame,
        widget_df,
    )


@app.cell
def __():
    return


if __name__ == "__main__":
    app.run()
