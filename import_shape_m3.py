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
from mathutils import Matrix
from mathutils import Vector
from bpy_extras.io_utils import ImportHelper

bl_info = {
    'name'       : 'Import Blizzard M3 Models(.m3)',
    'author'     : 'Alexander Stante',
    'version'    : (0, 14),
    'blender'    : (2, 80, 0),
    "api"        : 31667,
    'location'   : 'File > Import ',
    'description': 'Import the Blizzard M3 Model Format(.m3)',
    'warning'    : 'Alpha',
    'wiki_url'   : 'https://github.com/stante/blendm3',
    'tracker_url': 'https://github.com/stante/blendm3/issues',
    'category'   : 'Import/Export'
}


# M3 File representation encapsulating file handle
class M3File:

    def __init__(self, filepath):
        self.file = open(filepath, "rb")
        self.ReferenceTable = []
        
    def seek(self, position, offset):
        self.file.seek(position, offset)
        
    def seek(self, position):
        self.file.seek(position, 0)
        
    def skip_bytes(self, count):
        self.file.seek(count, 1)

    def read_bytes(self, count):
        return unpack_from("<" + str(count) + "B", self.file.read(calcsize("<" + str(count) + "B")))
    
    def read_uint(self):
        (unsignedInt, ) = unpack_from("<I", self.file.read(calcsize("<I")))
        return unsignedInt

    def read_short(self):
        (short, ) = unpack_from("<h", self.file.read(calcsize("<h")))
        return short
    
    def read_ushort(self):
        (unsignedShort, ) = unpack_from("<H", self.file.read(calcsize("<H")))
        return unsignedShort
        
    def read_float(self):
        (unsignedShort, ) = unpack_from("<f", self.file.read(calcsize("<f")))
        return unsignedShort
        
        
    def readArrayUnsignedShort(self, count):
        return unpack_from("<" + str(count) + "H", self.file.read(calcsize("<" + str(count) + "H")))
        
    def readArraySignedShort(self, count):
        return unpack_from("<" + str(count) + "h", self.file.read(calcsize("<" + str(count) + "h")))
        
    def read_vector(self):
        return unpack_from("<3f", self.file.read(calcsize("<3f")))
    
    def read_hvector(self):
        return unpack_from("<4f", self.file.read(calcsize("<4f")))
    
    def read_string(self, count):
        (string, ) = unpack_from("<" + str(count) + "s", self.file.read(calcsize("<" + str(count) + "s")))
        return string
        
    def read_id(self):
        id = self.read_string(4)
        return id[::-1]
        
    def read_reference_entry(self):
        ref = M3Reference(self)
        
        if (ref.Index != 0):
            return self.ReferenceTable[ref.Index]
        else:
            return self.ReferenceTable[ref.Index]
            # In non debug should return None
            # return None

    def read_CHAR(self, entry):
        offset = entry.Offset
        count = entry.Count
        
        self.file.seek(offset)
        string = self.read_string(count)
        string = string[0:-1].decode("ascii")
        return string
        
    
        
    def read_reference_by_id(self):
        entry = self.read_reference_entry()
        
        # Check for 'null' reference, return empty list
        #print(entry.Id)

        if (entry.Offset == 0):
            return None
        
        position = self.file.tell()
        
        if (entry.Id == b'CHAR'):
            result = self.read_CHAR(entry)
        elif (entry.Id == b'LAYR'):
            result = self.read_LAYR(entry)
        elif (entry.Id == b'MAT_'):
            result = self.read_MAT(entry)
        elif (entry.Id == b'MATM'):
            result = self.read_MATM(entry)
        elif (entry.Id == b'REGN'):
            result = self.read_REGN(entry)
        elif (entry.Id == b'BAT_'):
            result = self.read_BAT(entry)
        elif (entry.Id == b'MSEC'):
            result = self.read_MSEC(entry)
        elif (entry.Id == b'U16_'):
            result = self.readIndices(entry)
        elif (entry.Id == b'DIV_'):
            result = self.read_DIV(entry)
        elif (entry.Id == b'STC_'):
            result = self.read_STC(entry)
        elif (entry.Id == b'U32_'):
            result = self.read_U32(entry)
        elif (entry.Id == b'BONE'):
            result = self.read_BONE(entry)
        elif (entry.Id == b'IREF'):
            result = self.read_IREF(entry)
        else:
            #raise Exception('import_m3: !ERROR! Unsupported reference format. Format: %s Count: %s' % (str(entry.Id), str(entry.Count)))
            print('import_m3: !ERROR! Unsupported reference format. Format: %s Count: %s' % (str(entry.Id), str(entry.Count)))
            return entry

        
        self.file.seek(position)
        
        return result
        
    def read_STC(self, reference):
        stc = []
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            stc.append(STC(self))
            
        return stc
    
    def read_MATM(self, reference):
        matm = []
        count = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            matm.append(MATM(self))
            
        return matm
    
    def read_LAYR(self, reference):
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
            faces.append(self.read_ushort())
            
        return faces
    
    def read_REGN(self, reference):
        regions = []
        count = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            regions.append(REGN(self))
            
        return regions
        
    def read_BAT(self, reference):
        bat    = []
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            bat.append(BAT(self))
            
        return bat
    
    def read_MSEC(self, reference):
        return 0
        
    def read_MAT(self, reference):
        mat = []
        count = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            mat.append(MAT(self))
            
        return mat
        
    def read_DIV(self, reference):
        div = []
        count = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            div.append(DIV(self))
            
        return div
        
    def read_U32(self, reference):
        u32 = []
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            u32.append(self.read_uint)
            
        return u32
        
    def read_BONE(self, reference):
        bones = []
        
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            bones.append(BONE(self))
            
        return bones
        
    def read_IREF(self, reference):
        matrices = []
        
        count  = reference.Count
        offset = reference.Offset
        
        self.file.seek(offset)
        
        for i in range(count):
            matrices.append(IREF(self))
            
        return matrices
            
