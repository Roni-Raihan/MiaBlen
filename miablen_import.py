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

#Spesial Thanks to:
#  Tcalya
#  Raffsimation
#  Pebry

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import bpy
import os
import json
import math
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


#~~~~~~~~~~~~~~~~~~~
def baca_data(data, mf, baru = False):
    preferences = bpy.context.preferences
    addon_prefs = preferences.addons["MiaBlen"].preferences
    #addon_prefs = preferences.addons[__package__].preferences
    mf.mi_lokasi = addon_prefs.mi_lokasi
    
    mf.mif_format = data.get("format", 0)
    mf.mif_versi = data.get("created_in", "-")
    
    #baca data project
    data_project = data.get("project", None)
    if data_project:
        mf.mif_nama = data_project.get("name","-")
        mf.mif_author = data_project.get("author","-")
        mf.mif_deskripsi = data_project.get("description","-")
        
    #bersihin temline kalo load baru
    if baru and len(mf.mif_timeline) > 0:
        mf.mif_timeline.clear()
    elif not baru and len(mf.mif_timeline) > 0:
        for mf_tml in mf.mif_timeline:
            mf_tml.parent_id = "root"
            mf_tml.usang = True
            
    #cari nama di resources
    rc_mapping = {}
    data_resources = data.get("resources", None)
    if data_resources:
        for rc in data_resources:
            rc_mapping[rc.get("id", "")] = rc.get("filename", "").rsplit('.', 1)[0]
            
    #reset template
    if len(mf.mif_template) > 0:
        mf.mif_template.clear()
        
    #cari nama di templates
    tp_mapping = {}
    data_templates = data.get("templates", None)
    if data_templates:
        for tp in data_templates:
            name = cari_nama_template(tp, rc_mapping)
            tp_mapping[tp.get("id", "")] = name
            
            #simpan template berdasarkan type
            type = tp.get("type", "")
            if type in ('char', 'spblock'):
                mf_tp = mf.mif_template.add()
                mf_tp.name = name
                mf_tp.id = tp.get("id", "")
                mf_tp.type = type
                
                model_data = tp.get("model", None)
                if model_data:
                    state_data = model_data.get("state", None)
                    if state_data:
                        for k, v in state_data.items():
                            mf_st = mf_tp.state.add()
                            mf_st.name = f"{k}"
                            mf_st.nilai = f"{v}"
                
            elif type == 'model':
                mf_tp = mf.mif_template.add()
                mf_tp.name = name
                mf_tp.id = tp.get("id", "")
                mf_tp.type = type
                mf_tp.file_name = name+".mimodel"
                
            elif type == 'bodypart':
                mf_tp = mf.mif_template.add()
                mf_tp.name = name
                mf_tp.id = tp.get("id", "")
                mf_tp.type = type
                model_data = tp.get("model", None)
                if model_data:
                    mf_tp.part_name = model_data.get("part_name", "")
                    state_data = model_data.get("state", None)
                    if state_data:
                        for k, v in state_data.items():
                            mf_st = mf_tp.state.add()
                            mf_st.name = f"{k}"
                            mf_st.nilai = f"{v}"
                
    #mulai baca timeline
    data_timeline = data.get("timelines", None)
    if data_timeline:
        for tm in data_timeline:
            id = tm.get("id", "")
            type = tm.get("type", "")
            
            #cek apakah sudah ada di property
            if not baru and len(mf.mif_timeline) > 0:
                mf_tm = None
                for t in mf.mif_timeline:
                    if id == t.id:
                        mf_tm = t
                        break
                if not mf_tm:
                    mf_tm = mf.mif_timeline.add()
            else:
                mf_tm = mf.mif_timeline.add()
            
            #isi data
            mf_tm.id = id
            mf_tm.type = type
            
            #Nama
            if type == "bodypart": 
                name = tm.get("name", "")
                if name == "":
                    name = tm.get("model_part_name", type)
                mf_tm.name = name
                mf_tm.part_name = tm.get("model_part_name", type)
            else:
                name = tm.get("name", "")
                if name == "":
                    name = tp_mapping.get(tm.get("temp", ""), type)
                
                mf_tm.name = name
                mf_tm.bend_part = False #hapus bend
                mf_tm.target_bend_object = None
                mf_tm.part_name = ""
                
            #bagian lainnya
            mf_tm.parent_id = tm.get("parent", "root")
            mf_tm.template_id = tm.get("temp", "")
            mf_tm.part_tunggal = False
            mf_tm.usang = False
            
            inhe = tm.get("inherit", None)
            if inhe:
                mf_tm.loc_ikut_parent = inhe.get("position",True)
                mf_tm.rot_ikut_parent = inhe.get("rotation",True)
                mf_tm.scale_ikut_parent = inhe.get("scale",True)
                mf_tm.rot_point_ikut_parent = inhe.get("rot_point",False)
            
            #Blender MI JSON blender 1 = 16 Mineimator
            #   x    z   y
            #   y    x   x
            #   z    y   z
            
            origin_loc = tm.get("default_values", None)
            if origin_loc:
                loc_def_x = float(origin_loc.get("POS_Y", 0))
                loc_def_y = float(origin_loc.get("POS_X", 0))
                loc_def_z = float(origin_loc.get("POS_Z", 0))
            else:
                loc_def_x = 0
                loc_def_y = 0
                loc_def_z = 0
                
            mf_tm.loc_x = loc_def_x / 16
            mf_tm.loc_y = loc_def_y / 16
            mf_tm.loc_z = loc_def_z / 16
                
            if len(mf_tm.key_set) > 0:
                mf_tm.key_set.clear()
            
            key_json = tm.get("keyframes", None)
            if key_json:
                for f in sorted(key_json.keys(), key=float):
                    item_v = key_json[f]
                    key_set = mf_tm.key_set.add()
                    key_set.name = f"{f}"
                    key_set.frame = float(f)
                    
                    for k, v in item_v.items():
                        key_data = key_set.key_data.add()
                        key_data.name = f"{k}"
                        key_data.nilai = f"{v}"
    
