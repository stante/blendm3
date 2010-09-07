blendm3 - Blender plugin to work with Blizzard .m3 files


The plugin is created by Alexander Stante (stante_at_gmail_dot_com). The 
latest version of this plugin and additional information can be found on this 
site:

    http://code.google.com/p/blendm3/
	
You should regularly check this website for updates. New features are 
continuously added. The project aims to fully support the .m3 file 
format.

The Blender API is currently not stable and is subject to change. Therefore
I decided to not rely on the API of the official 2.53 Beta from 
http://www.blender.org but to use newer builds from http://www.graphicall.org.
The plugin has be tested to work with build r31786.

If your found any errors, bugs or if you have suggestions for improvements 
feel free to contact me.

=== History

0.14 
  * Works now with Blender from trunk (tested with r31786)
  * Can now be used with the Blender addon installer
  * Option to search for texture asserts added
  * Much more improved import of material (diffuse, specular, emissive and 
    normal)
  * Added import of decal texture layer
  * Imports now all UV layers

0.13
  * Support for material import added
  * Normals, Emissive and Diffusive are supported

0.12
  * Support for all vertex formats added.

0.11
  * Error handling improved.
  
0.10
  * Basic support for reading geometry.
  

=== Acknowledgment

This plugin would not be possible with the tons of information about the
.m3 provided by the libm3 project. The project homepage is 
'http://code.google.com/p/libm3/' and is a great source for information
about the file format. Also a big thank NiNtoxicated who developed a
3DS Max plugin which is also a great source to understand the .m3 file
format.


=== Installation

The following files are included with the distribution of the plugin:

.
|-- COPYING              Copy of the GPLv2 license.
|-- README.TXT           Description and installation instruction.
`-- import_shape_m3.py   The actual plugin.

To install the plugin download the archive and extract the contents into
a folder. From Blender go to 'File->User Prefeences...->Add-Ons'. Click
on 'Install Add-On...' and select the file 'import_shape_m3.py'. These
steps installs the add-on.

To activate the add-on go to 'Import/Export' in the same tab and activate
the 'Import/Export: Import Blizzard M3 Models(.m3)' by activating the 
checkbox.

After these steps the plugin shoud show off in 'File->Import->Blizzard M3(.m3)'

=== Usage

To work with the plugin and use all textures, the best way is to extract all
the contents of the .mpq archives shipped with Starcraft 2 into a directory.
This archives contains the models (.m3) and textures (.dds). If you open
a model from within the extracted archive, the textures will be automatically
found if you turn on the 'Search Textures' option (which is set by default).

If the option 'Search Textures' is turned off, the textures will be searched
relatively from the directory where the model (.m3) is stored. 

Note: 
The textures are usually stored in the directory 'Assets/Textures'. If the
option 'Search Textures' is not set, the plugin searches for the 
'Assets/Textures' directory relativley from the directory the model is loaded. 

If the option 'Search Textures' is set, the plugin searches for the 'Assets' 
directory in your path and then sets the working directory accordingly. If you
extract the whole contents of an .mpq directory, it is suggested to set this 
option.