## Alternate OpenSCAD Importer

### Installation

Note Addon manager no longer works in FreeCAD 0.18 due to changes in Github
     use FreeCAD 0.19 instead.

* Invoke the Addon Manager - Tools | Adddon manager
* Select Configure..
* Into Custom respositories enter https://github.com/KeithSloan/OpenSCAD_Alt_Import.git
* Then OK
* Restart FreeCAD

### Use

With the workbench installed when opening a File the user will be prompted with which
version to use.

### Changes from standard Importer

**Minkowski** for two objects are colour coded red & green
              rather than use the OpenSCAD binary to produce a meshed minkowski.
              The idea being that a FreeCAD user can then make changes to the indicated objects
              i.e. Add fillets etc to the Red object before deleting the green object.

**Hull** requests for two 2D objects are dealt with as a **Loft** between rather that handled as Meshes.
