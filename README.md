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

Upcoming Features:
* Option to remap specular parameters to 3ds Max ranges
* Option to remove numbers appended to the end of duplicate names
	* e.g., rename ~CS_COLL.012 to ~CS_COLL
