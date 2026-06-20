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
#  along with this program; if not, see < https://www.gnu.org/licenses/ >.
#
# ##### END GPL LICENSE BLOCK #####

# Copyright (c) 2025 Roni Raihan

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import bpy
import os
from bpy.props import (
    FloatProperty,
    EnumProperty,
    IntProperty,
    BoolProperty,
    PointerProperty
)


def mif_lokasi_update(self, context):
    self.cek_refres = True

def mi_lokasi_update(self, context):
    if self.mi_lokasi:
        path_lengkap = bpy.path.abspath(self.mi_lokasi)
        aset = os.path.join(path_lengkap, "Data/Minecraft")
        if os.path.isdir(aset):
            if any(os.scandir(aset)):
                self.mi_software_status = True
            else:
                self.mi_software_status = False
        else:
            self.mi_software_status = False
    else:
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        if addon_prefs.mi_lokasi:
            self.mi_lokasi = addon_prefs.mi_lokasi
            
def lihat_expand_update(self, context):
    sp = context.scene.miablen_projects[context.scene.miablen_pilih_projects]
    
    # Cari index item ini lalu set sebagai yang terpilih
    for i, tm in enumerate(sp.mif_timeline):
        if tm == self:
            sp.mif_timeline_pilih = i
            break
        
    update_tampil(sp)
    
def update_tampil(mf):
    children_map = {}
    for tm in mf.mif_timeline:
        children_map.setdefault(tm.parent_id, []).append(tm)

    def cascade(node, tampil):
        node.lihat_tampil = tampil
        for child in children_map.get(node.id, []):
            cascade(child, tampil and node.lihat_expand)

    for root in children_map.get("root", []):
        cascade(root, True)
        
def timeline_pilih_update(self, context):
    if self.mif_timeline_pilih > len(self.mif_timeline) - 1:
        return
    
    if context.mode != 'OBJECT':
        return
    
    tm = self.mif_timeline[self.mif_timeline_pilih]
    
    if not tm.target_object:
        return
    
    obj = context.scene.objects.get(tm.target_object.name)
    if not obj:
        return
    
    try:
        # Deselect semua lalu select target
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
    except zipfile.BadZipFile as e:
        print(f"{e}")
        return