class IREF:
    
    def __init__(self, file):
        v1 = file.read_hvector()
        v2 = file.read_hvector()
        v3 = file.read_hvector()
        v4 = file.read_hvector()
        
        self.matrix = Matrix((v1, v2, v3, v4)).transpose()
        
        
        #print(self.matrix)
        
class BONE:
    
    def __init__(self, file):
        # TODO all signed!!!
        self.d1     = file.read_uint()
        self.name   = file.read_reference_by_id()
        self.flags  = file.read_uint()
        self.parent = file.read_short()
        self.s1     = file.read_short()
        
        self.floats = []
        for i in range(34):
            self.floats.append(file.read_float())
            
        #print("Name: %s, Parent: %d, Flags: %s" % (self.name, self.parent, hex(self.flags)))

class STC:
    
    def __init__(self, file):
        self.name      = file.read_reference_by_id()
        self.d1        = file.read_uint()
        self.indSTC    = file.read_uint()
        self.animid    = file.read_reference_by_id()
        self.animindex = file.read_reference_by_id()
        self.d2        = file.read_uint()
        
        self.seq_data = []
        for i in range(13):
            self.seq_data.append(file.read_reference_by_id())
            

        #print("STC-------------------------------")
        #print("Name:   %s" % self.name)
        #print("IndStc: %d" % self.indSTC)
        #print("----------------------------------")

class MATM:
    #TYPES = {'MAT':1, 'DIS':2, 'CMP':3, 'TER':4, 'VOL':5}
    TYPES = {1:'MAT', 2:'DIS', 3:'CMP', 4:'TER', 5:'VOL'}
    def __init__(self, file):
        self.material_type  = MATM.TYPES[file.read_uint()]
        self.MaterialIndex = file.read_uint()
        
        if (self.material_type != 'MAT'):
            print("Unsupported material type")

def set_flags(bits, flag_defines):
    flags = {}
    
    for flag_name, mask in flag_defines.items():
        if bits & mask is not 0:
            flags[flag_name] = True
        else:
            flags[flag_name] = False
            
    return flags

