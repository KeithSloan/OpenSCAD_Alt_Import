## Alternate OpenSCAD Importer

### NOTICES

Functions such as PrismaticToroid require facilities in the FreeCAD version 0.20 of Part


### Installation

Note Addon manager no longer works in FreeCAD 0.18 due to changes in Github
     use FreeCAD 0.19 instead.

* Invoke the Addon Manager - Tools | Adddon manager
* Select Configure..
* Into Custom respositories enter https://github.com/KeithSloan/OpenSCAD_Alt_Import.git
* Then OK
* Restart FreeCAD

## Installation with FreeCAD 0.20

Use FreeCAD preferences to add the Repro to available 'Custom Repositories'

![Image 13-02-2022 at 12 55](https://user-images.githubusercontent.com/2291247/153757512-fedad170-7d27-4c5f-9618-8b68ca2b6b24.jpeg)

Invoke the Addon Manager - Tools | Addon manager


Click on 'Refresh local cache'

Then install

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
