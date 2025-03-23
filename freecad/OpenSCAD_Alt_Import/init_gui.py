import FreeCAD
FreeCAD.addImportType("New Importer : CSG (*.csg)","importAltCSG")
FreeCAD.addImportType("New Importer : SCAD (*.scad)","importAltCSG")
FreeCAD.addImportType("New Importer : ScadObject (*.scad)","importSCAD")
FreeCAD.addImportType("New Importer : ScadFileObject (*.scad)","importFileSCAD")
FreeCAD.addImportType("New Importer : Scad2Sheet (*.scad)","parse2Sheet")
FreeCAD.addImportType("New Importer : DXF (*.dxf)","importAltDXF")
FreeCAD.addImportType("New Importer : DxfObject (*.dxf)","importDXFObj")
#FreeCAD.addImportType("New Importer : DxfFileObject (*.scad)","importFileDXFObj")
FreeCAD.addExportType("New Exporter : exportCSG (*.csg)","exportAltCSG")