class LAYR:
    #TYPES = [('COLOR', 0), ('SPECULARITY', 2), ('COLOR', 3), ('NORMAL', 9)]
    #TYPES = {'DIFFUSE':0, 'DECAL':1, 'SPECULAR':2, 'SELF_ILLUMINATION':3, 'EMISSIVE':4, 'ENVIO':5, 'ENVIO_MASK':6, 'ALPHA':7, 'UNKNOWN':8, 'NORMAL':9, 'HEIGHT':10}
    TYPES = {0:'DIFFUSIVE', 1:'DECAL', 2:'SPECULAR', 3:'EMISSIVE', 
             4:'EMISSIVE_COLOR', 5:'ENVIO', 6:'ENVIO_MASK', 7:'ALPHA', 8:'UNKNOWN1', 
             9:'NORMAL', 10:'HEIGHT', 11:'UNKNOWN2', 12:'UNKNOWN3'}


    def __init__(self, file):
        file.skip_bytes(4)
        self.Path = file.read_reference_by_id()
    
class MAT:
    FLAGS = {'UNFOGGED_1'        :0x4, 
             'TWO_SIDED'         :0x8, 
             'UNSHADED'          :0x10, 
             'NO_SHADOW_CAST'    :0x20, 
             'NO_HIT'            :0x40, 
             'NO_SHADOW_RECEIVED':0x80, 
             'DEPTH_PREPASS'     :0x100, 
             'USE_TERRAIN_HDR'   :0x200, 
             'SPLAT_UV_FIX'      :0x800, 
             'SOFT_BLENDING'     :0x1000, 
             'UNFOGGED_2'        :0x2000}

    BLEND_MODE = {'OPAQUE'     :0,
                  'ALPHA_BLEND':1,
                  'ADD'        :2,
                  'ALPHA_ADD'  :3,
                  'MOD'        :4,
                  'MOD2X'      :5}
             
    def __init__(self, file):
        # Read chunk
        self.Name                = file.read_reference_by_id()
        self.D1                  = file.read_uint()
        self.flags               = set_flags(file.read_uint(), MAT.FLAGS)
        self.BlendMode           = file.read_uint()
        self.Priority            = file.read_uint()
        self.D2                  = file.read_uint()
        self.specularity         = file.read_float()
        self.F1                  = file.read_float()
        self.CutoutThreshold     = file.read_uint()
        self.specular_multiplier = file.read_float()
        self.EmissiveMultiplier  = file.read_float()
        
        self.Layers = {}
        
        for i in range(13):
            layer = file.read_reference_by_id()
            
            # Layer only exists if they have a path entry
            if (layer.Path != None and layer.Path != ""):
                self.Layers[LAYR.TYPES[i]] = layer
            
        self.D3            = file.read_uint()
        self.LayerBlend    = file.read_uint()
        self.EmissiveBlend = file.read_uint()
        self.D4            = file.read_uint()
        self.specular_type = file.read_uint()
        
        file.skip_bytes(2*0x14)
        
        #print("spec: %f, %f, %d" % (self.specularity, self.specular_multiplier, self.specular_type))
                
        
class BAT:
    
    def __init__(self, file):
        file.skip_bytes(4)
        self.REGN_Index = file.read_ushort()
        file.skip_bytes(4)
        self.MAT_Index = file.read_ushort()
        file.skip_bytes(2)
        #print("BAT---------------------------------------------")
        #print("REGN Index : " + str(self.REGN_Index))
        #print("MAT Index  : " + str(self.MAT_Index))
        #print("------------------------------------------------")

class M3Reference:

    def __init__(self, file):
        self.Count = file.read_uint()
        self.Index = file.read_uint()
        self.Flags = file.read_uint()
        
class REGN:

    def __init__(self, file):
        self.D1           = file.read_uint()
        self.D2           = file.read_uint()
        self.OffsetVert   = file.read_uint()
        self.NumVert      = file.read_uint()
        self.OffsetFaces  = file.read_uint()
        self.NumFaces     = file.read_uint()
        self.BoneCount    = file.read_ushort()
        self.IndBone      = file.read_ushort()
        self.NumBone      = file.read_ushort()
        self.s1           = file.readArrayUnsignedShort(3)

