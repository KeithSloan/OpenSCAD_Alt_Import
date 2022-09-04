## Alternate OpenSCAD Importer

### NOTICES

Functions such as PrismaticToroid require facilities in the FreeCAD version 0.20 of Part

## Installation

It can be installed via the [Addon Manager](https://github.com/FreeCAD/FreeCAD-addons) (from Tools menu)


## Alternative Installation

Clone into FreeCAD's Mod directory see https://wiki.freecadweb.org/Installing_more_workbenches

   * Change to FreeCAD Mod directory
   * **git clone https://github.com/KeithSloan/OpenSCAD_Alt_Import.git**

* Start/Restart FreeCAD


### Use

With the workbench installed when opening a CSG or SCAD File with 

        FreeCAD | File | Open 

the user will be prompted with which importer to use.

### Changes from standard Importer

* **Minkowski** for two objects are colour coded red & green
              rather than use the OpenSCAD binary to produce a meshed minkowski.
              The idea being that a FreeCAD user can then make changes to the indicated objects
              i.e. Add fillets etc to the Red object before deleting the green object.

* **Hull** A limited number of hull requests are converted to BREP equivalents
              
              - Collinear cylinders & cones
              - Two Spheres
              - Two Parallel Cylinders of equal length, orthogonaly displaced.
               
           others are dealt with as per standard importer i.e passed to OpenSCAD
           executable to create a Mesh
                      
### Thanks to FreeCAD Users

* wmayer
* chennes
* edwilliams16
