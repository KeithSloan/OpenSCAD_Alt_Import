import FreeCAD, FreeCADGui, os, pathlib, platform
from PySide import QtCore


class SCADLibsFeature:

    def Activated(self):
        #from PySide import QtGui, QtCore

        print(f"Add SCADLibs icons")
        self.getLibPath()
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

    def getLibPath(self):
        plat = platform.system()
        home = pathlib.Path.home()
        print(f"Platform {plat} Home {home}")
        osDict = {'linux':'.local/share/OpenSCAD/libraries', \
                    'Darwin': 'Documents/OpenSCAD/libraries', \
                    'Windows': 'My Documents\OpenSCAD\libraries'}
        scadPath = osDict.get(plat)
        if plat in ['linux','Darwin']:
            scadPath = os.path.join(home, scadPath)            
        print(f"OpenSCAD Library Path {scadPath}")
        #if os.path.exists(scadPath):
        if os.path.isdir(scadPath):
            return scadPath
        else:
            print(f"Library {scadPath} not found")
            


FreeCADGui.addCommand("SCADLibsCommand", SCADLibsFeature())
