import FreeCAD, FreeCADGui, os, pathlib, platform
from PySide import QtCore, QtGui


if FreeCAD.GuiUp:
    try:
        _encoding = QtGui.QApplication.UnicodeUTF8

        def translate(context, text):
            "convenience function for Qt translator"
            return QtGui.QApplication.translate(context, text, None, _encoding)

    except AttributeError:

        def translate(context, text):
            "convenience function for Qt translator"
            return QtGui.QApplication.translate(context, text, None)

class SCADLibsFeature:

    def Activated(self):
        #from PySide import QtGui, QtCore

        print(f"Add SCADLibs icons")
        self.getLibPath()
        self.getRootLibs()
        self.dialog = OpenSCADLibsDialog()
        self.dialog.setRootLibs(self.rootLibs)
        self.dialog.exec()
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
            self.scadLibPath = scadPath
        else:
            print(f"Library {scadPath} not found")

    def getRootLibs(self):
        print(f"Get Root Libs")
        libs = []
        for entry in os.scandir(self.scadLibPath):
            if entry.is_dir():
                #print(f"Entry {entry}")
                #print(dir(entry))
                libs.append(entry.name)
        self.rootLibs = sorted(libs)        
        print(f"Root Libs {self.rootLibs}")


class OpenSCADLibsDialog(QtGui.QDialog):
    def __init__(self,  *args):
        super(OpenSCADLibsDialog, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(translate("OpenSCAD", "OpenSCAD Libraries"))
        #self.setGeometry(self.left, self.top, self.width, self.height)
        self.setGeometry(50,50,400,200)
        self.libsGroup = QtGui.QGroupBox("Selected Library")
        self.Vlayout = QtGui.QVBoxLayout()
        self.Vlayout.addWidget(self.libsGroup)
        self.setLayout(self.Vlayout)

    def setRootLibs(self, rootsList):
        self.rootLibs = QtGui.QComboBox(self.libsGroup)
        self.rootLibs.addItems(rootsList)



FreeCADGui.addCommand("SCADLibsCommand", SCADLibsFeature())
