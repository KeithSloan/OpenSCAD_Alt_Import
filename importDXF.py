import FreeCAD, os

from OpenSCADdxf import loadDXF

def open(filename):
    "called when freecad opens a file."
    global doc
    FreeCAD.Console.PrintMessage('Processing : '+filename+'\n')
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith('.dxf'):
        doc = loadDXF(filename)
        return doc
    else:
        FreeCAD.Console.PrintMessage('Not a DXF file : '+filename+'\n')


def insert(filename, docname):
    "called when freecad imports a file"
    global doc
    try:
        doc=FreeCAD.getDocument(docname)
    except NameError:
        doc=FreeCAD.newDocument(docname)
    #importgroup = doc.addObject("App::DocumentObjectGroup",groupname)        
    if filename.lower().endswith('.dxf'):
        doc = loadDXF(filename)
        return doc
    else:
        FreeCAD.Console.PrintMessage('Not a DXF file : '+filename+'\n')

