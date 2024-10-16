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
    "version" : (1, 1, 0),
    "location" : "View3D > Sidebar > bustomize Tab",
    "category" : "Rigging"
}

import bpy
import base64
import json
import zlib
import math
import mathutils
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
        row.prop(settings, "flip_axes", text="", icon="CON_ROTLIKE")

        row = layout.row()
        row.operator("object.bustomize", text="do bustomize (scale)")
        row = layout.row()
        row.operator("object.bustomize_rotpos", text="do bustomize (rot, pos)")
        row = layout.row()
        row.operator("object.bustomize_reset", text="reset armature")

class Bustomize(bpy.types.Operator):
    bl_label = "bustomize"
    bl_idname = "object.bustomize"
    bl_description = "apply c+ scale data to targeted armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.mode != 'OBJECT': return False

        settings: Settings = context.scene.bustomize_settings
        if not settings: return False
        if settings.scale_was_applied: return False
        return True

    def execute(self, context: bpy.types.Context):
        settings: Settings = context.scene.bustomize_settings
        version, cplus_dict = translate_hash(settings.cplus_hash)
        scale_dict = get_bone_values(cplus_dict, 'Scaling')

        if not is_valid(self, context, version, (scale_dict, None, None)):
            return {'CANCELLED'}

        target_armature = settings.target_armature

        # unlink parent bone scaling for ALL bones
        # apply scale to pose bones in bonescale dict
        for posebone in target_armature.pose.bones:
            posebone.bone.inherit_scale = 'NONE'
            scale_vector = scale_dict[posebone.name]
            if scale_vector:
                if settings.flip_axes:
                    posebone.scale = mathutils.Vector((scale_vector['Z'], scale_vector['X'], scale_vector['Y']))
                else:
                    posebone.scale = mathutils.Vector((scale_vector['X'], scale_vector['Y'], scale_vector['Z']))

        settings.scale_was_applied = True
        return {'FINISHED'}

'''
approach:
1. any rot/pos modified bones should each have a DUPE_ bone created in the armature to which its original children are now parented
2. translate original posebone with c+ values (pos_dict)
3. disable rotation inheritance (use_inherit_rotation) and rotate original posebone with c+ values (rot_dict)
'''
class BustomizeRotPos(bpy.types.Operator):
    bl_label = "bustomize_rotpos"
    bl_idname = "object.bustomize_rotpos"
    bl_description = "(experimental) apply c+ rotation+location data to targeted armature"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.mode != 'OBJECT': return False

        settings: Settings = context.scene.bustomize_settings
        if not settings: return False
        if settings.rotpos_was_applied: return False
        return True

    def execute(self, context: bpy.types.Context):
        settings: Settings = context.scene.bustomize_settings
        version, cplus_dict = translate_hash(settings.cplus_hash)
        pos_dict = get_bone_values(cplus_dict, 'Translation')
        rot_dict = get_bone_values(cplus_dict, 'Rotation')
        target_armature = settings.target_armature

        if not is_valid(self, context, version, (None, rot_dict, pos_dict)):
            return {'CANCELLED'}

        # find bones to DUPE
        dupable_posebones = []
        for posebone in target_armature.pose.bones:
            translation = pos_dict[posebone.name]
            rotation = rot_dict[posebone.name]
            if translation or rotation:
                dupable_posebones.append(posebone)

        # create and parent DUPE_ bones
        for posebone in dupable_posebones:
            if not dupe(target_armature, posebone.bone):
                self.report({'WARNING'}, f'could not operate on missing bone: {posebone.name}')

        # translate+rotate posebones
        for posebone in target_armature.pose.bones:
            # disable rotation inheritance from ALL bones
            posebone.bone.use_inherit_rotation = False

            translation = pos_dict[posebone.name]
            rotation = rot_dict[posebone.name]
            if translation:
                if settings.flip_axes:
                    posebone.location += mathutils.Vector((translation['Z'], translation['X'], translation['Y']))
                else:
                    posebone.location += mathutils.Vector((translation['X'], translation['Y'], translation['Z']))

            # apply euler rotations as quat to posebones
            if rotation:
                if settings.flip_axes:
                    rot_radians = mathutils.Vector((
                        math.radians(rotation['Z']),
                        math.radians(rotation['X']),
                        math.radians(rotation['Y'])
                    ))
                else:
                    rot_radians = mathutils.Vector((
                        math.radians(rotation['X']),
                        math.radians(rotation['Y']),
                        math.radians(rotation['Z'])
                    ))
                euler_rot = mathutils.Euler(rot_radians, 'XYZ')
                posebone.rotation_quaternion.rotate(euler_rot)

        settings.rotpos_was_applied = True
        return {'FINISHED'}

