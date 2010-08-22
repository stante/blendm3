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
import os

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
        
    def readFloat(self):
        (unsignedShort, ) = unpack_from("<f", self.file.read(calcsize("<f")))
        return unsignedShort
        
        
    def readArrayUnsignedShort(self, count):
        return unpack_from("<" + str(count) + "H", self.file.read(calcsize("<" + str(count) + "H")))
        
    def readArraySignedShort(self, count):
        return unpack_from("<" + str(count) + "h", self.file.read(calcsize("<" + str(count) + "h")))
        
    def readVector(self):
        return unpack_from("<3f", self.file.read(calcsize("<3f")))
        
    def readString(self, count):
        (string, ) = unpack_from("<" + str(count) + "s", self.file.read(calcsize("<" + str(count) + "s")))
        return string
        
    def readId(self):
        id = self.readString(4)
        return id[::-1]
        
    def readM3Reference(self):
        return M3Reference(self)
        
    def readReferenceEntry(self):
        ref = M3Reference(self)
        
        if (ref.Index != 0):
            return self.ReferenceTable[ref.Index]
        else:
            return self.ReferenceTable[ref.Index]
            # In non debug should return None
            # return None

    def readCHAR(self, entry):
        offset = entry.Offset
        count = entry.Count
        
        self.file.seek(offset)
        string = self.readString(count)
        string = string[0:-1].decode("ascii")
        return string
        
    
        
    def readReferenceById(self):
        entry = self.readReferenceEntry()
        
        position = self.file.tell()
        
        if (entry.Id == b'CHAR'):
            result = self.readCHAR(entry)
        
        elif (entry.Id == b'LAYR'):
            result = self.readLAYR(entry)
            
        elif (entry.Id == b'MAT_'):
            result = self.readMAT(entry)
            
        else:
            #raise Exception('import_m3: !ERROR! Unsupported reference format. Format: %s Count: %s' % (str(entry.Id), str(entry.Count)))
            print('import_m3: !ERROR! Unsupported reference format. Format: %s Count: %s' % (str(entry.Id), str(entry.Count)))
            return entry

        
        self.file.seek(position)
        
        return result
    
    def readLAYR(self, reference):
        layr = 0
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        if count != 1:
            raise Exception("Unsupported LAYR count")
        
        return LAYR(self)
    
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
        
    def readBat(self, reference):
        bat    = []
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            bat.append(BAT(self))
            
        return bat
    
    def readMsec(self, reference):
        return 0
        
    def readMAT(self, reference):
        mat = []
        count = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            mat.append(MAT(self))
            
        return mat

class MAT:

    def __init__(self, file):
        # Read chunk
        self.Name = file.readReferenceById()
        self.D1 = file.readUnsignedInt()
        self.Flags = file.readUnsignedInt()
        self.BlendMode = file.readUnsignedInt()
        self.Priority = file.readUnsignedInt()
        self.D2 = file.readUnsignedInt()
        self.Specularity = file.readFloat()
        self.F1 = file.readFloat()
        self.CutoutThreshold = file.readUnsignedInt()
        self.SpecularMultiplier = file.readFloat()
        self.EmissiveMultiplier = file.readFloat()
        
        self.Layers = []
        
        for i in range(13):
            self.Layers.append(file.readReferenceById())
            if self.Layers[i] != None:
                print("%s: %s" % (i, self.Layers[i].Path))
            
        self.D3 = file.readUnsignedInt()
        self.LayerBlend = file.readUnsignedInt()
        self.EmissiveBlend = file.readUnsignedInt()
        self.D4 = file.readUnsignedInt()
        self.SpecularType = file.readUnsignedInt()
        
        file.skipBytes(2*0x14)
        
        print(self.Name)
        
class LAYR:

    def __init__(self, file):
        file.skipBytes(4)
        self.Path = file.readReferenceById()
        
        
