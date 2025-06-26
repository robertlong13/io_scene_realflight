# RealFlight FBX Exporter

Blender addon for exporting FBX files for creating custom models in
RealFlight. This based on the included FBX exporter by Campbell Barton,
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

## Porting Guide
This plugin needs to be updated for at least every new minor version of Blender.
I will document the process here, mostly for myself (I am going to be better try
to keep on top of this at least every 6 months), but if someone wants to open a
PR to fix this plugin when they notice it is broken, this should help them.

This plugin is a minor modification of the included FBX exporter in Blender.
The changes are as follows:
- `__init__.py`
  - Remove the file import ability
  - Change some default values of some settings
  - Change the default axis orientation to Z-up, Y-forward
- `data_types.py`
  - Unchanged
- `encode_bin.py`
  - Unchanged
- `export_fbx_bin.py`
  - Add a new property to `fbx_data_element_custom_properties` to export a
    property named "UDP3DSMAX". 3DS Max uses this property to store custom
    properties on objects, and that's where RealFlight looks for things labeled
    with "NUP_" for things like landing gear, bay doors, flashing lights, etc.
      - Properties in Blender named "NUP_" will automatically be added to the
        "UDP3DSMAX" property
      - The "UDP3DSMAX" property can also be set directly as a string, and
        "\r\n" is properly escaped as a newline
  - Dial down the default shininess from 20 to 0.1
  - Fix the scaling. RealFlight uses 1 unit = 1 inch.
- `fbx_utils.py`
  - Unchanged

The easiest way to port is to copy the 5 files from the new Blender version, then diff `__init__.py` and `export_fbx_bin.py` with the version in the corresponding old Blender release and manually apply those changes to the new version.