class BustomizeReset(bpy.types.Operator):
    bl_label = "bustomize"
    bl_idname = "object.bustomize_reset"
    bl_description = "reset bustomized data"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context: bpy.types.Context) -> bool:
        if context.mode != 'OBJECT': return False

        settings: Settings = context.scene.bustomize_settings
        if not settings: return False
        if not settings.scale_was_applied and not settings.rotpos_was_applied: return False
        return True

    def execute(self, context: bpy.types.Context):
        settings: Settings = context.scene.bustomize_settings
        target_armature = settings.target_armature
        if not is_valid_reset(self, context):
            return {'CANCELLED'}

        dedupable_posebones = []
        for posebone in target_armature.pose.bones:
            if posebone.name.startswith('DUPE_'):
                dedupable_posebones.append(posebone)

        # clean any generated bones
        for posebone in dedupable_posebones:
            if not dedupe(target_armature, posebone.bone):
                self.report({'WARNING'}, f'could not operate on missing bone: {posebone.name}')

        # reset bones' scale, rotation inheritance; local vs global pos bool
        # reset posebone pose/rot/scale data
        for posebone in target_armature.pose.bones:
            posebone.bone.inherit_scale = 'FULL'
            posebone.bone.use_inherit_rotation = True
            posebone.bone.use_local_location = True
            posebone.location = mathutils.Vector((0.0, 0.0, 0.0))
            posebone.rotation_quaternion = mathutils.Quaternion((1.0, 0.0, 0.0, 0.0))
            posebone.scale = mathutils.Vector((1.0, 1.0, 1.0))

        settings.scale_was_applied = False
        settings.rotpos_was_applied = False
        return {'FINISHED'}

class Settings(bpy.types.PropertyGroup):
    target_armature: bpy.props.PointerProperty(name='target armature object', type=bpy.types.Object, poll=lambda self, obj: obj.type == 'ARMATURE') # type: ignore
    cplus_hash: bpy.props.StringProperty(name='clipboard string from c+') # type: ignore
    flip_axes: bpy.props.BoolProperty(default=False, name='flip bone axes (toggle if your scaling applies weird)\ntypically, you should only use this with a problematic devkit skeleton') # type: ignore
    scale_was_applied: bpy.props.BoolProperty(default=False) # type: ignore
    rotpos_was_applied: bpy.props.BoolProperty(default=False) # type: ignore


def translate_hash(the_hasherrrr: str):
    bytes = base64.b64decode(the_hasherrrr)
    bytes_array = bytearray(bytes)

    # TODO: this is 31 when c+ version should be 4. 'version' key in json is correct
    version_byte = bytes_array[0]

    json_str = zlib.decompress(bytes_array, zlib.MAX_WBITS|16).decode('utf-8')
    json_dict = json.loads(json_str[1:])

    version = json_dict['Version']

    return version, json_dict

def get_bone_values(cplus_dict: dict, value_key: str):
    bones = cplus_dict['Bones']
    new_bones = defaultdict(dict)
    for key in bones.keys():
        values = bones[key][value_key]

        # skip pos/rot entries for bones if their x y and z are all 0.0
        if value_key in ['Translation', 'Rotation']:
            if values['X'] == values['Y'] == values['Z'] == 0.0:
                continue

        new_bones[key] = values
    return new_bones