# TODO read bat and msec		
class DIV:

    def __init__(self, file):
        print("Read Indices")
        self.Indices = file.read_reference_by_id()
        self.Regions = file.read_reference_by_id()
        self.Bat     = file.read_reference_by_id()
        self.Msec    = file.read_reference_by_id()

        #print("M3Div-------------------------------------------")
        #print("Vertex List Count  : " + str(referenceIndices.Count))
        #print("Vertex List Offset : " + hex(referenceIndices.Offset))
        #print("DIV List Count     : " + str(referenceRegions.Count))
        #print("DIV List Offset    : " + hex(referenceRegions.Offset))
        #print("BAT List Count     : " + str(referenceBat.Count))
        #print("BAT List Offset    : " + hex(referenceBat.Offset))
        #print("MSEC List Count    : " + str(referenceMsec.Count))
        #print("MSEC List Offset   : " + hex(referenceMsec.Offset))
        #print("------------------------------------------------")
# VERTEX_TYPE stores the amount of UV per vertex
VERTEX_TYPE = {'VERTEX32':1, 'VERTEX36':2, 'VERTEX40':3, 'VERTEX44':4}
class M3Vertex:
    
    def __init__(self, file, type, flags):
        self.type       = type
        self.Position   = file.read_vector()
        self.BoneWeight = file.read_bytes(4)
        self.BoneIndex  = file.read_bytes(4)
        self.Normal     = file.read_bytes(4)
        self.UV         = []

        # Vertex type specifies how many UV entries the Vertex format contains
        for i in range(VERTEX_TYPE[type]):
            (u, v) = file.readArraySignedShort(2)
            u = u / 2048.0
            v = v / 2048.0
            
            v = 1 - v
            self.UV.append((u,v))
        
        # Further investigation of this flag needed
        if ((flags & 0x200) != 0):
            file.skip_bytes(4)
            
        self.Tangent    = file.read_bytes(4)

