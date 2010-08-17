# ##### BEGIN GPL LICENSE BLOCK #####
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# ##### END GPL LICENCE BLOCK #####

# M3 Importer by Alexander Stante (stante@gmail.com)
#
# This script imports the M3 file into Blender for editing

import bpy

from bpy.props import *

class IMPORT_OT_m3(bpy.types.Operator):
	bl_idname = "import_shape.m3"
	bl_label  = "Import M3"

	filepath = StringProperty(name="File Path", description="Filepath used for importing the M3 file", maxlen= 1024, default= "")
	
	# Options to select import porperties
	IMPORT_MESH      = BoolProperty(name="Import Mesh", description="Import the Model Geometry", default=True)
	IMPORT_NORMALS   = BoolProperty(name="Import Normals", description="Import the Model Normals", default=False)
	IMPORT_MATERIALS = BoolProperty(name="Import Bones", description="Import the Model Bones", default=False)
	
	def poll(self, context):
		return True
		
	def execute(self, context):
		return {'FINISHED'}
		
	def invoke(self, context, event):
		wm = context.manager
		wm.add_fileselect(self)
		return {'RUNNING_MODAL'}
		
def menu_func(self, context):
    self.layout.operator(IMPORT_OT_m3.bl_idname, text="Blizzard M3 (.m3)")

def register():
    bpy.types.register(IMPORT_OT_m3)
    bpy.types.INFO_MT_file_import.append(menu_func)
    
def unregister():
    bpy.types.unregister(IMPORT_OT_m3)
    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()
