# RealFlight FBX Exporter

Blender addon for exporting FBX files for creating custom models in
RealFlight 8. This based on the included FBX exporter by Campbell Barton,
Bastien Montagne, and Jens Restemeier.

Features:
* Properly handle exporting Realflight properties on objects
  * Properties beginning with "NUP_" will automatically be added to the
  "UDP3DSMAX" property
  * The "UDP3DSMAX" property can also be set directly as a string, and "\r"
  is properly escaped as a carriage return
* By default, 1 Blender Unit exports to 1 meter in RealFlight
  * This can be changed using the scale paramter in the export dialog or by
  setting a unit scale factor in the scene settings
* ~~Specular hardness is properly mapped to the range expected by RealFlight~~
  * ~~Hardness of 1 maps to a Gloss value of 0%~~
  * ~~Hardness of 501 maps to a Gloss value of 100%~~
  * Blender 2.8 changed the way it handles shininess. I haven't looked into it. I've left the mapping the way that Blender's built-in FBX exporter does it.
