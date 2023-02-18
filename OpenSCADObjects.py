#**************************************************************************
#*                                                                         *
#*   Copyright (c) 2023 Keith Sloan <keith@sloan-home.co.uk>               *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         * 
#*   Acknowledgements :                                                    *
#*                                                                         *
#***************************************************************************


# Shared between SCADObject and SCADModule
def createMesh(srcObj, wrkSrc):
    import Part, Mesh, OpenSCADUtils
    import os, tempfile

    print(f"Create Mesh {srcObj.Name} {wrkSrc}")
    try:
        print(f"Source : {srcObj.source}")
        print(f"SourceFile : {srcObj.sourceFile}")
        tmpDir = tempfile.gettempdir()
        tmpOutFile = os.path.join(tmpDir, srcObj.Name+'.stl')
        print(f"Call OpenSCAD")
        print(f"Input file {wrkSrc}")
        print(f"Output file {tmpOutFile}")
        tmpFileName=OpenSCADUtils.callopenscad(wrkSrc, \
            outputfilename=tmpOutFile, outputext='stl')
        print(f"STL File name {tmpFileName}")
        mesh = Mesh.Mesh()
        print(f"files {tmpOutFile} {tmpFileName}")
        mesh.read(tmpFileName)
        #print(dir(mesh))
        print(f"Mesh bound box {mesh.BoundBox}")
        print(f"Count Facets {mesh.CountFacets}")
        #print(f"Facets {mesh.Facets}")
        print(f"Is Solid {mesh.isSolid()}")
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh.Topology, 0.1)
        return shape

    except OpenSCADUtils.OpenSCADError as e:
        #print(f"OpenSCADError {e} {e.value}")
        before = e.value.split('in file',1)[0]
        print(f"Before : {before}")
        after = e.value.rsplit(',',1)[1]
        print(f"After  : {after}")
        after = after.splitlines()[0]
        print(f"After  : {after}")
        print(f"End After")
        srcObj.message = before + after
        print(f"Error Message {srcObj.message}")
        FreeCAD.closeDocument("work")
        srcObj.execute = False

# Source may be procesed
def createBrep(srcObj, tmpDir, wrkSrc):
    import FreeCAD, Part, os, OpenSCADUtils
    from importCSG import  processCSG
    print(f"Create Brep {srcObj.source} {srcObj.fnmax}")
    wrkDoc = FreeCAD.newDocument("work")
    try:
        print(f"Source : {srcObj.source}")
        print(f"SourceFile : {srcObj.sourceFile}")
        print(wrkDoc)
        csgOutFile = os.path.join(tmpDir, srcObj.Name+'.csg')
        brepOutFile = os.path.join(tmpDir, srcObj.Name+'.brep')
        tmpFileName=OpenSCADUtils.callopenscad(wrkSrc, \
            outputfilename=csgOutFile, outputext='csg')
        print(f"CSG File name {tmpFileName}")
        processCSG(wrkDoc, tmpFileName, srcObj.fnmax)
        shapes = []
        for o in wrkDoc.Objects:
            if hasattr(o, "Shape"):
                shapes.append(o.Shape)
        print(f"Shapes in WrkDoc {len(shapes)}")        
        if len(shapes) > 1:
            retShape = Part.makeCompound(shapes)
        else:
            retShape = shapes[0]
        print(f"CreateBrep Shape {retShape}")
        if retShape.isValid():
            retShape.exportBrep(brepOutFile)
            retShape.exportBrep("/tmp/exportBrep.brep")
            #if srcObj.keepFile is not True:
            #    FreeCAD.closeDocument("work")
        else:
            print(f"Make Compound Failed")
            retShape.check()    
        return brepOutFile

    except OpenSCADUtils.OpenSCADError as e:
        #print(f"OpenSCADError {e} {e.value}")
        before = e.value.split('in file',1)[0]
        print(f"Before : {before}")
        after = e.value.rsplit(',',1)[1]
        print(f"After  : {after}")
        after = after.splitlines()[0]
        print(f"After  : {after}")
        print(f"End After")
        srcObj.message = before + after
        print(f"Error Message {srcObj.message}")
        FreeCAD.closeDocument("work")
        srcObj.execute = False


