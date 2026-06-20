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
import math
import json
import zipfile
#from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from mathutils import Matrix, Vector, Euler


#print(json.dumps(data, indent=4))

#Blender | Model bech (mimodel) | Json mi
#    X         Z                     Y      ZXY Model bech -> Json mi YXZ
#    Y         X                     X       Json mi YXZ   -> Blender XYZ
#    Z         Y                     Z      blender 1 = 16 Mineimator

def load_data(fpath):
    path_lengkap = bpy.path.abspath(fpath)
    try:
        with open(path_lengkap, "r", encoding="utf-8") as f:
            data = json.load(f)
            f.close()
            return data
    except Exception as e:
        print(e)
        return None
    
def mapping_zib(midata_path):
    zib_path = os.path.splitext(midata_path)[0] + ".zip"
    if not os.path.exists(zib_path):
        return {}
    try:
        hasil = {}
        with zipfile.ZipFile(zib_path, 'r') as zf:
            for path_dalam in zf.namelist():
                nama_file = os.path.basename(path_dalam)
                if nama_file.endswith('.mimodel'):
                    hasil[nama_file] = (zib_path, path_dalam)
        return hasil
    except zipfile.BadZipFile as e:
        print(f"Gagal baca zip: {e}")
        return {}
    
def load_mimodel_dari_zib(zib_mapping, file_name):
    info = zib_mapping.get(file_name, None)
    if not info:
        return None
    zib_path, path_dalam = info
    try:
        with zipfile.ZipFile(zib_path, 'r') as zf:
            with zf.open(path_dalam) as f:
                return json.load(f)
    except Exception as e:
        print(f"Gagal baca {file_name}: {e}")
        return None

def catat_template_dari_midata(md, mf):
    def cari_file_mimodel(c, tp):
        file = c.get("file", None)
        if file: #cek tahap file atas
            return file
        
        #cek tahap states
        state_json = c.get("states", None)
        for st in tp.state:
            value = state_json.get(st.name, {})
            for v in value:
                value_json = v.get("value", "")
                if st.nilai == value_json:
                    file = v.get("file", None)
                    if file:
                        return file
    
    #cari type caracter
    char_json = md.get("characters", None)
    if char_json:
        for tp in mf.mif_template:
            if tp.type == 'char':
                for c in char_json:
                    name = c.get("name", "")
                    if tp.name == name:
                        tp.file_name = cari_file_mimodel(c, tp)
                        
    #cari type spesial block
    spblock_json = md.get("special_blocks", None)
    if spblock_json:
        for tp in mf.mif_template:
             if tp.type == 'spblock':
                 for c in spblock_json:
                     name = c.get("name", "")
                     if tp.name == name:
                         tp.file_name = cari_file_mimodel(c, tp)

def catat_part_mimodel(mimodel_jsoin,tp):
    def baca_part(part, tp, parent_name = ""):
        p = tp.model_part.add()
        
        name = part.get("name", "")
        p.name = name
        
        loc = part.get("position", [0, 0, 0])
        p.loc_x = loc[2] / 16 # x z
        p.loc_y = loc[0] / 16 # y x
        p.loc_z = loc[1] / 16 # z y
        
        rot = part.get("rotation", [0, 0, 0])
        p.rot_x = math.radians(rot[2])
        p.rot_y = math.radians(rot[0])
        p.rot_z = math.radians(rot[1])
        
        siz = part.get("scale", [1, 1, 1])
        p.siz_x = siz[2]
        p.siz_y = siz[0]
        p.siz_z = siz[1]
        
        p.parent = parent_name
        
        bend = part.get("bend", None)
        if bend:
            p.bend = True
            p.offset_bend = bend.get("offset", 0)
            p.type_bend = bend.get("part", None)
        else:
            p.bend = False
        
        for sub in part.get("parts", []):
            baca_part(sub, tp, name)
        
    for root in mimodel_jsoin.get("parts", []):
        baca_part(root, tp, "")

def generate_empty(context, tm, bend = False):
    if context.active_object:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        
    if bend:
        name = tm.name + "_bend"
    else:
        name = tm.name
        
    print(f"Generate {name}")
    obj = bpy.data.objects.new(name, None)
    obj.empty_display_type = 'ARROWS'
    obj.empty_display_size = 0.5
    
    bpy.context.collection.objects.link(obj)
    
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    
    return obj

