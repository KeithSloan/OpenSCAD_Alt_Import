#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2023 Keith Sloan <keith@sloan-home.co.uk>               *
#*             (c) 2023 Matt Considine                                     *
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

__title__="FreeCAD Alternate OpenSCAD Workbench - importer DXF Object"
__author__ = "Keith Sloan <keith@sloan-home.co.uk>"
__url__ = ["http://www.sloan-home.co.uk/ImportDxfObj"]

#import FreeCAD, Part, Draft, io, os, sys, xml.sax
import FreeCAD, FreeCADGui, os
if FreeCAD.GuiUp:
    import FreeCADGui
    gui = True
else:
    print("FreeCAD Gui not present.")
    gui = False

# Save the native open function to avoid collisions
if open.__module__ in ['__builtin__', 'io']:
    pythonopen = open

from DXFObjects import DXFObject, ViewDXFProvider

'''
def open(filename):
    "called when freecad opens a file."
    FreeCAD.Console.PrintMessage('Creating Object from : '+filename+'\n')
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]
    print(f"Create Object {objectName} path {filename}")
    doc = FreeCAD.ActiveDocument
    if doc is None:
        doc=FreeCAD.newDocument(filename)
    obj = doc.addObject("Part::FeaturePython", objectName)
    DXFObject(obj, filename)
    ViewDXFProvider(obj.ViewObject)
    if hasattr(obj, 'Proxy'):
        obj.Proxy.executeFunction(obj)
    FreeCAD.ActiveDocument.recompute()
    FreeCADGui.SendMsgToActiveView("ViewFit")
'''
def open(filename,currentdoc=None):
    "called when freecad opens a file."
    FreeCAD.Console.PrintMessage('Creating Object from : '+filename+'\n')
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]
    print(f"Create Object {objectName} path {filename}")
    #doc = FreeCAD.ActiveDocument
    if currentdoc is None:
        doc=FreeCAD.newDocument(objectName)    
    else:
        doc=FreeCAD.getDocument(currentdoc)
    obj = doc.addObject("Part::FeaturePython", objectName) #vs Feature?? MattC
    DXFObject(obj, filename)
    ViewDXFProvider(obj.ViewObject)
    if hasattr(obj, 'Proxy'):
        obj.Proxy.executeFunction(obj)
    FreeCAD.ActiveDocument.recompute()
    FreeCADGui.SendMsgToActiveView("ViewFit")

def insert(filename, currentdoc):
    open(filename, currentdoc)