#~~~~~~~~~~~~~~~~~~~~ key data
class key_data(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', default='')
    nilai: bpy.props.StringProperty(name='Value', default='')
    
class key_set(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', default='')
    frame: bpy.props.FloatProperty(name='frame', default=0.0)
    key_data: bpy.props.CollectionProperty(type=key_data)
    
#~~~~~~~~~~~~~~~~~~~~ template
class part_data(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Part Name', default='')
    parent: bpy.props.StringProperty(name='Parent', default='')
    loc_x: bpy.props.FloatProperty(name='Location X', default=0.0)
    loc_y: bpy.props.FloatProperty(name='Location Y', default=0.0)
    loc_z: bpy.props.FloatProperty(name='Location Z', default=0.0)
    
    rot_x: bpy.props.FloatProperty(name='Rotation X', default=0.0)
    rot_y: bpy.props.FloatProperty(name='Rotation Y', default=0.0)
    rot_z: bpy.props.FloatProperty(name='Rotation Z', default=0.0)
    
    siz_x: bpy.props.FloatProperty(name='Scale X', default=1.0)
    siz_y: bpy.props.FloatProperty(name='Scale Y', default=1.0)
    siz_z: bpy.props.FloatProperty(name='Scale Z', default=1.0)
    
    bend: bpy.props.BoolProperty(name='Bend', default=False)
    offset_bend: bpy.props.FloatProperty(name='Offset', default=0.0)
    type_bend: bpy.props.StringProperty(name='Type Bend', default='')
    
class state_data(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', default='')
    nilai: bpy.props.StringProperty(name='Value', default='')
    
class mf_template(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', default='')
    id: bpy.props.StringProperty(name='ID', default='')
    type: bpy.props.StringProperty(name='Type', default='')
    file_name: bpy.props.StringProperty(name='File', default='')
    
    state: bpy.props.CollectionProperty(type=state_data)
    part_name: bpy.props.StringProperty(name='Name Part', default='')
    
    model_part: bpy.props.CollectionProperty(type=part_data)
    
#~~~~~~~~~~~~~~~~~~~~ temline
class mf_timeline(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name', default='')
    id: bpy.props.StringProperty(name='ID', default='')
    type: bpy.props.StringProperty(name='Type', default='')
    usang: bpy.props.BoolProperty(name='Usang', default=False)
    parent_id: bpy.props.StringProperty(name='Parent', default='')
    template_id: bpy.props.StringProperty(name='Template', default='')
    
    lihat_level: bpy.props.IntProperty(default=0)
    lihat_rank: bpy.props.IntProperty(default=0)
    lihat_tampil: bpy.props.BoolProperty(default=True)
    lihat_expand: bpy.props.BoolProperty(default=True, update=lihat_expand_update)
    
    target_object: bpy.props.PointerProperty(type=bpy.types.Object, name='Target', description='Data written to')
    
    target_bend_object: bpy.props.PointerProperty(type=bpy.types.Object, name='Target Bend', description='Data Bend written to')
    bend_part: bpy.props.BoolProperty(name='Bend', default=False)
    offset_bend: bpy.props.FloatProperty(name='Offset', default=0.0)
    type_bend: bpy.props.StringProperty(name='Type Bend', default='')
    part_name: bpy.props.StringProperty(name='Name Part', default='')
    part_tunggal: bpy.props.BoolProperty(name='Tunggal', default=False)
    
    key_set: bpy.props.CollectionProperty(type=key_set)
    key_set_pilih: bpy.props.IntProperty(name='Pilih temline', default=0, min=0)
    
    loc_x: bpy.props.FloatProperty(name='Location X', default=0.0)
    loc_y: bpy.props.FloatProperty(name='Location y', default=0.0)
    loc_z: bpy.props.FloatProperty(name='Location z', default=0.0)
    
    loc_ikut_parent: bpy.props.BoolProperty(name='Follow Parent Location', default=True)
    rot_ikut_parent: bpy.props.BoolProperty(name='Follow Parent Rotation', default=True)
    scale_ikut_parent: bpy.props.BoolProperty(name='Follow Parent Scale', default=True)
    
    rot_point_ikut_parent: bpy.props.BoolProperty(name='Follow Parent Scale', default=False)
    
    invers_loc_x: bpy.props.FloatProperty(name='Invers Location X', default=0.0)
    invers_loc_y: bpy.props.FloatProperty(name='Invers Location Y', default=0.0)
    invers_loc_z: bpy.props.FloatProperty(name='Invers Location Z', default=0.0)
    
    invers_rot_x: bpy.props.FloatProperty(name='Invers Rotation X', default=0.0)
    invers_rot_y: bpy.props.FloatProperty(name='Invers Rotation Y', default=0.0)
    invers_rot_z: bpy.props.FloatProperty(name='Invers Rotation Z', default=0.0)
    
    invers_siz_x: bpy.props.FloatProperty(name='Invers Scale X', default=1.0)
    invers_siz_y: bpy.props.FloatProperty(name='Invers Scale Y', default=1.0)
    invers_siz_z: bpy.props.FloatProperty(name='Invers Scale Z', default=1.0)

#~~~~~~~~~~~~~~~~~~~~~~ itrm project
class miablen_projects(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name='Name project', default='')
    lokasi: bpy.props.StringProperty(name='File project', default='', update=mif_lokasi_update)
    cek_refres: bpy.props.BoolProperty(name='Cek', default=False)
    mi_lokasi: bpy.props.StringProperty(name='Mine-Imator', default='', update = mi_lokasi_update)
    mi_software_status: bpy.props.BoolProperty(name='Usang', default=False)
    
    mif_nama: bpy.props.StringProperty(name='Name project', default='-')
    mif_author: bpy.props.StringProperty(name='Author', default='-')
    mif_deskripsi: bpy.props.StringProperty(name='Description', default='-')
    mif_format: bpy.props.FloatProperty(name='Data format', default=0.0)
    mif_versi: bpy.props.StringProperty(name='Project Version', default='')
    
    mif_timeline: bpy.props.CollectionProperty(type=mf_timeline)
    mif_timeline_pilih: bpy.props.IntProperty(name='Pilih temline', default=0, min=0, update=timeline_pilih_update)
    
    mif_template: bpy.props.CollectionProperty(type=mf_template)
    mif_template_pilih: bpy.props.IntProperty(name='Pilih template', default=0, min=0)
    
    
classes = [
    key_data,
    key_set,
    part_data,
    state_data,
    mf_template,
    mf_timeline,
    miablen_projects
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    bpy.types.Scene.miablen_projects = bpy.props.CollectionProperty(type=miablen_projects)
    bpy.types.Scene.miablen_pilih_projects = bpy.props.IntProperty(name='Pilih project', default=0, min=0)
    

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()