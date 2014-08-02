Summary
=======

This site hosts the blendm3 add-on for Blender, a open source 3D
content creation suite. With the release of Starcraft II Blizzard
introduced a new model format (.m3). This add-on allows you to load
this files and associated textures into Blender and work with them.

Blender is currently under heavy development. Due to this fact, the
internal add-on API is not stable and can change during releases. The
project focuses to be compliant with the newest Blender releases. This
means, the add-on will not work with the current 2.53 beta release
available from http://www.blender.org. To use this add-on you should
try the newes builds which are available from
http://www.graphicall.org. You should also regularly check this
website for updates. New features are continuously added. The project
aims to fully support the .m3 file format. Please report any issues
with the add-on in the Issues tab.

Latest Release
==============

0.15 on 2014-08-02

* New release after reviving the Project
* Adapted to work with current version of Blender 2.71

0.14 on 2010-09-07

* Works now with Blender from trunk (tested with release 31786)
* Can now be used with the Blender add-on installer
* Option to search for texture asserts added
* Much more improved import of material (diffuse, specular, emissive and normal)
* Added import of decal texture layer
* Imports now all UV layers 

Full version history here.

Features
========

The add-on currently supports

* Geometry
* UV texture
* Diffusive, Specular, Emissive and Normal maps
* Decals 

Further Reading
===============
* Installation Instructions
* Version History 

Screenshots
===========
![][screenshot]

Full list of screenshots here.

Acknowledgment
==============

This plugin would not be possible with the tons of information about
the .m3 provided by the libm3 project. The project homepage is
'http://code.google.com/p/libm3/' and is a great source for
information about the file format. Also a big thank NiNtoxicated who
developed a 3DS Max plugin which is also a great source to understand
the .m3 file format.

[screenshot]: https://raw.github.com/wiki/stante/blendm3/images/colossus_uv_render_editing_small.png
 "Colossus uv render"