class MODL23:
    
    def __init__(self):
        self.Flags = 0
        self.Vertices = []
        self.Faces = []
        self.Materials = []
        
    def read(file):
        m3model         = MODL23()
        m3model.name    = file.read_reference_by_id()
        m3model.version = file.read_uint()
        m3model.SEQS    = file.read_reference_by_id()
        m3model.STC     = file.read_reference_by_id()
        m3model.STG     = file.read_reference_by_id()
        
        file.skip_bytes(0x1c)
        m3model.Bones   = file.read_reference_by_id()
        m3model.d5      = file.read_uint()
        m3model.Flags   = file.read_uint()
        vertexReference = file.read_reference_entry()
        m3model.Div     = file.read_reference_by_id()[0] # expecting only one Div Entry
        m3model.BonesI  = file.read_reference_by_id()
        
        # Bounding Sphere
        vector0 = file.read_vector()
        vector1 = file.read_vector()
        radius  = file.read_float()
        flags   = file.read_uint()
        
        file.skip_bytes(0x3C)
        
        m3model.Attachments      = file.read_reference_by_id()
        m3model.AttachmentLookup = file.read_reference_by_id()
        m3model.Lights           = file.read_reference_by_id()
        m3model.SHBX             = file.read_reference_by_id()
        m3model.Cameras          = file.read_reference_by_id()
        m3model.D                = file.read_reference_by_id()
        m3model.MaterialLookup   = file.read_reference_by_id()
        m3model.Materials        = file.read_reference_by_id()
        m3model.Displacement     = file.read_reference_by_id()
        m3model.CMP              = file.read_reference_by_id()
        m3model.TER              = file.read_reference_by_id()
        #m3model.VOL              = file.read_reference_by_id()
        #m3model.d21              = file.read_uint()
        #m3model.d22              = file.read_uint()
        #m3model.CREP             = file.read_reference_by_id()
        #m3model.PAR              = file.read_reference_by_id()
        #m3model.PARC             = file.read_reference_by_id()
        #m3model.RIB              = file.read_reference_by_id()
        #m3model.PROJ             = file.read_reference_by_id()
        #m3model.FOR              = file.read_reference_by_id()
        #m3model.WRP              = file.read_reference_by_id()
        #m3model.d24              = file.read_uint()
        #m3model.d25              = file.read_uint()
        #m3model.PHRB             = file.read_reference_by_id()
        #m3model.d27              = file.read_uint()
        #m3model.d28              = file.read_uint()
        #m3model.d29              = file.read_uint()
        #m3model.d30              = file.read_uint()
        #m3model.d32              = file.read_uint()
        #m3model.d33              = file.read_uint()
        #m3model.IKJT             = file.read_reference_by_id()
        #m3model.d35              = file.read_uint()
        #m3model.d36              = file.read_uint()
        #m3model.PATU             = file.read_reference_by_id()
        #m3model.TRGD             = file.read_reference_by_id()
        file.skip_bytes(0xD8)
        m3model.IREF             = file.read_reference_by_id()
        
        # Reading Vertices
        count = 0
        type  = 0
    
        if ((m3model.Flags & 0x100000) != 0):   
            count = vertexReference.Count // 44
            type  = 'VERTEX44'
                
        elif ((m3model.Flags & 0x80000) != 0):
            count = vertexReference.Count // 40
            type  = 'VERTEX40'

        elif ((m3model.Flags & 0x40000) != 0):
            count = vertexReference.Count // 36
            type  = 'VERTEX36'

        elif ((m3model.Flags & 0x20000) != 0):
            count = vertexReference.Count // 32
            type  = 'VERTEX32'
                
        else:
            raise Exception('import_m3: !ERROR! Unsupported vertex format. Flags: %s' % hex(m3model.Flags))

            
        print("Reading %s vertices, Flags: %s" % (count, hex(m3model.Flags)))

        file.seek(vertexReference.Offset)
        for i in range(count):
             m3model.Vertices.append(M3Vertex(file, type, m3model.Flags))
        
        submeshes = []
        Div = m3model.Div

        for i, bat in enumerate(Div.Bat):
            regn = Div.Regions[bat.REGN_Index]
            
            offset = regn.OffsetVert
            count  = regn.NumVert
            
            vertices = m3model.Vertices[offset:offset + count]
            faces = []
            
            for j in range(regn.OffsetFaces, regn.OffsetFaces + regn.NumFaces, 3):
                faces.append((Div.Indices[j], Div.Indices[j+1], Div.Indices[j+2]))
                
            submesh = Submesh(vertices, faces, m3model.Materials[m3model.MaterialLookup[bat.MAT_Index].MaterialIndex], m3model.IREF, m3model.Bones)
            submeshes.append(submesh)
            
        
        return submeshes
                    
class M3ReferenceEntry:
    
    def __init__(self, file):
        self.Id     = file.read_id()
        self.Offset = file.read_uint()
        self.Count  = file.read_uint()
        self.Type   = file.read_uint()
        
    # def print(self):
        # DEBUG
        #print("M3ReferenceEntry--------------------------------")
        #print("Id:     " + str(self.Id))
        #print("Offset: " + hex(self.Offset))
        #print("Count:  " + hex(self.Count))
        #print("Type:   " + hex(self.Type))
        #print("------------------------------------------------")
                
class M3Header:

    def __init__(self, file):
        self.id                   = file.read_id()
        
        if self.id != b'MD34':
            raise Exception('import_m3: !ERROR! Unsupported file format: %s' % self.id)
            
        reference_table_offset = file.read_uint()
        reference_table_count  = file.read_uint()
        model_count            = file.read_uint()
        model_index            = file.read_uint()
        
        file.seek(reference_table_offset)
        
        # Creating reference table
        for i in range(reference_table_count):
            file.ReferenceTable.append(M3ReferenceEntry(file))
            
        # Creating models
        modelReference = file.ReferenceTable[model_index]
        
        if (modelReference.Type != 23):
            raise Exception('import_m3: !ERROR! Unsupported model format: %s' % hex(modelReference.Type))

        file.seek(modelReference.Offset)
        
        assert(modelReference.Count == 1)
        self.m3Model = MODL23.read(file)