class BAT:
    
    def __init__(self, file):
        file.skipBytes(4)
        self.REGN_Index = file.readUnsignedShort()
        file.skipBytes(4)
        self.MAT_Index = file.readUnsignedShort()
        file.skipBytes(2)
        print("BAT---------------------------------------------")
        print("REGN Index : " + str(self.REGN_Index))
        print("MAT Index  : " + str(self.MAT_Index))
        print("------------------------------------------------")

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
        referenceIndices = file.readReferenceEntry()
        referenceRegions = file.readReferenceEntry()
        referenceBat     = file.readReferenceEntry()
        referenceMsec    = file.readReferenceEntry()

        self.Indices = file.readIndices(referenceIndices)
        self.Regions = file.readRegions(referenceRegions)
        self.Bat     = file.readBat(referenceBat)
        self.Msec    = file.readMsec(referenceMsec)

        print("M3Div-------------------------------------------")
        print("Vertex List Count  : " + str(referenceIndices.Count))
        print("Vertex List Offset : " + hex(referenceIndices.Offset))
        print("DIV List Count     : " + str(referenceRegions.Count))
        print("DIV List Offset    : " + hex(referenceRegions.Offset))
        print("BAT List Count     : " + str(referenceBat.Count))
        print("BAT List Offset    : " + hex(referenceBat.Offset))
        print("MSEC List Count    : " + str(referenceMsec.Count))
        print("MSEC List Offset   : " + hex(referenceMsec.Offset))
        print("------------------------------------------------")

class M3Vertex:
    VERTEX32 = 0
    VERTEX36 = 1
    VERTEX40 = 2
    VERTEX44 = 3
    
    def __init__(self, file, type, flags):
        self.Position   = file.readVector()
        self.BoneWeight = file.readBytes(4)
        self.BoneIndex  = file.readBytes(4)
        self.Normal     = file.readBytes(4)
        self.UV         = []

        # Vertex type specifies how many UV entries the Vertex format contains
        for i in range(type + 1):
            (u, v) = file.readArraySignedShort(2)
            u = u / 2048.0
            v = v / 2048.0
            
            v = 1 - v
            self.UV.append((u,v))
        
        # Further investigation of this flag needed
        if ((flags & 0x200) != 0):
            file.skipBytes(4)
            
        self.Tangent    = file.readBytes(4)

class MODL23:
    
    def __init__(self):
        self.Flags = 0
        self.Vertices = []
        self.Faces = []
        self.Materials = []
        
    def read(file):
        m3model = MODL23()
        file.skipBytes(0x60)
        m3model.Flags = file.readUnsignedInt()

        vertexReference = file.readReferenceEntry()
        viewReference   = file.readReferenceEntry()
        BoneLookup = file.readReferenceEntry()
        print("BoneLookup:")
        BoneLookup.print()
        
        # Bounding Sphere
        vector0 = file.readVector()
        vector1 = file.readVector()
        radius = file.readFloat()
        flags = file.readUnsignedInt()
        
        file.skipBytes(0x3C)
        
        Attachments = file.readReferenceEntry()
        print("Attachments")
        Attachments.print()
        AttachmentLookup = file.readReferenceEntry()
        print("Attachment Lookup")
        AttachmentLookup.print()
        Lights = file.readReferenceEntry()
        print("Lights")
        Lights.print()
        SHBX = file.readReferenceEntry()
        print("SHBX")
        SHBX.print()
        Cameras = file.readReferenceEntry()
        print("Cameras")
        Cameras.print()
        D = file.readReferenceEntry()
        print("D")
        D.print()
        MaterialLookup = file.readReferenceEntry()
        print("Material Lookup")
        MaterialLookup.print()
        
        m3model.Materials = file.readReferenceById()
        
        # Reading Vertices
        count = 0
        type  = 0
    
        if ((m3model.Flags & 0x100000) != 0):   
            count = vertexReference.Count // 44
            type  = M3Vertex.VERTEX44
                
        elif ((m3model.Flags & 0x80000) != 0):
            count = vertexReference.Count // 40
            type  = M3Vertex.VERTEX40

        elif ((m3model.Flags & 0x40000) != 0):
            count = vertexReference.Count // 36
            type  = M3Vertex.VERTEX36

        elif ((m3model.Flags & 0x20000) != 0):
            count = vertexReference.Count // 32
            type  = M3Vertex.VERTEX32            
                
        else:
            raise Exception('import_m3: !ERROR! Unsupported vertex format. Flags: %s' % hex(m3model.Flags))

            
        print("Reading %s vertices, Flags: %s" % (count, hex(m3model.Flags)))

        file.seek(vertexReference.Offset)
        for i in range(count):
             m3model.Vertices.append(M3Vertex(file, type, m3model.Flags))
        
        # Reading DIV
        file.seek(viewReference.Offset)
        div = M3Div(file)
        
        submeshes = []
        
        # Reading DIV.REGN
        for regn in div.Regions:
            offset = regn.OffsetVert
            number = regn.NumVert
            
            vertices = m3model.Vertices[offset:offset + number]
            faces = []
            
            for j in range(regn.OffsetFaces, regn.OffsetFaces + regn.NumFaces, 3):
                faces.append((div.Indices[j], div.Indices[j+1], div.Indices[j+2]))
                
            submeshes.append(Submesh(vertices, faces, m3model.Materials[0]))
        
        return submeshes
                    
