# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

bl_info = {
    "name": "VRML2 converted for Blender 3.0",
    "author": "Campbell Barton",
    "blender": (3, 0, 0),
    "location": "File > Export",
    "description": "Exports mesh objects to VRML2, supporting vertex and material colors",
    "warning": "",
    "wiki_url": "http://wiki.blender.org/index.php/Extensions:2.6/Py/"
                "Scripts/Import-Export/VRML2",
    "support": 'OFFICIAL',
    "category": "Import-Export"}

if "bpy" in locals():
    import importlib
    if "export_vrml2" in locals():
        importlib.reload(export_vrml2)


import os
import bpy
from bpy.props import (
        CollectionProperty,
        StringProperty,
        BoolProperty,
        EnumProperty,
        FloatProperty,
        )
from bpy_extras.io_utils import (
        ExportHelper,
        orientation_helper,
        axis_conversion,
        path_reference_mode,
        )


#ExportVRMLOrientationHelper = orientation_helper("ExportVRMLOrientationHelper", axis_forward='Y', axis_up='Z')

@orientation_helper(axis_forward='Y', axis_up='Z')
class ExportVRML(bpy.types.Operator, ExportHelper):
    """Export mesh objects as a VRML2, colors and texture coordinates"""
    bl_idname = "export_scene.vrml2"
    bl_label = "Export VRML2"

    filename_ext = ".wrl"
    filter_glob: StringProperty(default="*.wrl", options={'HIDDEN'})

    use_selection: BoolProperty(
            name="Selection Only",
            description="Export selected objects only",
            default=True,
            )
    use_mesh_modifiers: BoolProperty(
            name="Apply Modifiers",
            description="Apply Modifiers to the exported mesh",
            default=True,
            )
    use_color: BoolProperty(
            name="Vertex Colors",
            description="Export the active vertex color layer",
            default=False,
            )
    color_type: EnumProperty(
            name='Color',
            items=(
            ('VERTEX', "Vertex Color", ""),
            ('MATERIAL', "Material Color", "")),
            )
    use_uv: BoolProperty(
            name="Texture/UVs",
            description="Export the active texture and UV coords",
            default=False,
            )

    global_scale: FloatProperty(
            name="Scale",
            min=0.01, max=1000.0,
            default=1.0,
            )

    path_mode: path_reference_mode

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return (obj is not None) and obj.type == 'MESH'

    def execute(self, context):
        from . import export_vrml2
        from mathutils import Matrix

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "global_scale",
                                            "check_existing",
                                            "filter_glob",
                                            ))

        global_matrix = axis_conversion(to_forward=self.axis_forward,
                                        to_up=self.axis_up,
                                        ).to_4x4() * Matrix.Scale(self.global_scale, 4)
        keywords["global_matrix"] = global_matrix

        filepath = self.filepath
        filepath = bpy.path.ensure_ext(filepath, self.filename_ext)

        return export_vrml2.save(self, context, **keywords)

    def draw(self, context):
        layout = self.layout

        layout.prop(self, "use_selection")
        layout.prop(self, "use_mesh_modifiers")

        row = layout.row()
        row.prop(self, "use_uv")
        row.prop(self, "use_color")
        row = layout.row()
        row.active = self.use_color
        row.prop(self, "color_type")
        layout.prop(self, "axis_forward")
        layout.prop(self, "axis_up")
        layout.prop(self, "global_scale")
        layout.prop(self, "path_mode")


def menu_func_export(self, context):
    self.layout.operator(ExportVRML.bl_idname, text="VRML2 (.wrl)")

classes = (
        ExportVRML,
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