def atur_parent(obj, parent_obj, tm, bend = False):
    name_cosnt = f"id {tm.parent_id}"
    if name_cosnt in obj.constraints: #cek apakah ada constraintnya
        pacon = obj.constraints[name_cosnt]
    else:
        pacon = obj.constraints.new('CHILD_OF')
        pacon.name = name_cosnt
        
    pacon.target = parent_obj
    
    pacon.use_location_x = tm.loc_ikut_parent
    pacon.use_location_y = tm.loc_ikut_parent
    pacon.use_location_z = tm.loc_ikut_parent
        
    pacon.use_rotation_x = tm.rot_ikut_parent
    pacon.use_rotation_y = tm.rot_ikut_parent
    pacon.use_rotation_z = tm.rot_ikut_parent
        
    pacon.use_scale_x = tm.scale_ikut_parent
    pacon.use_scale_y = tm.scale_ikut_parent
    pacon.use_scale_z = tm.scale_ikut_parent
    
    if tm.type == 'bodypart' and not bend and not tm.part_tunggal:
        loc = Vector((tm.invers_loc_x, tm.invers_loc_y, tm.invers_loc_z))
        rot = Euler((tm.invers_rot_x, tm.invers_rot_y, tm.invers_rot_z), 'XYZ')
        scale = Vector((tm.invers_siz_x, tm.invers_siz_y, tm.invers_siz_z))
    
        mat = Matrix.LocRotScale(loc, rot, scale)
        pacon.inverse_matrix = mat
    else:
        loc = Vector((0, 0, 0))
        rot = Euler((0, 0, 0), 'XYZ')
        scale = Vector((1, 1, 1))
    
        mat = Matrix.LocRotScale(loc, rot, scale)
        pacon.inverse_matrix = mat
    
def inter(terpola = "LINEAR"):
    if terpola == 'LINEAR':
        return "LINEAR"
    
    elif terpola == 'instant':
        return "CONSTANT"
    
    else:
        return "BEZIER"
    
def anim_setup(obj, tm, bend = False):
    #Action
    #├── Slot (terikat ke object)
    #└── Layer
    #    └── Strip (type='KEYFRAME')
    #        └── ChannelBag (per slot, via strip.channelbag(slot))
    #            └── FCurve
    #                └── KeyframePoint
    
    #Blender | Model bech (mimodel) | Json mi
    #    X         Z                     Y      ZXY Model bech -> Json mi YXZ
    #    Y         X                     X       Json mi YXZ   -> Blender XYZ
    #    Z         Y                     Z      blender 1 = 16 Mineimator
    
    def target_object_keyframe(obj, tm, ch):
        loc_x = ch.fcurves.new("location", index=0)
        loc_y = ch.fcurves.new("location", index=1)
        loc_z = ch.fcurves.new("location", index=2)
        
        rot_x = ch.fcurves.new("rotation_euler", index=0)
        rot_y = ch.fcurves.new("rotation_euler", index=1)
        rot_z = ch.fcurves.new("rotation_euler", index=2)
        
        siz_x = ch.fcurves.new("scale", index=0)
        siz_y = ch.fcurves.new("scale", index=1)
        siz_z = ch.fcurves.new("scale", index=2)
        
        for ks in tm.key_set:
            kd_mapping = {}
            for kd in ks.key_data:
                kd_mapping[kd.name] = kd.nilai
                
            transition = inter(kd_mapping.get("TRANSITION", "LINEAR"))
            
            loc_x.keyframe_points.insert(ks.frame, float(kd_mapping.get("POS_Y", tm.loc_x))/16).interpolation = transition
            loc_y.keyframe_points.insert(ks.frame, float(kd_mapping.get("POS_X", tm.loc_y))/16).interpolation = transition
            loc_z.keyframe_points.insert(ks.frame, float(kd_mapping.get("POS_Z", tm.loc_z))/16).interpolation = transition
            
            rot_x.keyframe_points.insert(ks.frame, math.radians(float(kd_mapping.get("ROT_Y", 0)))).interpolation = transition
            rot_y.keyframe_points.insert(ks.frame, math.radians(float(kd_mapping.get("ROT_X", 0)))).interpolation = transition
            rot_z.keyframe_points.insert(ks.frame, math.radians(float(kd_mapping.get("ROT_Z", 0)))).interpolation = transition
            
            siz_x.keyframe_points.insert(ks.frame, float(kd_mapping.get("SCA_Y", 1))).interpolation = transition
            siz_y.keyframe_points.insert(ks.frame, float(kd_mapping.get("SCA_X", 1))).interpolation = transition
            siz_z.keyframe_points.insert(ks.frame, float(kd_mapping.get("SCA_Z", 1))).interpolation = transition
            
        loc_x.update()
    
    if not obj.animation_data:
        obj.animation_data_create()

    anim = obj.animation_data
    
    # Action
    act = bpy.data.actions.new(obj.name)
    anim.action = act

    # Slot
    slot = act.slots.new(id_type='OBJECT', name=obj.name)
    anim.action_slot = slot
    
    # Layer dan Strip
    layer = act.layers.new("Layer")
    strip = layer.strips.new(type='KEYFRAME')

    # ChannelBag ke FCurve
    ch = strip.channelbag(slot, ensure=True)
    
    if not bend:
        target_object_keyframe(obj, tm, ch)
    