def createArmatures(bones, irefs):
    bpy.ops.object.add(
        type='ARMATURE', 
        enter_editmode=True, 
        location=[0, 0, 0])
        
    ob       = bpy.context.object
    ob.x_ray = True
    ob.name  = 'SC2Armature'
    
    amt           = ob.data
    amt.name      = 'SC2ArmatureAMT'
    amt.draw_axes = True
    
    bpy.ops.object.mode_set(mode='EDIT')
    
    # building hierarchy
    bone_list = []
    for i, b in enumerate(bones):
        new_bone = amt.edit_bones.new(b.name)
    
        if b.parent is not -1:
            new_bone.parent = bone_list[b.parent]
        
        bone_list.append(new_bone)
        
    # calculating
    for i, b in enumerate(bone_list):
        v = Vector([0, 0, 0, 1])
        m = irefs[i].matrix
        if b.parent is not None:
            b.tail = b.parent.head
        else:
            b.head = Vector([0,0,0])
        b.head = b.tail + (v*m).resize3D()
        #print(b.tail)
    
    #for i, b in enumerate(bone_list):
    #    v = Vector([0,0,0,1])
    #    v = v * irefs[i].matrix
        
    #    parent = bones[i].parent
    #    while parent is not -1:
    #        v = v * irefs[parent].matrix
    #        parent = bones[parent].parent
           
    #    b.head = v.resize3D()
        
    #for i, b in enumerate(bone_list):
    #    if b.parent is not None:
    #        b.tail = b.parent.head
def createNodeMaterial(material):
    mat = bpy.data.materials.new(material.Name)
    mat.use_nodes = True

    diffuse_bsdf = mat.node_tree.nodes['Diffuse BSDF']
    material_out = mat.node_tree.nodes['Material Output']

    for key in material.Layers.keys():
        print("Material: ", key, " Path: ", material.Layers[key].Path)

    # Diffusive
    if ('DIFFUSIVE' in material.Layers):
        layer = material.Layers['DIFFUSIVE']
        tex = createTexture(material.Name + "_DIFFUSIVE", layer.Path)
    
        if tex is not None:
            node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            node.image = tex.image
            mat.node_tree.links.new(diffuse_bsdf.inputs['Color'], node.outputs['Color'])

    # Normal
    if ('NORMAL' in material.Layers):
        layer = material.Layers['NORMAL']
        tex = createTexture(material.Name + "_NORMAL", layer.Path)
    
        if tex is not None:
            node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            node.image = tex.image
            mat.node_tree.links.new(diffuse_bsdf.inputs['Normal'], node.outputs['Color'])
        

    # Emissive
    if ('EMISSIVE' in material.Layers):
        layer = material.Layers['EMISSIVE']
        tex = createTexture(material.Name + "_EMISSIVE", layer.Path)

        if tex is not None:
            node = mat.node_tree.nodes.new('ShaderNodeTexImage')
            emissive = mat.node_tree.nodes.new('ShaderNodeEmission')
            node.image = tex.image
            mat.node_tree.links.new(emissive.inputs['Color'], node.outputs['Color'])
            mixer = mat.node_tree.nodes.new('ShaderNodeMixShader')
            mat.node_tree.links.new(emissive.outputs['Emission'], mixer.inputs[2])
            mat.node_tree.links.new(diffuse_bsdf.outputs['BSDF'], mixer.inputs[1])
            mat.node_tree.links.new(mixer.outputs['Shader'], material_out.inputs['Surface'])
            emissive.inputs['Strength'].default_value = 2.0

    # Emissive and Mixer Node

    return mat