def scanForModules(appendFp, sourceFp, module):
    print(f"Scan for Modules")
    print(FreeCAD.ActiveDocument.Objects)
    for obj in FreeCAD.ActiveDocument.Objects:
        print(f"get Source {obj.Label}")
        # Proxy has functions but need to pass Object with properties
        if hasattr(obj, "Proxy"):
            if hasattr(obj.Proxy, "getSource"):
                src = obj.Proxy.getSource(obj)
                if src is not None:
                    print(f"Module Source : {src}")
                    #source += src
                    appendFp.write(src)

    # Is this a SCADModule
    if module == True:
        print("add mod call")
        src = srcObj.name + '('
        if len(srcObj.variables) > 0:
            for v in srcObj.variables[:-1]:
                src = src + v + ','
                src = src + srcObj.variables[-1]
        src = src +');'
        print(f"mod call {src}")
        appendFp.write(src)
    source = sourceFp.read()
    appendFp.write(source)


def shapeFromSourceFile(srcObj, keepWork=False, module=False, modules=False):
    import os, tempfile
    import FreeCAD, Part, sys
    from importCSG import  processCSG
    global doc
    print(f"shapeFrom Source File : keepWork {keepWork}")
    tmpDir = tempfile.gettempdir()
    if modules == True:
        wrkSrc = os.path.join(tmpDir, srcObj.Name+'.scad')
        #   wrkSrcFp = fopen(wrkSrc)
        #   scanForModules(wrkSrcFp, module)
    else:
        wrkSrc = srcObj.sourceFile

    if srcObj.mode == "Brep":
        brepFile = createBrep(srcObj, tmpDir, wrkSrc)
        print(f"Brep file {brepFile}")
        print(f"keepWork {keepWork}")
        newShape = Part.Shape()
        newShape.read(brepFile)
        print(newShape)
        return newShape

    elif srcObj.mode == "Mesh":
        print(f"wrkSrc {wrkSrc}")
        return createMesh(srcObj, tmpDir, wrkSrc)

# Cannot put in self as SCADlexer is not JSON serializable
# How to make static ???
def parse(obj, src):
    from scadLexer import SCADlexer
    from scadParser import SCADparser
    scadlexer = SCADlexer()
    scadparser = SCADparser(obj, scadlexer)
    parser = scadparser.parser
    #parser.parse(obj.definition, debug=True)
    parser.parse(src)
    #obj.setEditorMode("text",2)


