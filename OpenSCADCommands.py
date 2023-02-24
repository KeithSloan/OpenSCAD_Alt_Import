import FreeCAD, FreeCADGui
from PySide import QtCore

class SCADLibsFeature:

    def Activated(self):
        #from PySide import QtGui, QtCore

        print(f"Add SCADLibs icons")
        return

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True

    def GetResources(self):
        return {
            "Pixmap": "SCADLibsFeature",
            "MenuText": QtCore.QT_TRANSLATE_NOOP(
                "SCADLibsFeature", "Add access to SCAD Libs"
            ),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP(
                "SCADLibsFeature", "Add SCAD Libs Icon"
            ),
        }

FreeCADGui.addCommand("SCADLibsCommand", SCADLibsFeature())
