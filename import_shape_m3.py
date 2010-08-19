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
from struct import unpack_from, calcsize
from os.path import basename

# M3 File representation encapsulating file handle
class M3File:
	def __init__(self, filepath):
		self.file = open(filepath, "rb")
		self.ReferenceTable = []
		
	def seek(self, position, offset):
		self.file.seek(position, offset)
		
	def seek(self, position):
		self.file.seek(position, 0)
		
	def skipBytes(self, count):
		self.file.seek(count, 1)

	def readBytes(self, count):
		return unpack_from("<" + str(count) + "B", self.file.read(calcsize("<" + str(count) + "B")))
	
	def readUnsignedInt(self):
		(unsignedInt, ) = unpack_from("<I", self.file.read(calcsize("<I")))
		return unsignedInt
		
	def readUnsignedShort(self):
		(unsignedShort, ) = unpack_from("<H", self.file.read(calcsize("<H")))
		return unsignedShort
		
	def readArrayUnsignedShort(self, count):
		return unpack_from("<" + str(count) + "H", self.file.read(calcsize("<" + str(count) + "H")))
		
	def readVertex(self):
		return unpack_from("<3f", self.file.read(calcsize("<3f")))
		
	def readString(self, count):
		(string, ) = unpack_from("<" + str(count) + "s", self.file.read(calcsize("<" + str(count) + "s")))
		return string
		
	def readId(self):
		id = self.readString(4)
		return id[::-1]
		
	def readM3Reference(self):
		return M3Reference(self)
		
	def readIndices(self, reference):
		faces = []
		count = reference.Count
		offset = reference.Offset
		
		self.file.seek(offset)
		
		for i in range(count):
			faces.append(self.readUnsignedShort())
			
		return faces
	
	def readRegions(self, reference):
		regions = []
		count = reference.Count
		offset = reference.Offset
		
		self.file.seek(offset)
		
		for i in range(count):
			regions.append(M3Region(self))
			
		return regions

class M3Reference:
	def __init__(self, file):
		self.Count = file.readUnsignedInt()
		self.Index = file.readUnsignedInt()
		self.Flags = file.readUnsignedInt()
		
class M3Region:

	def __init__(self, file):
		self.D1           = file.readUnsignedInt()
		self.D2           = file.readUnsignedInt()
		self.OffsetVert   = file.readUnsignedInt()
		self.NumVert      = file.readUnsignedInt()
		self.OffsetFaces  = file.readUnsignedInt()
		self.NumFaces     = file.readUnsignedInt()
		self.BoneCount    = file.readUnsignedShort()
		self.IndBone      = file.readUnsignedShort()
		self.NumBone      = file.readUnsignedShort()
		self.s1           = file.readArrayUnsignedShort(3)

# TODO read bat and msec		
class M3Div:

	def __init__(self, file):
		self.Bat     = []
		self.Msec    = []
		referenceIndices = M3Reference(file)
		referenceRegions = M3Reference(file)
		referenceBat     = M3Reference(file)
		referenceMsec    = M3Reference(file)
		
		referenceIndicesEntry = file.ReferenceTable[referenceIndices.Index]
		referenceRegionsEntry = file.ReferenceTable[referenceRegions.Index]
		
		self.Indices = file.readIndices(referenceIndicesEntry)
		self.Regions = file.readRegions(referenceRegionsEntry)

class M3Vertex:
	
	def __init__(self, file):
		self.Position   = file.readVertex()
		self.BoneWeight = file.readBytes(4)
		self.BoneIndex  = file.readBytes(4)
		self.Normal     = file.readBytes(4)
		self.UV         = file.readArrayUnsignedShort(2)
		self.D1         = file.readUnsignedInt()
		self.Tangent    = file.readBytes(4)		

class M3Model23:
	
	def __init__(self):
		self.Flags = 0
		self.Vertices = []
		self.Faces = []
		
	def read(file):
		m3model = M3Model23()
		file.skipBytes(0x60)
		m3model.Flags = file.readUnsignedInt()

		vertexReference = M3Reference(file)
		viewReference   = M3Reference(file)
		
		viewReferenceEntry = file.ReferenceTable[viewReference.Index]
		vertexReferenceEntry = file.ReferenceTable[vertexReference.Index]
		
		# if ((m3model.Flags & 0x20000) != 0):
		if ((m3model.Flags & 0x40000) != 0):
			count = vertexReferenceEntry.Count // 36
			file.seek(vertexReferenceEntry.Offset)
			for i in range(count):
				ver = M3Vertex(file)
				m3model.Vertices.append(ver.Position)
		else:
			raise Exception('import_m3: !ERROR! Unsupported vertex format')
			
		file.seek(viewReferenceEntry.Offset)
		div = M3Div(file)
		
		submeshes = []
		
		for regn in div.Regions:
			offset = regn.OffsetVert
			number = regn.NumVert
			
			vertices = m3model.Vertices[offset:offset + number]
			faces = []
			
			for j in range(regn.OffsetFaces, regn.OffsetFaces + regn.NumFaces, 3):
				faces.append((div.Indices[j], div.Indices[j+1], div.Indices[j+2]))
				
			submeshes.append(Submesh(vertices, faces))
		
		return submeshes
					
class M3ReferenceEntry:
	
	def __init__(self, file):
		self.Id     = file.readId()
		self.Offset = file.readUnsignedInt()
		self.Count  = file.readUnsignedInt()
		self.Type   = file.readUnsignedInt()

class M3Header:

	def __init__(self, file):
		self.Id                   = file.readId()
		self.ReferenceTableOffset = file.readUnsignedInt()
		self.ReferenceTableCount  = file.readUnsignedInt()
		self.ModelCount           = file.readUnsignedInt()
		self.ModelIndex           = file.readUnsignedInt()
		
		if self.Id != b'MD34':
			raise Exception('import_m3: !ERROR! Unsupported file format')
		
		count  = self.ReferenceTableCount
		offset = self.ReferenceTableOffset
		
		file.seek(offset)
		
		for i in range(count):
			file.ReferenceTable.append(M3ReferenceEntry(file))
		
class M3Data:

	def __init__(self, filepath):
		file = M3File(filepath)
		
		# Reading file header
		self.m3Header = M3Header(file)
		
		# Reading model
		modelReference = file.ReferenceTable[self.m3Header.ModelIndex]
		
		file.seek(modelReference.Offset)
		self.m3Model = M3Model23.read(file)
		
class Submesh:

	def __init__(self, vertices, faces):
		self.Name = "NONAME"
		self.Vertices = vertices
		self.Faces = faces

def import_m3(context, filepath):
	m3data = M3Data(filepath)
	name = basename(filepath)
	
	for submesh in m3data.m3Model:
		mesh = bpy.data.meshes.new(name)
		mesh.from_pydata(submesh.Vertices, [], submesh.Faces)
		mesh.update(True)
		ob = bpy.data.objects.new(name, mesh)
		context.scene.objects.link(ob)

class IMPORT_OT_m3(bpy.types.Operator):
	'''Import from Blizzard M3 file'''
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
		import_m3(context, self.properties.filepath)
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
