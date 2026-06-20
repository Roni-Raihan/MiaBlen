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


def gambar_ui_project(context):
    scene = context.scene
    if not scene.miablen_pilih_projects > len(scene.miablen_projects)-1:
        mf = scene.miablen_projects[scene.miablen_pilih_projects]
        if not mf.cek_refres:
            return True
        else:
            return False
    else:
        return False
    
def ikon_berdasarkan_type(type):
    if type == 'char':
        return ("Character", "ARMATURE_DATA")
    
    elif type == 'bodypart':
        return ("Character Part", "BONE_DATA")
    
    elif type == 'item':
        return ("Item", "OBJECT_DATAMODE")
    
    elif type == 'block':
        return ("Block", "MESH_CUBE")
    
    elif type == 'spblock':
        return ("Special Block", "FACE_MAPS")
    
    elif type == 'model':
        return ("Custom model", "ARMATURE_DATA")
    
    elif type in ('surface', 'cube', 'cone', 'cylinder', 'sphere'):
        return (type, "GEOMETRY_SET")
    
    elif type == 'texture':
        return ("Texture", "UV")
    
    elif type == 'skin':
        return ("Skin", "UV")
    
    elif type == 'itemsheet':
        return ("Item sheet", "MESH_GRID")
    
    elif type == 'blocksheet':
        return ("Block sheet", "MESH_GRID")
    
    elif type == 'particlesheet':
        return ("Particle sheet", "MESH_GRID")
    
    elif type == 'folder':
        return ("Folder", "FILEBROWSER")
    
    elif type == 'camera':
        return ("Camera", "CAMERA_DATA")
    
    elif type == 'spotlight':
        return ("Spot Light", "LIGHT_SPOT")
    
    elif type == 'pointlight':
        return ("Point Light", "LIGHT")
    
    elif type == 'audio':
        return ("Audio", "OUTLINER_DATA_SPEAKER")
    
    elif type == 'root':
        return ("root", "EMPTY_ARROWS")
    
    else :
        return ("Other", "MESH_DATA")
    
class project_list_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row()
                row.prop(item, "name", text='', emboss=False)
                
class timeline_list_UI(bpy.types.UIList):
    def filter_items(self, context, data, propname):
        items = getattr(data, propname)
        flt_flags = [self.bitflag_filter_item if it.lihat_tampil else 0 for it in items]
        flt_neworder = [it.lihat_rank for it in items]
        return flt_flags, flt_neworder

    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        row = layout.row(align=True)
        row.alert = item.usang
        for _ in range(item.lihat_level):
            row.label(text="", icon='BLANK1')
            
        punya_anak = any(t.parent_id == item.id for t in data.mif_timeline)
        if punya_anak:
            ic = 'DISCLOSURE_TRI_DOWN' if item.lihat_expand else 'DISCLOSURE_TRI_RIGHT'
            row.prop(item, "lihat_expand", text="", icon=ic, emboss=False)
        else:
            row.label(text="", icon='BLANK1')
            
        row.prop(item, "name", text="", icon=ikon_berdasarkan_type(item.type)[1], emboss=False)
        
class key_set_list_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row()
                row.prop(item, "name", text='', emboss=False)
                
