# SPDX-FileCopyrightText: 2011-2023 Blender Foundation
#
# SPDX-License-Identifier: GPL-2.0-or-later

bl_info = {
    "name": "RealFlight FBX export",
    "author": "Bob Long",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "File > Export",
    "description": "FBX export specifically for making custom aircraft for RealFlight",
    "wiki_url": "https://github.com/robertlong13/io_scene_realflight/wiki",
    "tracker_url": "https://github.com/robertlong13/io_scene_realflight/issues",
    "support": 'COMMUNITY',
    "category": "Import-Export",
}


if "bpy" in locals():
    import importlib
    if "export_fbx_bin" in locals():
        importlib.reload(export_fbx_bin)
    if "export_fbx" in locals():
        importlib.reload(export_fbx)


import bpy
from bpy.props import (
    StringProperty,
    BoolProperty,
    FloatProperty,
    EnumProperty,
    CollectionProperty,
)
from bpy_extras.io_utils import (
    ExportHelper,
    orientation_helper,
    path_reference_mode,
    axis_conversion,
    poll_file_object_drop,
)

@orientation_helper(axis_forward='Y', axis_up='Z')
class ExportFBX(bpy.types.Operator, ExportHelper):
    """Write a FBX file"""
    bl_idname = "export_scene.realflight_fbx"
    bl_label = "Export RealFlight FBX"
    bl_options = {'UNDO', 'PRESET'}

    filename_ext = ".fbx"
    filter_glob: StringProperty(default="*.fbx", options={'HIDDEN'})

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.

    use_selection: BoolProperty(
        name="Selected Objects",
        description="Export selected and visible objects only",
        default=False,
    )
    use_visible: BoolProperty(
        name='Visible Objects',
        description='Export visible objects only',
        default=True,
    )
    use_active_collection: BoolProperty(
        name="Active Collection",
        description="Export only objects from the active collection (and its children)",
        default=False,
    )
    collection: StringProperty(
        name="Source Collection",
        description="Export only objects from this collection (and its children)",
        default="",
    )
    global_scale: FloatProperty(
        name="Scale",
        description="Scale all data (Some importers do not support scaled armatures!)",
        min=0.001, max=1000.0,
        soft_min=0.01, soft_max=1000.0,
        default=1.0,
    )
    apply_unit_scale: BoolProperty(
        name="Apply Unit Scale",
        description="Take into account current Blender units settings (if unset, raw Blender Units values are used as-is)",
        default=True,
    )

    use_space_transform: BoolProperty(
        name="Use Space Transform",
        description="Apply global space transform to the object rotations. When disabled "
        "only the axis space is written to the file and all object transforms are left as-is",
        default=True,
    )
    bake_space_transform: BoolProperty(
        name="Apply Transform",
        description="Bake space transform into object data, avoids getting unwanted rotations to objects when "
        "target space is not aligned with Blender's space "
        "(WARNING! experimental option, use at own risk, known to be broken with armatures/animations)",
        default=False,
    )

    object_types: EnumProperty(
        name="Object Types",
        options={'ENUM_FLAG'},
        items=(('EMPTY', "Empty", ""),
               ('CAMERA', "Camera", ""),
               ('LIGHT', "Lamp", ""),
               ('ARMATURE', "Armature", "WARNING: not supported in dupli/group instances"),
               ('MESH', "Mesh", ""),
               ('OTHER', "Other", "Other geometry types, like curve, metaball, etc. (converted to meshes)"),
               ),
        description="Which kind of object to export",
        default={'EMPTY', 'CAMERA', 'MESH', 'OTHER'},
    )

    use_mesh_modifiers: BoolProperty(
        name="Apply Modifiers",
        description="Apply modifiers to mesh objects (except Armature ones) - "
        "WARNING: prevents exporting shape keys",
        default=True,
    )
    use_mesh_modifiers_render: BoolProperty(
        name="Use Modifiers Render Setting",
        description="Use render settings when applying modifiers to mesh objects (DISABLED in Blender 2.8)",
        default=True,
    )
    mesh_smooth_type: EnumProperty(
        name="Smoothing",
        items=(('OFF', "Normals Only", "Export only normals instead of writing edge or face smoothing data"),
               ('FACE', "Face", "Write face smoothing"),
               ('EDGE', "Edge", "Write edge smoothing"),
               ),
        description="Export smoothing information "
        "(prefer 'Normals Only' option if your target importer understand split normals)",
        default='FACE',
    )
    colors_type: EnumProperty(
        name="Vertex Colors",
        items=(('NONE', "None", "Do not export color attributes"),
               ('SRGB', "sRGB", "Export colors in sRGB color space"),
               ('LINEAR', "Linear", "Export colors in linear color space"),
               ),
        description="Export vertex color attributes",
        default='SRGB',
    )
    prioritize_active_color: BoolProperty(
        name="Prioritize Active Color",
        description="Make sure active color will be exported first. Could be important "
        "since some other software can discard other color attributes besides the first one",
        default=False,
    )
    use_subsurf: BoolProperty(
        name="Export Subdivision Surface",
        description="Export the last Catmull-Rom subdivision modifier as FBX subdivision "
        "(does not apply the modifier even if 'Apply Modifiers' is enabled)",
        default=False,
    )
    use_mesh_edges: BoolProperty(
        name="Loose Edges",
        description="Export loose edges (as two-vertices polygons)",
        default=False,
    )
    use_tspace: BoolProperty(
        name="Tangent Space",
        description="Add binormal and tangent vectors, together with normal they form the tangent space "
        "(will only work correctly with tris/quads only meshes!)",
        default=False,
    )
    use_triangles: BoolProperty(
        name="Triangulate Faces",
        description="Convert all faces to triangles",
        default=False,
    )
    use_custom_props: BoolProperty(
        name="Custom Properties",
        description="Export custom properties",
        default=False,
    )
    add_leaf_bones: BoolProperty(
        name="Add Leaf Bones",
        description="Append a final bone to the end of each chain to specify last bone length "
        "(use this when you intend to edit the armature from exported data)",
        default=True  # False for commit!
    )
    primary_bone_axis: EnumProperty(
        name="Primary Bone Axis",
        items=(('X', "X Axis", ""),
               ('Y', "Y Axis", ""),
               ('Z', "Z Axis", ""),
               ('-X', "-X Axis", ""),
               ('-Y', "-Y Axis", ""),
               ('-Z', "-Z Axis", ""),
               ),
        default='Y',
    )
    secondary_bone_axis: EnumProperty(
        name="Secondary Bone Axis",
        items=(('X', "X Axis", ""),
               ('Y', "Y Axis", ""),
               ('Z', "Z Axis", ""),
               ('-X', "-X Axis", ""),
               ('-Y', "-Y Axis", ""),
               ('-Z', "-Z Axis", ""),
               ),
        default='X',
    )
    use_armature_deform_only: BoolProperty(
        name="Only Deform Bones",
        description="Only write deforming bones (and non-deforming ones when they have deforming children)",
        default=False,
    )
    armature_nodetype: EnumProperty(
        name="Armature FBXNode Type",
        items=(('NULL', "Null", "'Null' FBX node, similar to Blender's Empty (default)"),
               ('ROOT', "Root", "'Root' FBX node, supposed to be the root of chains of bones..."),
               ('LIMBNODE', "LimbNode", "'LimbNode' FBX node, a regular joint between two bones..."),
               ),
        description="FBX type of node (object) used to represent Blender's armatures "
        "(use the Null type unless you experience issues with the other app, "
        "as other choices may not import back perfectly into Blender...)",
        default='NULL',
    )
    bake_anim: BoolProperty(
        name="Baked Animation",
        description="Export baked keyframe animation",
        default=False,
    )
    bake_anim_use_all_bones: BoolProperty(
        name="Key All Bones",
        description="Force exporting at least one key of animation for all bones "
        "(needed with some target applications, like UE4)",
        default=True,
    )
    bake_anim_use_nla_strips: BoolProperty(
        name="NLA Strips",
        description="Export each non-muted NLA strip as a separated FBX's AnimStack, if any, "
        "instead of global scene animation",
        default=True,
    )
    bake_anim_use_all_actions: BoolProperty(
        name="All Actions",
        description="Export each action as a separated FBX's AnimStack, instead of global scene animation "
        "(note that animated objects will get all actions compatible with them, "
        "others will get no animation at all)",
        default=True,
    )
    bake_anim_force_startend_keying: BoolProperty(
        name="Force Start/End Keying",
        description="Always add a keyframe at start and end of actions for animated channels",
        default=True,
    )
    bake_anim_step: FloatProperty(
        name="Sampling Rate",
        description="How often to evaluate animated values (in frames)",
        min=0.01, max=100.0,
        soft_min=0.1, soft_max=10.0,
        default=1.0,
    )
    bake_anim_simplify_factor: FloatProperty(
        name="Simplify",
        description="How much to simplify baked values (0.0 to disable, the higher the more simplified)",
        min=0.0, max=100.0,  # No simplification to up to 10% of current magnitude tolerance.
        soft_min=0.0, soft_max=10.0,
        default=1.0,  # default: min slope: 0.005, max frame step: 10.
    )
    path_mode: path_reference_mode
    embed_textures: BoolProperty(
        name="Embed Textures",
        description="Embed textures in FBX binary file (only for \"Copy\" path mode!)",
        default=False,
    )
    batch_mode: EnumProperty(
        name="Batch Mode",
        items=(('OFF', "Off", "Active scene to file"),
               ('SCENE', "Scene", "Each scene as a file"),
               ('COLLECTION', "Collection",
                "Each collection (data-block ones) as a file, does not include content of children collections"),
               ('SCENE_COLLECTION', "Scene Collections",
                "Each collection (including master, non-data-block ones) of each scene as a file, "
                "including content from children collections"),
               ('ACTIVE_SCENE_COLLECTION', "Active Scene Collections",
                "Each collection (including master, non-data-block one) of the active scene as a file, "
                "including content from children collections"),
               ),
    )
    use_batch_own_dir: BoolProperty(
        name="Batch Own Dir",
        description="Create a dir for each exported file",
        default=True,
    )
    use_metadata: BoolProperty(
        name="Use Metadata",
        default=True,
        options={'HIDDEN'},
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        # Are we inside the File browser
        is_file_browser = context.space_data.type == 'FILE_BROWSER'

        export_main(layout, self, is_file_browser)
        export_panel_include(layout, self, is_file_browser)
        export_panel_transform(layout, self)
        export_panel_geometry(layout, self)
        export_panel_armature(layout, self)
        export_panel_animation(layout, self)

    @property
    def check_extension(self):
        return self.batch_mode == 'OFF'

    def execute(self, context):
        from mathutils import Matrix
        if not self.filepath:
            raise Exception("filepath not set")

        global_matrix = (axis_conversion(to_forward=self.axis_forward,
                                         to_up=self.axis_up,
                                         ).to_4x4()
                         if self.use_space_transform else Matrix())

        keywords = self.as_keywords(ignore=("check_existing",
                                            "filter_glob",
                                            "ui_tab",
                                            ))

        keywords["global_matrix"] = global_matrix

        from . import export_fbx_bin
        return export_fbx_bin.save(self, context, **keywords)


def export_main(layout, operator, is_file_browser):
    row = layout.row(align=True)
    row.prop(operator, "path_mode")
    sub = row.row(align=True)
    sub.enabled = (operator.path_mode == 'COPY')
    sub.prop(operator, "embed_textures", text="", icon='PACKAGE' if operator.embed_textures else 'UGLYPACKAGE')
    if is_file_browser:
        row = layout.row(align=True)
        row.prop(operator, "batch_mode")
        sub = row.row(align=True)
        sub.prop(operator, "use_batch_own_dir", text="", icon='NEWFOLDER')


def export_panel_include(layout, operator, is_file_browser):
    header, body = layout.panel("FBX_export_include", default_closed=False)
    header.label(text="Include")
    if body:
        sublayout = body.column(heading="Limit to")
        sublayout.enabled = (operator.batch_mode == 'OFF')
        if is_file_browser:
            sublayout.prop(operator, "use_selection")
            sublayout.prop(operator, "use_visible")
            sublayout.prop(operator, "use_active_collection")

        body.column().prop(operator, "object_types")
        body.prop(operator, "use_custom_props")


def export_panel_transform(layout, operator):
    header, body = layout.panel("FBX_export_transform", default_closed=False)
    header.label(text="Transform")
    if body:
        body.prop(operator, "global_scale")
        body.prop(operator, "apply_scale_options")

        body.prop(operator, "axis_forward")
        body.prop(operator, "axis_up")

        body.prop(operator, "apply_unit_scale")
        body.prop(operator, "use_space_transform")
        row = body.row()
        row.prop(operator, "bake_space_transform")
        row.label(text="", icon='ERROR')


def export_panel_geometry(layout, operator):
    header, body = layout.panel("FBX_export_geometry", default_closed=True)
    header.label(text="Geometry")
    if body:
        body.prop(operator, "mesh_smooth_type")
        body.prop(operator, "use_subsurf")
        body.prop(operator, "use_mesh_modifiers")
        #sub = body.row()
        # sub.enabled = operator.use_mesh_modifiers and False  # disabled in 2.8...
        #sub.prop(operator, "use_mesh_modifiers_render")
        body.prop(operator, "use_mesh_edges")
        body.prop(operator, "use_triangles")
        sub = body.row()
        # ~ sub.enabled = operator.mesh_smooth_type in {'OFF'}
        sub.prop(operator, "use_tspace")
        body.prop(operator, "colors_type")
        body.prop(operator, "prioritize_active_color")


def export_panel_armature(layout, operator):
    header, body = layout.panel("FBX_export_armature", default_closed=True)
    header.label(text="Armature")
    if body:
        body.prop(operator, "primary_bone_axis")
        body.prop(operator, "secondary_bone_axis")
        body.prop(operator, "armature_nodetype")
        body.prop(operator, "use_armature_deform_only")
        body.prop(operator, "add_leaf_bones")


def export_panel_animation(layout, operator):
    header, body = layout.panel("FBX_export_bake_animation", default_closed=True)
    header.use_property_split = False
    header.prop(operator, "bake_anim", text="")
    header.label(text="Animation")
    if body:
        body.enabled = operator.bake_anim
        body.prop(operator, "bake_anim_use_all_bones")
        body.prop(operator, "bake_anim_use_nla_strips")
        body.prop(operator, "bake_anim_use_all_actions")
        body.prop(operator, "bake_anim_force_startend_keying")
        body.prop(operator, "bake_anim_step")
        body.prop(operator, "bake_anim_simplify_factor")


def menu_func_export(self, context):
    self.layout.operator(ExportFBX.bl_idname, text="RealFlight FBX (.fbx)")


classes = (
    ExportFBX,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)

    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
