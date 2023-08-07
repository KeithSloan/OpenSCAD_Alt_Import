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

import FreeCAD, FreeCADGui, Part, Mesh, OpenSCADUtils
import os, sys, tempfile

from OpenSCADdxf import importEZDXFshape


class DXFBase:
    def __init__(self, obj, filename):
        super().__init__()
        obj.addProperty("App::PropertyFile","source","DXF-Object","DXF source")
        obj.source = obj.Label+".dxf"
        obj.setEditorMode("source",1)
        obj.addProperty("App::PropertyFile","sourceFile","DXF-Object","DXF source File")
        obj.sourceFile = filename
        #obj.setEditorMode("sourceFile",2)
        obj.addProperty("App::PropertyString","message","DXF-Object","DXF-Objectmessage")
        obj.addProperty("App::PropertyBool","edit","DXF-Object","Edit DXF")
        obj.addProperty("App::PropertyBool","execute","DXF-Object","Process DXF source")
        #self.obj = obj
        obj.Proxy = self
        self.createGeometry(obj)

    def onChanged(self, fp, prop):
        print(f"{fp.Label} State : {fp.State} prop : {prop}")

        if "Restore" in fp.State:
            return

        if prop in ["Shape"]:
            print(f"OnChange Shape {fp.Shape}")
            return

        if prop in ["execute"]:
            if fp.execute == True:
                self.executeFunction(fp)
                fp.execute = False
            else:
                print(f"Touched execute Shape {fp.Shape}")
                #obj.Shape = self.newShape


        if prop in ["edit"]:
            if fp.edit == True:
                self.editFile(fp.sourceFile)
                fp.edit = False
            FreeCADGui.Selection.addSelection(fp)

        if prop in ["message"]:
            print("message changed")
            FreeCADGui.updateGui()


    def execute(self, fp):
        '''Do something when doing a recomputation, this method is mandatory'''
        print(f"execute")


    def executeFunction(self, obj):
        from timeit import default_timer as timer
        print(f"Execute {obj.Name}")
        #start = timer()
        #print(dir(obj))
        obj.message = ""
        shp = importEZDXFshape(obj.sourceFile)
        if shp is not None:
            print(f"Initial Shape {obj.Shape}")
            print(f"Returned Shape {shp}")
            #shp.check()
            #newShp = shp.copy()
            #print(f"New Shape {newShp}")
            #print(f"Old Shape {shp}")
            #obj.Shape = newShp
            #if isinstance(shp, tuple): #MattC commented out 20230807 0838
            #    obj.Shape = shp[0]
            #else:
            #    obj.Shape = shp
        else:
            print(f"Shape is None")
            obj.Shape = Part.Shape()
        print(f"Function Object Shape {obj.Shape}")
        obj.execute = False
        #end = timer()
        #print(f"==== Create Shape took {end-start} secs ====")    
        #obj.recompute()
        FreeCAD.ActiveDocument.recompute()
        FreeCADGui.Selection.addSelection(obj)
        FreeCADGui.SendMsgToActiveView("ViewFit")
        # Need to update Gui for properties change
        # try and catch as puts out warning
        try:
            obj.execute = False
            FreeCADGui.updateGui()
        except err:
            print(f"Warning {err}")
        #FreeCADGui.Selection.addSelection(obj)


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
            "User parameter:BaseApp/Preferences/Mod/OpenSCAD").GetString('externalDXFeditor')
        print(f"Path to external DXF editor {editorPathName}")
        # ToDo : Check pathname valid
        if editorPathName != "":
            p1 = subprocess.Popen( \
                [editorPathName, fname], \
                stdin=subprocess.PIPE,\
                stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        else:
            print(f"External DXF Editor preference editorPathName not set")


    def createGeometry(self, obj):
        import FreeCAD, Part
        print("create Geometry")    #def getSource(self):
        print("Do not process DXF source on Document recompute")
        return

        print(f"Active Document {FreeCAD.ActiveDocument.Name}")
        #shp = shapeFromSourceFile(obj, keepWork, modules = obj.modules)
        shp = shapeFromSourceFile(obj, modules = obj.modules)
        print(f"Active Document {FreeCAD.ActiveDocument.Name}")
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

class DXFObject(DXFBase):
    def __init__(self, obj, filename):
        import FreeCAD, os, tempfile, Part
        super().__init__(obj, filename)
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
        obj.sourceFile = tmpPath
        obj.setEditorMode("sourceFile",2)

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


class ViewDXFProvider:
    def __init__(self, obj):
        """Set this object to the proxy object of the actual view provider"""
        obj.Proxy = self


    def updateData(self, fp, prop):
        """If a property of the handled feature has changed we have the chance to handle this here"""
        pass

    def getDisplayModes(self, obj):
        """Return a list of display modes."""
        # print("getDisplayModes")
        modes = []
        modes.append("Shaded")
        modes.append("Wireframe")
        modes.append("Points")
        return modes


    def getDefaultDisplayMode(self):
        """Return the name of the default display mode. It must be defined in getDisplayModes."""
        return "Shaded"

    def setDisplayMode(self, mode):
        """Map the display mode defined in attach with those defined in getDisplayModes.\
               Since they have the same names nothing needs to be done. This method is optional"""
        return mode


    def onChanged(self, vp, prop):
        """Here we can do something when a single property got changed"""
        print(f"View Provider OnChanged : prop {prop}")


    def getIcon(self):
        """Return the icon in XPM format which will appear in the tree view. This method is\
               optional and if not defined a default icon is shown."""

    def __getstate__(self):
        """When saving the document this object gets stored using Python's json
        module.
        Since we have some un-serializable parts here -- the Coin stuff --
        we must define this method\
        to return a tuple of all serializable objects or None."""
        return None

    def __setstate__(self, arg):
        """When restoring the serialized object from document we have the
        chance to set some internals here. Since no data were serialized
        nothing needs to be done here."""
        pass