class M3ReferenceEntry:
    
    def __init__(self, file):
        self.Id     = file.readId()
        self.Offset = file.readUnsignedInt()
        self.Count  = file.readUnsignedInt()
        self.Type   = file.readUnsignedInt()
        
    def print(self):
        print("M3ReferenceEntry--------------------------------")
        print("Id:     " + str(self.Id))
        print("Offset: " + hex(self.Offset))
        print("Count:  " + hex(self.Count))
        print("Type:   " + hex(self.Type))
        print("------------------------------------------------")
                
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
        
        if (modelReference.Type != 23):
            raise Exception('import_m3: !ERROR! Unsupported model format: %s' % hex(modelReference.Type))
        
        file.seek(modelReference.Offset)
        self.m3Model = MODL23.read(file)
        
def createMaterial(material):
    # Create image texture from image. Change here if the snippet
    # folder is not located in you home directory.
    realpath = os.path.abspath(material.Layers[0].Path)
    tex = bpy.data.textures.new(material.Name)
    tex.type = 'IMAGE'
    tex = tex.recast_type()
    tex.image = bpy.data.images.load(realpath)
    tex.use_alpha = True
    # Create shadeless material and MTex
    mat = bpy.data.materials.new('TexMat')
    mat.shadeless = False
    mat.add_texture(texture = tex,
    texture_coordinates = 'UV',
    map_to = 'COLOR')
    return mat
                
class Submesh:

    def __init__(self, vertices, faces, material):
        self.Name = "NONAME"
        self.Vertices = []
        # TODO: maybe better to unflatten here instead of in calling function
        self.Faces = faces
        self.UV1 = []
        
        self.Material = material
        
        # position in vertices array
        for v in vertices:
            self.Vertices.append(v.Position)
            
        for i, f in enumerate(self.Faces):
            self.UV1.append(((vertices[f[0]].UV[0]), (vertices[f[1]].UV[0]), (vertices[f[2]].UV[0])))

def import_m3(context, filepath):
    m3data = M3Data(filepath)
    name = basename(filepath)
    os.chdir(os.path.dirname(filepath))

    for submesh in m3data.m3Model:
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(submesh.Vertices, [], submesh.Faces)
        
        mesh.add_uv_texture()
        uvtex = mesh.uv_textures[0]
        uvtex.name = "foo"
        
        for i, uv in enumerate(submesh.UV1):
            data = uvtex.data[i]
            data.uv1 = uv[0]
            data.uv2 = uv[1]
            data.uv3 = uv[2]
            data.uv4 = (0,0)
            
        m = createMaterial(submesh.Material)
        
        mesh.update(True)
        ob = bpy.data.objects.new(name, mesh)
        ob.data.add_material(m)
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
