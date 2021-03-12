# RealFlight FBX Exporter

Blender addon for exporting FBX files for creating custom models in
RealFlight 8. This based on the included FBX exporter by Campbell Barton,
Bastien Montagne, and Jens Restemeier.

Features:
* Properly handle exporting Realflight properties on objects
  * Properties beginning with "NUP_" will automatically be added to the
  "UDP3DSMAX" property
  * The "UDP3DSMAX" property can also be set directly as a string, and "\r\n"
  is properly escaped as a newline
* By default, 1 Blender Unit exports to 1 meter in RealFlight
  * This can be changed using the scale paramter in the export dialog or by
  setting a unit scale factor in the scene settings
