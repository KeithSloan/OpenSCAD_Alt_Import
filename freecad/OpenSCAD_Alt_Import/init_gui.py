import FreeCAD
FreeCAD.addImportType("New Importer : CSG (*.csg)","importCSG")
FreeCAD.addImportType("New Importer : SCAD (*.scad)","importCSG")
FreeCAD.addImportType("New Importer : ScadObject (*.scad)","importSCAD")
FreeCAD.addImportType("New Importer : ScadFileObject (*.scad)","importFileSCAD")

import OpenSCADLibs as osl
osl.addTools()