def createMaterial(material):
    mat = bpy.data.materials.new(material.Name)
    
    # Material options
    #mat.shadeless           = not material.flags['UNSHADED']
    mat.use_shadeless           = False
    mat.use_shadows             = not material.flags['NO_SHADOW_RECEIVED']
    mat.use_cast_buffer_shadows = not material.flags['NO_SHADOW_CAST']
    #mat.specular_intensity      = material.specularity
    mat.specular_intensity      = 0.0

    #=============================================================
    # Create Diffusive
    #=============================================================
    if ('DIFFUSIVE' in material.Layers):
        layer = material.Layers['DIFFUSIVE']
        tex = createTexture(material.Name + "_DIFFUSIVE", layer.Path)

        if tex is not None:
            tex.use_alpha = False
            
            slot = mat.texture_slots.add()
            slot.texture               = tex
            slot.texture_coords        = 'UV'
            slot.use_map_diffuse       = True
            slot.use_map_color_diffuse = True
    
    #=============================================================
    # Create Decal
    #=============================================================
    if ('DECAL' in material.Layers):
        layer = material.Layers['DECAL']
        tex = createTexture(material.Name + "_DECAL", layer.Path)

        if tex is not None:
            tex.use_alpha             = True
            tex.extension             = 'CLIP'
            #tex.image.use_premultiply = True
            
            slot = mat.texture_slots.add()
            slot.texture               = tex
            slot.texture_coords        = 'UV'
            slot.use_map_diffuse       = True
            slot.use_map_color_diffuse = True
            slot.uv_layer              = 'UV_1'
    
    #==============================================================
    # Create Specular
    #==============================================================
    if ('SPECULAR in material.Layers'):
        layer  = material.Layers['SPECULAR']
        tex = createTexture(material.Name + "_SPECULAR", layer.Path)

        if tex is not None:
            tex.use_alpha = False
            
            slot = mat.texture_slots.add()
            slot.texture               = tex
            slot.texture_coords        = 'UV'
            slot.use_map_color_diffuse = False   
            slot.use_map_specular      = True
            #slot.use_map_color_spec    = True
            slot.specular_factor       = 0.2
    
    #==============================================================
    # Create Normal
    #==============================================================
    if ('NORMAL' in material.Layers):
        layer = material.Layers['NORMAL']
        tex = createTexture(material.Name + "_NORMAL", layer.Path)

        if tex is not None:
            slot = mat.texture_slots.add()
            slot.texture               = tex # (texture=tex, texture_coordinates='UV', map_to='NORMAL')
            slot.texture_coords        = 'UV'
            slot.use_map_color_diffuse = False
            slot.use_map_normal        = True

    #=============================================================
    # Create Emissive Color
    #=============================================================
    #emissive_layer = material.Layers['EMISSIVE_COLOR']

    #tex = createTexture(material.Name + "_EMISSIVE_COLOR", layer.Path)
    #tex.use_calculate_alpha = True
    #tex.use_alpha           = True
    
    #slot = mat.texture_slots.add()
    #slot.texture               = tex
    #slot.texture_coords        = 'UV'
    #slot.use_map_color_diffuse = True
    #slot.use_map_emit          = False

    #=============================================================
    # Create Emissive
    #=============================================================
    if ('EMISSIVE' in material.Layers):
        layer = material.Layers['EMISSIVE']
        tex = createTexture(material.Name + "_EMISSIVE", layer.Path)

        if tex is not None:
            tex.use_calculate_alpha = True
            tex.use_alpha           = True
            
            slot = mat.texture_slots.add()
            slot.texture               = tex
            slot.texture_coords        = 'UV'
            slot.use_map_color_diffuse = False
            slot.use_map_emit          = True
    
    return mat

def findImage(image_path):
    '''Finds the image on the file system and returns the path, if the
    file exists'''
    filename = basename(image_path)
    
    if os.path.isfile(image_path):
        return image_path

    # Search for filename in all subdirectories
    for prefix, directories, files in os.walk("."):
        if filename in files:
            return prefix + "/" + filename

    return None
    