class template_list_UI(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if item:
                row = layout.row()
                row.label(text=f"{item.name}", icon=ikon_berdasarkan_type(item.type)[1])
                

class MiaBlen_Panel(bpy.types.Panel):
    bl_label = "MiaBlen"
    bl_idname = "SCENE_PT_MiaBlen"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"

    def draw(self, context):
        scene = context.scene
        
        layout = self.layout
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        layout.label(text="File Project")
        row = layout.row()
        row.template_list("project_list_UI", "", scene, "miablen_projects", scene, "miablen_pilih_projects")
        
        col = row.column(align= True)
        col.operator("scene.import_mif", icon='ADD', text='')
        col.operator("scene.hapus_mif", icon='REMOVE', text='')
        
        if len(scene.miablen_projects) > 0:
            col.separator()
            col.operator("scene.pindah_miafile_ke_atas", icon='TRIA_UP', text='')
            col.operator("scene.pindah_miafile_ke_bawah", icon='TRIA_DOWN', text='')
            
        if not scene.miablen_pilih_projects > len(scene.miablen_projects)-1:
            mf = scene.miablen_projects[scene.miablen_pilih_projects]
            
            layout.label(text="Project")
            col = layout.column()
            col.prop(mf, "name", text="Name")
            row = col.row()
            row.prop(mf, "lokasi")
            row.operator("scene.change_mif", icon='FILEBROWSER', text='')
            
            row = col.row()
            if not mf.mi_software_status:
                row.alert = True
            row.prop(mf, "mi_lokasi")
            row.operator("scene.pilih_folder_mineimator_mif", icon='FILEBROWSER', text='')
            if not mf.mi_software_status:
                box_info = col.box()
                box_info.alert = True
                box_info_col = box_info.column()
                box_info_col.label(text="Invalid Mine-Imator software or not supported version", icon='ERROR')
                box_info_col.label(text="Select the folder where", icon='QUESTION')
                box_info_col.label(text="the Mine-Imator software is located.", icon='BLANK1')
                box_info_col.label(text="This is necessary to generate and arrange", icon='BLANK1')
                box_info_col.label(text="the initial position of the bones of an asset,", icon='BLANK1')
                box_info_col.label(text="such as a character rig, block rig, and so on.", icon='BLANK1')
                box_info_col.label(text="Leave the field blank to use the default folder.", icon='INFO')
            
            col = layout.column()
            col.alert = mf.cek_refres
            col.operator("scene.reload_mif", icon='FILE_REFRESH', text='Reload')
            
            if not mf.cek_refres:
                box = layout.box()
                box_col = box.column(align=True)
                
                box_col.label(text="Data format - %i" % mf.mif_format)
                box_col.label(text="")
                
                box_col.prop(mf, "mif_nama", emboss=False)
                box_col.prop(mf, "mif_author", emboss=False)
                box_col.prop(mf, "mif_deskripsi", expand=False, emboss=False)
                box_col.prop(mf, "mif_versi", emboss=False)
                
                if mf.mi_software_status:
                    col = layout.column()
                    col.label(text="Scene Project")
                    col.operator("scene.mif_setup", icon='SCENE_DATA', text='Setup Scene Project')
                
class MiaBlen_Timeline(bpy.types.Panel):
    bl_label = "Timeline"
    bl_idname = "SCENE_PT_MiaBlen_Timeline"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_MiaBlen"
    
    @classmethod
    def poll(cls, context):
        return gambar_ui_project(context)
    
    def draw(self, context):
        scene = context.scene
        mf = scene.miablen_projects[scene.miablen_pilih_projects]
        
        layout = self.layout
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column()
        
        col.template_list("timeline_list_UI", "", mf, "mif_timeline", mf, "mif_timeline_pilih")
        
        if not mf.mif_timeline_pilih > len(mf.mif_timeline)-1:
            tm = mf.mif_timeline[mf.mif_timeline_pilih]
            
            col.label(text="Properties", icon = ikon_berdasarkan_type(tm.type)[1])
                
            row = col.row()
            row.prop_search(tm, "target_object", scene, "objects")
            
            if tm.target_bend_object or tm.bend_part:
                row = col.row()
                row.prop_search(tm, "target_bend_object", scene, "objects")
            
            box = layout.box()
            col_box = box.column()
            if tm.usang:
                col_box.label(text="This Timeline Item is not in the Project File")
                col_box.operator("scene.hapus_usang", icon='REMOVE')
            else:
                col_box.prop(tm, "id", emboss=False)
                col_box.prop(tm, "parent_id", emboss=False)
                
                if tm.type in ('char', 'bodypart', 'spblock', 'model'):
                    col_box.prop(tm, "template_id", emboss=False)
                
                if tm.part_name:
                    col_box.prop(tm, "part_name", emboss=False)
                
                col_box.prop(tm, "loc_x", emboss=False)
                col_box.prop(tm, "loc_y", emboss=False)
                col_box.prop(tm, "loc_z", emboss=False)
                
                #if tm.type =='bodypart':
                    #col_box.prop(tm, "invers_loc_x", emboss=False)
                    #col_box.prop(tm, "invers_loc_y", emboss=False)
                    #col_box.prop(tm, "invers_loc_z", emboss=False)
                
                col = layout.column()
                col.label(text="Keyframe Data")
                col.template_list("key_set_list_UI", "", tm, "key_set", tm, "key_set_pilih")
                
                if not tm.key_set_pilih > len(tm.key_set)-1:
                    ks = tm.key_set[tm.key_set_pilih]
                    if ks.key_data:
                        box = layout.box()
                        col_box = box.column()
                        col_box.label(text=f"Frame {ks.frame}")
                        
                        for kd in ks.key_data:
                            col_box.prop(kd, "nilai", text=f"{kd.name}", emboss=False)
                            
class MiaBlen_Template(bpy.types.Panel):
    bl_label = "Template"
    bl_idname = "SCENE_PT_MiaBlen_Template"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "scene"
    bl_parent_id = "SCENE_PT_MiaBlen"
    
    @classmethod
    def poll(cls, context):
        return gambar_ui_project(context)
    
    def draw(self, context):
        scene = context.scene
        mf = scene.miablen_projects[scene.miablen_pilih_projects]
        
        layout = self.layout
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        col = layout.column()
        col.template_list("template_list_UI", "", mf, "mif_template", mf, "mif_template_pilih")
        
        if not mf.mif_template_pilih > len(mf.mif_template)-1:
            tp = mf.mif_template[mf.mif_template_pilih]
            col.label(text="Properties", icon = ikon_berdasarkan_type(tp.type)[1])
            
            box = layout.box()
            col_box = box.column()
            
            col_box.prop(tp, "id", emboss=False)
            if tp.part_name:
                col_box.prop(tp, "part_name", emboss=False)
                
            if tp.file_name:
                col_box.prop(tp, "file_name", emboss=False)
                
            if len(tp.state) > 0:
                for st in tp.state:
                    col_box.prop(st, "nilai", text=f"{st.name}", emboss=False)
                    
            if len(tp.model_part) > 0:
                box = layout.box()
                col_box = box.column()
                    
                    
classes = [
    project_list_UI,
    timeline_list_UI,
    key_set_list_UI,
    template_list_UI,
    MiaBlen_Panel,
    MiaBlen_Timeline,
    MiaBlen_Template,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()