def cari_nama_template(tm, rc_mapping):
    nama = tm.get("name", "")
    if nama:
        return nama

    tipe = tm.get("type", "")

    if tipe == "model":
        return rc_mapping.get(tm.get("model", ""), "")

    elif tipe == "item":
        return tm.get("item", {}).get("name", "")

    elif tipe == "block":
        return tm.get("block", {}).get("name", "")

    elif tipe in ("char", "bodypart", "spblock"):
        nama_model = tm.get("model", {}).get("name", "")
        return nama_model

    else:
        return tipe
    
def urut_hirarki(mf):
    children_map = {}
    for tm in mf.mif_timeline:
        children_map.setdefault(tm.parent_id, []).append(tm)

    urutan = []
    def dfs(node, level):
        node.lihat_level = level
        urutan.append(node)
        for child in children_map.get(node.id, []):
            dfs(child, level + 1)

    for root in children_map.get("root", []):
        dfs(root, 0)

    for i, node in enumerate(urutan):
        node.lihat_rank = i
    
def load_data(fpath):
    path_lengkap = bpy.path.abspath(fpath)
    try:
        with open(path_lengkap, "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return (data, False)
    except Exception as e:
        return (e, True)

#~~~~ Add path ke file mi
class add_miafile(Operator, ImportHelper):
    """Add path to list"""
    bl_idname = "scene.import_mif"
    bl_label = "Add"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".miproject"

    filter_glob: StringProperty(
        default="*.miproject",
        options={'HIDDEN'},
        maxlen=255
    )

    penyesuai_path: BoolProperty(
        name="Relative path",
        description="Relative path",
        default=True
    )

    def execute(self, context):
        letak = self.filepath
        scene = context.scene
        
        af = scene.miablen_projects.add()
        af.name = bpy.path.basename(letak)
        if self.penyesuai_path:
            af.lokasi = bpy.path.relpath(letak)
        else:
            af.lokasi = bpy.path.abspath(letak)
        scene.miablen_pilih_projects = len(scene.miablen_projects)-1
            
        data = load_data(letak)
        if data[1]:
            af.cek_refres = True
            self.report({'ERROR'}, f"Can't load: {data[0]}")
            return {'CANCELLED'}
        
        baca_data(data[0], af, True)
        urut_hirarki(af)
        af.cek_refres = False
        return {'FINISHED'}
    
#~~~~ Ubah path ke file mi
class reload_miafile(Operator):
    """Reload"""
    bl_idname = "scene.reload_mif"
    bl_label = "Reload"
    bl_options = {'REGISTER', 'UNDO'}
    
    reset_tm: BoolProperty(
        name="Reset Timeline Data",
        description="Reset Timeline Data",
        default=False
    )
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        scene = context.scene
        sp = scene.miablen_projects[scene.miablen_pilih_projects]
        
        data = load_data(sp.lokasi)
        if data[1]:
            sp.cek_refres = True
            self.report({'ERROR'}, f"Can't load: {data[0]}")
            return {'CANCELLED'}
        
        baca_data(data[0], sp, self.reset_tm)
        urut_hirarki(sp)
        sp.cek_refres = False
        return {'FINISHED'}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Will reload all data", icon = 'ERROR')
        layout.prop(self, "reset_tm")
    
#~~~~ Ubah path ke file mi
class ubah_miafile(Operator, ImportHelper):
    """Change path to list"""
    bl_idname = "scene.change_mif"
    bl_label = "Change"
    bl_options = {'REGISTER', 'UNDO'}

    filename_ext = ".miproject"

    filter_glob: StringProperty(
        default="*.miproject",
        options={'HIDDEN'},
        maxlen=255
    )

    penyesuai_path: BoolProperty(
        name="Relative path",
        description="Relative path",
        default=True
    )

    def execute(self, context):
        letak = self.filepath
        scene = context.scene
        sp = scene.miablen_projects[scene.miablen_pilih_projects]
        if self.penyesuai_path:
            sp.lokasi = bpy.path.relpath(letak)
        else:
            sp.lokasi = bpy.path.abspath(letak)
        sp.cek_refres = True
        return {'FINISHED'}

class pilih_folder_mineimator_pengaturan(Operator):
    """Set Mine-Imator installation folder"""
    bl_idname = "scene.pilih_folder_mineimator_pengaturan"
    bl_label = "Set Folder Mine-Imator"
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(
        name="Folder",
        subtype='DIR_PATH'
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__package__].preferences
        addon_prefs.mi_lokasi = self.directory
        return {'FINISHED'}
    
class pilih_folder_mineimator_mif(Operator):
    """Set Mine-Imator installation folder"""
    bl_idname = "scene.pilih_folder_mineimator_mif"
    bl_label = "Set Folder Mine-Imator"
    bl_options = {'REGISTER', 'UNDO'}

    directory: StringProperty(
        name="Folder",
        subtype='DIR_PATH'
    )

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        scene = context.scene
        sp = scene.miablen_projects[scene.miablen_pilih_projects]
        sp.mi_lokasi = self.directory
        return {'FINISHED'}

classes = [
    add_miafile,
    reload_miafile,
    ubah_miafile,
    pilih_folder_mineimator_pengaturan,
    pilih_folder_mineimator_mif
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()