def createTexture(name, filepath):
        realpath = os.path.abspath(filepath)
        realpath = os.path.normpath(realpath)

        imagepath = findImage(realpath)

        if imagepath:
            tex = bpy.data.textures.new(name, 'IMAGE')
        
            try:
                tex.image = bpy.data.images.load(imagepath)
                print("Importing image: %s ok." % imagepath)

            except Exception as err:
                print("Cannot load texture: %s (%s)" % (realpath, str(err))) 
                return None
        else:
            print("Importing image: %s failed." % basename(realpath))
            return None
        
        return tex
        
class Submesh:

    def __init__(self, vertices, faces, material, iref, bones):
        self.Name = "NONAME"
        self.Vertices = []
        # TODO: maybe better to unflatten here instead of in calling function
        self.Faces = faces
        self.UV = []
        
        self.Material = material
        self.bones = bones
        self.iref = iref
        
        # position in vertices array
        for v in vertices:
            self.Vertices.append(v.Position)
            
        for i, f in enumerate(self.Faces):
            #self.UV1.append(((vertices[f[0]].UV[0]), (vertices[f[1]].UV[0]), (vertices[f[2]].UV[0])))
            
            
            self.UV.append(((vertices[f[0]].UV), (vertices[f[1]].UV), (vertices[f[2]].UV)))

def load(context, filepath, import_material, search_textures):
    file = M3File(filepath)
        
    # Reading file header
    m3Header = M3Header(file)

    name = basename(filepath)
    index = filepath.rfind('Assets')
    if search_textures == True and index is not -1:
        workdir = filepath[0:index]
        os.chdir(workdir)
    else:
        os.chdir(os.path.dirname(filepath))

    for submesh in m3Header.m3Model:
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata(submesh.Vertices, [], submesh.Faces)
        
        mesh.uv_textures.new()
        mesh.uv_textures.new()
        mesh.uv_textures.new()
        mesh.uv_textures.new()
        mesh.uv_textures[0].name = 'UV_0'
        mesh.uv_textures[1].name = 'UV_1'
        mesh.uv_textures[2].name = 'UV_2'
        mesh.uv_textures[3].name = 'UV_3'

        for i, face in enumerate(submesh.UV):
            for l in range(len(face[0])):
                data = mesh.uv_layers[l].data[i]
                mesh.uv_layers[l].data[i*3 + 0].uv = face[0][l]
                mesh.uv_layers[l].data[i*3 + 1].uv = face[1][l]
                mesh.uv_layers[l].data[i*3 + 2].uv = face[2][l]
        
        mesh.update(True)
        ob = bpy.data.objects.new(name, mesh)
        
        if import_material:
            if bpy.context.scene.render.engine == 'BLENDER_RENDER':
                mat = createMaterial(submesh.Material)
                ob.data.materials.append(mat)
            elif bpy.context.scene.render.engine == 'CYCLES':
                mat = createNodeMaterial(submesh.Material)
                ob.data.materials.append(mat)
            
        #createArmatures(submesh.bones, submesh.iref)
            
        #for f in ob.data.faces:
        #    print(f.material_index)
        #    print(f.index)
        
        context.scene.objects.link(ob)

class IMPORT_OT_m3(bpy.types.Operator, ImportHelper):
    '''Import from Blizzard M3 file'''
    bl_idname = "import_shape.m3"
    bl_label  = "Import M3"

    import_material: BoolProperty(name="Create Material", 
                                   description="Creates material for the model", 
                                   default=True)

    search_textures: BoolProperty(name="Search Textures", 
                                  description="Search for textures based on .mpq file structure", 
                                  default=True)
    
    def execute(self, context):
        load(context, 
             self.filepath, 
             self.import_material,
             self.search_textures)

        return {'FINISHED'}


exported_classes = {
    IMPORT_OT_m3,
}
        
def menu_func(self, context):
    self.layout.operator(IMPORT_OT_m3.bl_idname, text="Blizzard M3 (.m3)")

def register():
    for c in exported_classes:
        bpy.utils.register_class(c)
    bpy.types.TOPBAR_MT_file_import.append(menu_func)
def unregister():
    for c in reversed(exported_classes):
        bpy.utils.unregister_class(c)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func)


if __name__ == "__main__":
    register()
