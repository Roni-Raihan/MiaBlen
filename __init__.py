bl_info = {
    "name": "MiaBlen",
    "author": "Roni Raihan (TRPHB Animation)",
    "version": (1, 0),
    "blender": (4, 4, 1),
    "location": "Properties > Scene Properties",
    "description": "Read Mineimator Project file (animation data only)",
    "warning": "animation data only",
    "doc_url": "",
    "category": "Import-Export",
}

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

from . import miablen_property
from . import miablen_operator
from . import miablen_ui
from . import miablen_import

from .generate import generate_and_setup
#from .generate import gen_model
#from .generate import setup_parent
#from .generate import setup_animation
#from .generate import setup_all
        
class catatan_addon(bpy.types.AddonPreferences):
    bl_idname = __name__
    
    mi_lokasi: bpy.props.StringProperty(name='Default Mine-Imator Software Folder', default='')
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        col = layout.column()
        
        box = col.box()
        if not self.mi_lokasi:
            box.alert = True
        row = box.row(align=True)
        row.prop(self, "mi_lokasi")
        row.operator("scene.pilih_folder_mineimator_pengaturan", icon='FILEBROWSER', text='')
        
        box_col = box.column()
        box_col.label(text="This is needed to generate and arrange the initial position of the bones of an", icon='INFO')
        box_col.label(text="asset such as a character rig, block rig, etc.", icon='BLANK1')
        
        box2 = col.box()
        col = box2.column()
        col.label(text="Spesial Thanks to:", icon='INFO')
        col.label(text="Yogaindo CR", icon='BLANK1')
        col.label(text="Aryl Animasi", icon='BLANK1')
        col.label(text="Erval", icon='BLANK1')
        col.label(text="Tcalya", icon='BLANK1')
        col.label(text="Pebry", icon='BLANK1')
        col.label(text="Raffsimation", icon='BLANK1')

def register():
    bpy.utils.register_class(catatan_addon)
    miablen_property.register()
    miablen_import.register()
    miablen_operator.register()
    miablen_ui.register()
    
    generate_and_setup.register()

def unregister():
    bpy.utils.unregister_class(catatan_addon)
    miablen_property.unregister()
    miablen_import.unregister()
    miablen_operator.unregister()
    miablen_ui.unregister()
    
    generate_and_setup.unregister()

if __name__ == "__main__":
    register()