class SCADObject:
    def __init__(self, obj, filename):
        import os, tempfile
        super().__init__()
        obj.addProperty("App::PropertyFile","source","OpenSCAD","OpenSCAD source")
        obj.source = obj.Label+".scad"
        obj.setEditorMode("source",1)
        #tmpDir = obj.Document.TransientDir
        #print(f"Doc temp dir {tmpDir}")
        tmpDir = tempfile.gettempdir()
        #tmpDir = obj.Document.getPropertyByName("TransientDir")
        print(f"Doc temp dir {tmpDir}")
        tmpPath = os.path.join(tmpDir, obj.source)
        print(f"Path {tmpPath}")
        self.copyFile(filename, tmpPath)
        # After creating 
        #dir_list = os.listdir(tmpDir)
        #print("List of directories and files after creation:")
        #print(dir_list)
        obj.addProperty("App::PropertyFile","sourceFile","OpenSCAD","OpenSCAD source")
        obj.sourceFile = tmpPath
        obj.setEditorMode("sourceFile",2)
        obj.addProperty("App::PropertyString","message","OpenSCAD","OpenSCAD message")
        obj.addProperty("App::PropertyBool","modules","OpenSCAD","OpenSCAD Uses Modules")
        obj.addProperty("App::PropertyBool","edit","OpenSCAD","Edit SCAD source")
        obj.addProperty("App::PropertyBool","execute","OpenSCAD","Process SCAD source")
        obj.modules = True
        obj.addProperty("App::PropertyEnumeration","mode","OpenSCAD","mode - create Brep or Mesh")
        obj.mode = ['Brep', 'Mesh']
        obj.mode = 0
        obj.addProperty("App::PropertyInteger","fnmax","OpenSCAD","Max Poylgon - If circle or cylinder has more than this number of sides, treat as circle or cyliner")
        obj.fnmax = 16
        obj.addProperty("App::PropertyBool","mesh_recombine","OpenSCAD","Process SCAD source")
        obj.mesh_recombine = False
        self.obj = obj
        obj.Proxy = self

    def onChanged(self, obj, prop):
        import FreeCAD, FreeCADGui, Part
        print(f"{obj.Label} State : {obj.State} prop : {prop}")

        if "Restore" in obj.State:
            return

        if prop in ["Shape"]:
            print(f"OnChange Shape {obj.Shape}")
            return

        if prop in ["execute"]:
            if obj.execute == True:
                #self.executeFunction(obj)
                obj.message = ""
                print(f"Initial Shape {obj.Shape}")
                self.newShape = shapeFromSourceFile(obj, True, \
                                    modules = obj.modules)
                print(f"Returned Shape {self.newShape}")
                #newShp = shp.copy()
                #print(f"New Shape {newShp}")
                if self.newShape is not None:
                    #obj.Shape = shp.copy()
                    obj.Shape = self.newShape.copy()
                    #obj.Shape = newShp
                else:
                    obj.Shape = Part.Shape()
                print(f"execute Object Shape {obj.Shape}")
                obj.execute = False
                #FreeCADGui.updateGui()
                #FreeCADGui.Selection.addSelection(obj)
                #return
            else:
                print(f"Touched execute Shape {obj.Shape}")
                #obj.Shape = self.newShape


        if prop in ["edit"]:
            if obj.edit == True:
                #obj.message = ""
                #shp = shapeFromSource(obj, modules = obj.modules)
                #if shp is not None:
                #    obj.Shape = shp
                #else:
                #    obj.Shape = Part.Shape()
                #   obj.execute = False
                self.editFile(obj.sourceFile)
                obj.edit = False
            FreeCADGui.Selection.addSelection(obj)

        if prop in ["message"]:
            print("message changed")
            FreeCADGui.updateGui()



    def executeFunction(self, obj, keepWork = False):
        import FreeCADGui, Part
        import os, tempfile
        print(f"Execute {obj.Name} keepWork {keepWork}")
        #print(dir(obj))
        obj.message = ""
        shp = shapeFromSourceFile(obj, keepWork, modules = obj.modules)
        if shp is not None:
            print(f"Initial Shape {obj.Shape}")
            print(f"Returned Shape {shp}")
            shp.check()
            newShp = shp.copy()
            print(f"New Shape {newShp}")
            print(f"Old Shape {shp}")
            #obj.Shape = shp.copy()
            obj.Shape = newShp
        else:
            print(f"Shape is None")
            obj.Shape = Part.Shape()
        print(f"Function Object Shape {obj.Shape}")
        obj.execute = False
        #obj.recompute()
        FreeCADGui.updateGui()
        FreeCADGui.Selection.addSelection(obj)


    def copyFile(self, src, trg):
        print(f"Copy File {src} {trg}")
        fps = open(src,'r')
        fpt = open(trg,'w')
        buffer = fps.read()
        fpt.write(buffer)
        fpt.close()
        fps.close()


    def editFile(self, fname):
        import FreeCAD
        import subprocess,  os, sys
        editorPathName = FreeCAD.ParamGet(\
            "User parameter:BaseApp/Preferences/Mod/OpenSCAD").GetString('externalEditor')
        print(f"Path to external editor {editorPathName}")

        # ToDo : Check pathname valid
        if editorPathName != "":
            p1 = subprocess.Popen( \
                [editorPathName, fname], \
                stdin=subprocess.PIPE,\
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        else:
            print(f"External Editor preference editorPathName not set")



    def createGeometry(self, obj):
        print("create Geometry")    #def getSource(self):
    #    print(f"SCAD Object : get Source")
    #    #print(dir(self))
    #    print(f"Object Source {self.source}")
    #    return self.source

    def execute(self, sp):
        import FreeCADGui
        #FreeCADGui.updateGui()

    def __getstate__(self):
        """When saving the document this object gets stored using Python's json
        module.
        Since we have some un-serializable parts here -- the Coin stuff --
        we must define this method\
        to return a tuple of all serializable objects or None."""
        if hasattr(self, "obj"):
            if hasattr(self.obj, "sourceFile"):
                print(f"Save Source File {self.obj.sourceFile}")
                sf = open(self.obj.sourceFile, 'r')
                buffer = sf.read()
                return {"sourceFile": [self.obj.sourceFile, buffer]}
        else:
            pass

    def __setstate__(self, arg):
        import os, tempfile
        """When restoring the serialized object from document we have the
        chance to set some internals here. Since no data were serialized
        nothing needs to be done here."""
        print(f"Restore {type(arg)} {arg}")
        tmpDir = tempfile.gettempdir()
        sourceName = arg.keys()[0]
        print(f"{arg[sourceName]}")
        sourcePath = os.path.join(tmpDir, soureName)
        print(f"Source Path {sourcePath}")
        fp = open(sourcePath,"w")
        if fp is not None:
            fp.write(arg[sourceName])
        else:
            print(f"Failed to open {sourcePath}")

class SCADLoadFileObject:
        # TO DO
        pass
