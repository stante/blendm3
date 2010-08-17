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
		
	def readM3Reference(self):
		return M3Reference.read(self)
		
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
			regions.append(M3Region.read(self))
			
		return regions

class M3Reference:
	def __init__(self):
		self.Count = 0
		self.Index = 0
		self.Flags = 0
		
	def read(file):
		m3reference = M3Reference()
		
		m3reference.Count = file.readUnsignedInt()
		m3reference.Index = file.readUnsignedInt()
		m3reference.Flags = file.readUnsignedInt()
		
		return m3reference


class M3Region:
	def __init__(self):
		self.D1        = 0
		self.OffsetVert   = 0
		self.NumVert   = 0
		self.OffsetFaces  = 0
		self.NumFaces  = 0
		self.BoneCount = 0
		self.IndBone   = 0
		self.Numbone   = 0
		self.S1        = []
		
	def read(file):
		m3region = M3Region()
		
		m3region.D1        = file.readUnsignedInt()
		m3region.D2        = file.readUnsignedInt()
		m3region.OffsetVert   = file.readUnsignedInt()
		m3region.NumVert   = file.readUnsignedInt()
		m3region.OffsetFaces  = file.readUnsignedInt()
		m3region.NumFaces  = file.readUnsignedInt()
		m3region.BoneCount = file.readUnsignedShort()
		m3region.IndBone   = file.readUnsignedShort()
		m3region.NumBone   = file.readUnsignedShort()
		m3region.s1        = file.readArrayUnsignedShort(3)
		#file.skipBytes(6)
		
		print("M3Region-----------------")
		print("D1:            " + str(m3region.D1))
		print("OffsetVert:    " + str(m3region.OffsetVert))
		print("NumVert:       " + str(m3region.NumVert))
		print("OffsetFaces:   " + str(m3region.OffsetFaces))
		print("NumFaces:      " + str(m3region.NumFaces))
		print("BoneCount:     " + str(m3region.BoneCount))
		print("IndBone:       " + str(m3region.IndBone))
		print("NumBone:       " + str(m3region.NumBone))
		print("------------------------")
		
		return m3region

class M3Div:
	def __init__(self):
		self.Indices = []
		self.Regions = []
		self.Bat     = []
		self.Msec    = []
	
	def read(file):
		div = M3Div()
		referenceIndices = file.readM3Reference()
		referenceRegions = file.readM3Reference()
		referenceBat     = file.readM3Reference()
		referenceMsec    = file.readM3Reference()
		
		print("Model Divisions")
		print("===============")
		print("Faces:  " + str(referenceIndices.Count))
		print("Meshes: " + str(referenceRegions.Count))
		
		referenceIndicesEntry = file.ReferenceTable[referenceIndices.Index]
		referenceRegionsEntry = file.ReferenceTable[referenceRegions.Index]
		
		referenceIndicesEntry.print()
		referenceRegionsEntry.print()
			
		div.Indices = file.readIndices(referenceIndicesEntry)
		div.Regions = file.readRegions(referenceRegionsEntry)

		return div

# TODO: Fix read using M3File
class M3Vertex:
	
	def __init__(self):
		self.Position = (0, 0, 0)
		
	def read(file):
		m3vertex = M3Vertex()
		m3vertex.Position   = file.readVertex()
		m3vertex.BoneWeight = file.readBytes(4)
		m3vertex.BoneIndex  = file.readBytes(4)
		m3vertex.Normal     = file.readBytes(4)
		m3vertex.UV         = file.readArrayUnsignedShort(2)
		m3vertex.D1         = file.readUnsignedInt()
		m3vertex.Tangent    = file.readBytes(4)
		
		return m3vertex
		

