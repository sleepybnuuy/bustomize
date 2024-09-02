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
        pass

class BustomizePanel(bpy.types.Panel):
    bl_label = "bustomize"
    bl_idname = "object.bustomize.panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "bustomize"
    bl_options = set()

    def draw(self, context):
        layout = self.layout
        settings = context.scene.bustomize_settings

        row = layout.row(align=True)
        row.prop(settings, "target_armature")

class Settings(bpy.types.PropertyGroup):
    target_armature: bpy.props.PointerProperty(name='target', type=bpy.types.Armature) # type: ignore

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