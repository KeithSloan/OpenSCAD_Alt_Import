import FreeCAD, FreeCADGui, os, Part
if FreeCAD.GuiUp:
    import FreeCADGui
    gui = True
else:
    print("FreeCAD Gui not present.")
    gui = False


from OpenSCADdxf import importEZDXFshape #loadDXF

def open(filename,acomp=True,thefaces=False): #options not currently used here
    "called when freecad opens a file."
    print(f"Alternate importer")
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]    
    global doc
    FreeCAD.Console.PrintMessage('Processing : '+filename+'\n')
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith('.dxf'):
        #doc = loadDXF(filename)
        obj = doc.addObject("Part::Feature", objectName)
        obj.Shape = Part.Shape(importEZDXFshape(filename, retcompound=True, retfaces=False))
        FreeCAD.ActiveDocument.recompute()
        return doc
    else:
        FreeCAD.Console.PrintMessage('Not a DXF file : '+filename+'\n')

def insert(filename, docname, acomp=True,thefaces=False):
    "called when freecad imports a file"
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]    
    global doc, f
    try:
        doc=FreeCAD.getDocument(docname)
    except NameError:
        doc=FreeCAD.newDocument(docname)
    #importgroup = doc.addObject("App::DocumentObjectGroup",groupname)        
    if filename.lower().endswith('.dxf'):
        if acomp==True and thefaces==False:
            obj = doc.addObject("Part::Feature", objectName)
            obj.Shape = Part.Shape(importEZDXFshape(filename, retcompound=True, retfaces=False))
        elif acomp==False and thefaces==True:
            obj = doc.addObject("App::DocumentObjectGroup", objectName)        
            f = importEZDXFshape(filename, retcompound=False, retfaces=True)
            f = [Part.show(i) for i in f]
            obj.addObjects(f)
        elif acomp==True and thefaces==True:
            obj1 = doc.addObject("Part::Feature", objectName)    
            obj2 = doc.addObject("App::DocumentObjectGroup", objectName)                 
            c,f = importEZDXFshape(filename, retcompound=True, retfaces=True)
            obj1.Shape = Part.Shape(c)
            f = [Part.show(i) for i in f]
            obj2.addObjects(f)
        FreeCAD.ActiveDocument.recompute()
        return doc
    else:
        FreeCAD.Console.PrintMessage('Not a DXF file : '+filename+'\n')