class M3Model23:
	
	def __init__(self):
		self.Flags = 0
		self.Vertices = []
		self.Faces = []
		
	def read(file):
		m3model = M3Model23()
		file.skipBytes(0x60)
		m3model.Flags = file.readUnsignedInt()

		vertexReference = M3Reference.read(file)
		viewReference   = M3Reference.read(file)
		
		print("Flags:  " + hex(m3model.Flags))
		
		viewReferenceEntry = file.ReferenceTable[viewReference.Index]
		vertexReferenceEntry = file.ReferenceTable[vertexReference.Index]
		
		viewReferenceEntry.print()
		vertexReferenceEntry.print()
		
		if ((m3model.Flags & 0x20000) != 0):
			if ((m3model.Flags & 0x40000) != 0):
				count = vertexReferenceEntry.Count // 36
				print(count)
				file.seek(vertexReferenceEntry.Offset)
				for i in range(count):
					ver = M3Vertex.read(file)
					m3model.Vertices.append(ver.Position)
					# print(self.Vertices[i].Position)
		
		#print("DIV: " + hex(self.DivDataOffset))
		#print("DIV: " + hex(self.DivDataCount))
			
		file.seek(viewReferenceEntry.Offset)
		div = M3Div.read(file)
		
		#for i in range(len(div.Regions)):
		i = 1

		add = div.Regions[i].OffsetVert
		
		print("div.Indices length:")
		print(len(div.Indices))
		
		for j in range(div.Regions[i].OffsetFaces, div.Regions[i].OffsetFaces + div.Regions[i].NumFaces, 3):
			m3model.Faces.append((div.Indices[j]+add, div.Indices[j+1]+add, div.Indices[j+2]+add))
			
		#for i in range(22, len(div.Indices)-3, 3):
		#	m3model.Faces.append((div.Indices[i], div.Indices[i+1], div.Indices[i+2]))
		
		return m3model
		
		#print(self.Vertices)
					
class M3ReferenceEntry:
	
	def __init__(self):
		self.Id = []
		self.Offset = 0
		self.Count = 0
		self.Type = 0

	def print(self):
		print("============================")
		print("Id:     " + str(self.Id))
		print("Offset: " + hex(self.Offset))
		print("Count:  " + str(self.Count))
		print("Type:   " + hex(self.Type))
		print("============================")
		
	def read(file):
		m3referenceEntry = M3ReferenceEntry()
		
		m3referenceEntry.Id = file.readString(4)
		m3referenceEntry.Id = m3referenceEntry.Id[::-1]
		m3referenceEntry.Offset = file.readUnsignedInt()
		m3referenceEntry.Count = file.readUnsignedInt()
		m3referenceEntry.Type = file.readUnsignedInt()
		
		return m3referenceEntry
	

class M3Header:

	def __init__(self):
		self.Id = []
		self.ReferenceTableOffset = 0
		self.ReferenceTableCount = 0
		self.ModelCount = 0
		self.ModelIndex = 0
		
	def read(file):
		m3header = M3Header()
	
		m3header.Id = file.readString(4)
		m3header.ReferenceTableOffset = file.readUnsignedInt()
		m3header.ReferenceTableCount = file.readUnsignedInt()
		m3header.ModelCount = file.readUnsignedInt()
		m3header.ModelIndex = file.readUnsignedInt()
		
		print("M3 File Header")
		print("--------------")
		print(m3header.Id)
		print(hex(m3header.ReferenceTableOffset))
		print(m3header.ReferenceTableCount)
		print(m3header.ModelCount)
		print(m3header.ModelIndex)
		print("--------------")

		count  = m3header.ReferenceTableCount
		offset = m3header.ReferenceTableOffset
		
		file.seek(offset)
		
		for i in range(count):
			file.ReferenceTable.append(M3ReferenceEntry.read(file))
			
		return m3header
				

class M3Data:
	def __init__(self, filepath):
		file = M3File(filepath)
		
		# Reading file header
		self.m3Header = M3Header.read(file)
		
		# Reading model
		modelReference = file.ReferenceTable[self.m3Header.ModelIndex]
		modelReference.print()
		
		file.seek(modelReference.Offset)
		self.m3Model = M3Model23.read(file)

def import_m3(filepath):
	m3data = M3Data(filepath)
	mesh = bpy.data.meshes.new("MyMesh")
	mesh.from_pydata(m3data.m3Model.Vertices, [], m3data.m3Model.Faces)
	mesh.update(True)
	ob = bpy.data.objects.new("MyObject", mesh)
	sc = bpy.data.scenes[0].objects.link(ob)

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
		import_m3(self.properties.filepath)
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
