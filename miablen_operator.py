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
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


#~~~~ Remove path di file list
class hapus_miafile(Operator):
    """Remove path to list"""
    bl_idname = "scene.hapus_mif"
    bl_label = "Remove"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        if not len(scene.miablen_projects) == 0:        
            scene.miablen_projects.remove(scene.miablen_pilih_projects)
            
            if scene.miablen_pilih_projects > len(scene.miablen_projects)-1 and not scene.miablen_pilih_projects == 0:
                scene.miablen_pilih_projects = len(scene.miablen_projects)-1
        return {'FINISHED'}

#~~~~ pindah data Ke atas di file list
class pindah_miafile_ke_atas(Operator):
    """Move item in list to UP"""
    bl_idname = "scene.pindah_miafile_ke_atas"
    bl_label = "Move"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        miablen_projects = scene.miablen_projects
        
        if not scene.miablen_pilih_projects > len(miablen_projects)-1 and not scene.miablen_pilih_projects == 0:
            miablen_projects.move(scene.miablen_pilih_projects, scene.miablen_pilih_projects-1)
            scene.miablen_pilih_projects -= 1
        return {'FINISHED'}

#~~~~ pindah data Ke bawah di file list
class pindah_miafile_ke_bawah(Operator):
    """Move item in list to DOWN"""
    bl_idname = "scene.pindah_miafile_ke_bawah"
    bl_label = "Move"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        scene = context.scene
        miablen_projects = scene.miablen_projects
        
        if not scene.miablen_pilih_projects == len(miablen_projects)-1:
            miablen_projects.move(scene.miablen_pilih_projects, scene.miablen_pilih_projects+1)
            scene.miablen_pilih_projects += 1
        return {'FINISHED'}

classes = [
    hapus_miafile,
    pindah_miafile_ke_atas,
    pindah_miafile_ke_bawah
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()