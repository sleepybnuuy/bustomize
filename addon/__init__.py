# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "bustomize",
    "author" : "sleepybnuuy",
    "description" : "customize+ to blender add-on",
    "blender" : (4, 0, 0),
    "version" : (0, 0, 1),
    "location" : "View3D > Sidebar > bustomize Tab",
    "category" : "Rigging"
}

import bpy
import base64
import json
import zlib
from collections import defaultdict

class BustomizePanel(bpy.types.Panel):
    bl_label = "bustomize"
    bl_idname = "OBJECT_PT_bustomize_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "bustomize"
    bl_options = set()

    def draw(self, context):
        layout = self.layout
        settings = context.scene.bustomize_settings

        row = layout.row()
        row.label(text='Target Armature')
        row = row.row(align=True)
        row.prop(settings, "target_armature", text="")

        row = layout.row()
        row.label(text='Customize+ String')
        row = row.row(align=True)
        row.prop(settings, "cplus_hash", text="", icon="PASTEDOWN")

        row = layout.row()
        row.operator("object.bustomize", text="do bustomize")
        row = layout.row()
        row.operator("object.bustomize", text="reset armature scale")

class Bustomize(bpy.types.Operator):
    bl_label = "bustomize"
    bl_idname = "object.bustomize"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.mode != 'OBJECT': return False

        settings: Settings = context.scene.bustomize_settings
        if not settings: return False
        return True

    def execute(self, context: bpy.types.Context):
        settings: Settings = context.scene.bustomize_settings
        ver, cplus_dict = translate_hash(settings.cplus_hash)
        print(f'c+ version: {ver}')
        bonescale_dict = get_bone_scaling(cplus_dict)
        print(f'bonescale dict: {bonescale_dict}')
        return {'FINISHED'}

class BustomizeReset(bpy.types.Operator):
    # STUB
    # should overwrite all scaling in target armature to 1.1.1
    # should reset Inherit Scale on all bones in armature to Full
    bl_label = "bustomize"
    bl_idname = "object.bustomize_reset"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.mode != 'OBJECT': return False

        settings: Settings = context.scene.bustomize_settings
        if not settings: return False
        return True

    def execute(self, context: bpy.types.Context):
        settings: Settings = context.scene.bustomize_settings
        return {'FINISHED'}

class Settings(bpy.types.PropertyGroup):
    target_armature: bpy.props.PointerProperty(name='target', type=bpy.types.Armature) # type: ignore
    cplus_hash: bpy.props.StringProperty(name='clipboard base64 str from c+') # type: ignore

def translate_hash(the_hasherrrr: str):
    bytes = base64.b64decode(the_hasherrrr)
    bytes_array = bytearray(bytes)
    version = bytes_array[0]

    json_str = zlib.decompress(bytes_array, zlib.MAX_WBITS|16).decode('utf-8')
    json_dict = json.loads(json_str[1:])

    return version, json_dict

def get_bone_scaling(cplus_dict: dict):
    bones = cplus_dict['Bones']
    new_bones = defaultdict(dict)
    for key in bones.keys():
        new_bones[key] = bones[key]['Scaling']
    return new_bones

def register():
    bpy.utils.register_class(Bustomize)
    bpy.utils.register_class(BustomizePanel)
    bpy.utils.register_class(Settings)
    bpy.types.Scene.bustomize_settings = bpy.props.PointerProperty(type=Settings)

def unregister():
    bpy.utils.unregister_class(Bustomize)
    bpy.utils.unregister_class(BustomizePanel)
    bpy.utils.unregister_class(Settings)
    del bpy.types.Scene.bustomize_settings

if __name__ == "__main__":
    register()