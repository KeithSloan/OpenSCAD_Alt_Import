# OpenSCAD
Inprocess : Installable version of FreeCAD OpenSCAD workbench.

#Install : To install in a version of FreeCAD which comes with the old OpenSCAD workbench

* remove current ../Mod/OpenSCAD directory
* change to ../Mod
* git clone https://github.com/KeithSloan/OpenSCAD.git

For linux FreeCAD is installed in /usr/lib/freecad so OpenSCAD directory is /usr/lib/freecad/Mod/OpenSCAD
and you will have to prefix commands with sudo

#branch : IndicatMinkowski

A trial version of importer that if minkowski request is for two objects, colour codes then
rather than use OpenSCAD binary to produce mesh of minkowski.

The idea being that a FreeCAD user can then make changes to the indicated objects i.e. Add fillets before deleting other object etc.
