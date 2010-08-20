blendm3 - Blender plugin to work with Blizzard .m3 files


The latest version of this plugin and additional information can be found 
on this site:

    http://code.google.com/p/blendm3/
	
You should regularly check this website for updates. New features are 
continuously added. The project aims to fully support the .m3 file 
format.


=== History
0.12 Alexander Stante (stante_at_gmail_dot_com)
  * Support for all vertex formats added.

0.11 Alexander Stante (stante_at_gmail_dot_com)
  * Error handling improved.
  
0.10 Alexander Stante (stante_at_gmail_dot_com)
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

To install the plugin just copy the file 'import_shape_m3.py' into your
blender plugin directory. After restarting Blender the import menu should
contain a 'Blizzard M3 (.m3)' entry. The plugin is tested with Blender
version 2.53.