class gen_setup(Operator):
    """Setup Scene Project"""
    bl_idname = "scene.mif_setup"
    bl_label = "Setup Scene Project"
    bl_options = {'REGISTER', 'UNDO'}
    
    baru: bpy.props.BoolProperty(name='create all objects from scratch', default=False)
    
    def draw(self, context):
        layout = self.layout
        layout.prop(self, "baru")
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        scene = context.scene
        mf = scene.miablen_projects[scene.miablen_pilih_projects]
        path_miproject = bpy.path.abspath(mf.lokasi)
        dir_miproject = os.path.dirname(path_miproject)
        
        #Cek keberadaan aset sofware mineimator
        path_mi = bpy.path.abspath(mf.mi_lokasi)
        aset = os.path.join(path_mi, "Data/Minecraft")
        if os.path.isdir(aset):
            
            #catat midata file
            midata_file = [] 
            for file in os.listdir(aset):
                if file.endswith('.midata'):
                    midata_file.append(file)
            if len(midata_file) > 0:
                mf.mi_software_status = True
            else:
                mf.mi_software_status = False
                return {'CANCELLED'}
        else:
            mf.mi_software_status = False
            return {'CANCELLED'}
        
        #Baca data aset dan maping zib
        midata_json = []
        zib_mapping = {}
        for fmidata in midata_file:
            midata_file_path = os.path.join(aset, fmidata)
            data = load_data(midata_file_path)
            zib = mapping_zib(midata_file_path)
            if data:
                midata_json.append(data)
            zib_mapping.update(zib)
                
        if len(midata_json) > 0:
            if len(mf.mif_template) > 0:
                for md in midata_json:
                    catat_template_dari_midata(md, mf)
        else:
            mf.mi_software_status = False
            return {'CANCELLED'}

        #Catat structure mimodel
        if len(mf.mif_template) > 0:
            for tp in mf.mif_template:
                #bersihin dulu part nya
                if len(tp.model_part) > 0:
                    tp.model_part.clear()
                #cek file name
                if tp.file_name:
                    mimodel_json = None
                    
                    if tp.type == 'model':
                        file_mimodel = os.path.join(dir_miproject, tp.file_name)
                        if os.path.exists(file_mimodel):
                            mimodel_json = load_data(file_mimodel)
                            
                    elif tp.type in ('char', 'bodypart', 'spblock'):
                        mimodel_json = load_mimodel_dari_zib(zib_mapping, tp.file_name)
                        
                    if mimodel_json:
                        catat_part_mimodel(mimodel_json,tp)
        
        #Buat atau pake object dan sinkronisasi template
        parent_id = {}
        for tm in mf.mif_timeline:
            if tm.usang:
                continue
            
            #sinkronisasi template
            if tm.type == 'bodypart':
                for tp in mf.mif_template:
                    if tm.template_id == tp.id:
                        
                        #body part tunggal
                        tm.part_tunggal = False
                        if tp.type == 'bodypart':
                            tm.part_tunggal = True
                        
                        #body part dari model
                        for mp in tp.model_part:
                            if tm.part_name == mp.name:
                                tm.bend_part = mp.bend
                                tm.offset_bend = mp.offset_bend
                                tm.type_bend = mp.type_bend
                                if not tm.part_tunggal:
                                    tm.invers_loc_x = mp.loc_x
                                    tm.invers_loc_y = mp.loc_y
                                    tm.invers_loc_z = mp.loc_z
    
                                    tm.invers_rot_x = mp.rot_x
                                    tm.invers_rot_y = mp.rot_y
                                    tm.invers_rot_z = mp.rot_z
    
                                    tm.invers_siz_x = mp.siz_x
                                    tm.invers_siz_y = mp.siz_y
                                    tm.invers_siz_z = mp.siz_z
                                break
                        break
            
            #buat baru atau pake object yang ada
            if not self.baru and tm.target_object: #cek target object
                obj = scene.objects.get(tm.target_object.name)
                if not obj:
                    obj = generate_empty(context, tm)
                    tm.target_object = obj
            else:
                obj = generate_empty(context, tm)
                tm.target_object = obj
                
            #buat baru atau tambahkan object bend
            if tm.bend_part:
                if not self.baru and tm.target_bend_object: #cek bend object
                    obj_bend = scene.objects.get(tm.target_bend_object.name)
                    if not obj_bend:
                        obj_bend = generate_empty(context, tm, True)
                        tm.target_bend_object = obj_bend
                else:
                    obj_bend = generate_empty(context, tm, True)
                    tm.target_bend_object = obj_bend
            
            #sekaligus catat parent
            parent_id[tm.id] = tm.target_object.name
                
        #mulai oprasi
        for tm in mf.mif_timeline:
            if tm.usang:
                continue
            
            obj = tm.target_object
            
            #Atur Parent
            if not tm.parent_id == 'root':
                parent = parent_id.get(tm.parent_id, None)
                if parent:
                    parent_obj = scene.objects.get(parent)
                    atur_parent(obj, parent_obj, tm)
            
            #atur lokasi dan animasi
            if len(tm.key_set) > 0: #atur animasi
                anim_setup(obj, tm)
                
            else: #atur lokasi buat yang gak punya animasi
                if obj.animation_data:
                    anim = obj.animation_data
                    anim.action = None
                obj.location[0] = tm.loc_x
                obj.location[1] = tm.loc_y
                obj.location[2] = tm.loc_z
                
                obj.rotation_euler[0] = 0
                obj.rotation_euler[1] = 0
                obj.rotation_euler[2] = 0
                
                obj.scale[0] = 1
                obj.scale[1] = 1
                obj.scale[2] = 1
        
        return {'FINISHED'}

classes = [
    gen_setup,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()