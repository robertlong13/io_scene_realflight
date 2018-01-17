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

Upcoming Features:
* Option to remap specular parameters to 3ds Max ranges
* Option to remove numbers appended to the end of duplicate names
	* e.g., rename ~CS_COLL.012 to ~CS_COLL