'''
tuple = scale[0], rot[1], pos[2]
'''
def is_valid(self, context, ver, tuple):
    if ver != 4:
        self.report({'ERROR'}, 'C+ string version {ver} incompatible; bustomize expects 4')
        return False

    settings: Settings = context.scene.bustomize_settings

    # validate target armature contents
    # only apply scaling to pose bones when we can safely revert
    target_armature = settings.target_armature
    if not target_armature:
        self.report({'ERROR'}, 'Target armature DNE')
        return False
    if not target_armature.type == "ARMATURE":
        self.report({'ERROR'}, 'Did not select a valid armature object')
        return False

    # scale checks
    scale = tuple[0]
    if scale:
        target_bone_names = []
        for bone in target_armature.data.bones:
            if bone.inherit_scale != "FULL":
                self.report({'ERROR'}, f'Armature contains bone {bone.name} which does not inherit parent bone scaling')
                return False
            target_bone_names.append(bone.name)

        # TODO: Armature contains bone j_asi_b_l with unexpected scale: <Vector (1.0000, 1.0000, 1.0000)>
        # check for scale that's 'close enough' to 1.0

        missing_bones = []
        for bonescale_name in scale.keys():
            if bonescale_name not in target_bone_names:
                missing_bones.append(bonescale_name)
        if len(missing_bones) == len(scale.keys()):
            self.report({'ERROR'}, f'Armature contains no matching bones to scale!')
            return False
        elif len(missing_bones) > 1:
            self.report({'WARNING'}, f'Skipping missing bones: {", ".join(missing_bones)}')

    # rotpos checks
    rotation = tuple[1]
    position = tuple[2]
    if rotation or position:
        if not target_armature.visible_get():
            self.report({'ERROR'}, f'Armature is not visible in viewport (may cause issues, unhide to resolve)')
            return False

    return True

def is_valid_reset(self, context):
    settings: Settings = context.scene.bustomize_settings

    # validate target armature
    target_armature = settings.target_armature
    if not target_armature:
        self.report({'ERROR'}, 'Target armature DNE')
        return False
    if not target_armature.type == "ARMATURE":
        self.report({'ERROR'}, 'Did not select a valid armature object')
        return False

    return True

def dedupe(armature, dupe_bone):
    # temp enter edit mode to nuke dupe bone
    bpy.ops.object.editmode_toggle()

    # parent bones back to original to cleanup armature
    try:
        dupe_edit_bone = armature.data.edit_bones[dupe_bone.name]
        edit_bone = armature.data.edit_bones[dupe_bone.name[5:]]
    except Exception as e:
        bpy.ops.object.editmode_toggle()
        return False

    for child in dupe_edit_bone.children:
        child.parent = edit_bone

    armature.data.edit_bones.remove(dupe_edit_bone)

    bpy.ops.object.editmode_toggle()
    return True

def dupe(armature, bone):
    # temp enter edit mode to create dupe bone
    bpy.ops.object.editmode_toggle()

    try:
        edit_bone = armature.data.edit_bones[bone.name]
    except Exception as e:
        bpy.ops.object.editmode_toggle()
        return False

    dupe_edit_bone = armature.data.edit_bones.new(f'DUPE_{bone.name}')
    dupe_edit_bone.matrix = edit_bone.matrix.copy()
    dupe_edit_bone.length = edit_bone.length
    dupe_edit_bone.parent = edit_bone.parent

    # parent bones to new dupe to prevent inheriting translation edit
    for child in edit_bone.children:
        child.parent = dupe_edit_bone

    bpy.ops.object.editmode_toggle()
    return True


def register():
    bpy.utils.register_class(Bustomize)
    bpy.utils.register_class(BustomizeRotPos)
    bpy.utils.register_class(BustomizeReset)
    bpy.utils.register_class(BustomizePanel)
    bpy.utils.register_class(Settings)
    bpy.types.Scene.bustomize_settings = bpy.props.PointerProperty(type=Settings)

def unregister():
    bpy.utils.unregister_class(Bustomize)
    bpy.utils.unregister_class(BustomizeRotPos)
    bpy.utils.unregister_class(BustomizeReset)
    bpy.utils.unregister_class(BustomizePanel)
    bpy.utils.unregister_class(Settings)
    del bpy.types.Scene.bustomize_settings

if __name__ == "__main__":
    register()
