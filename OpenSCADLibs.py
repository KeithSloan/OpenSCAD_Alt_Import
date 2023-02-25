import FreeCAD as App
import FreeCADGui as Gui
import os


def joinDir(path):
    import os

    __dirname__ = os.path.dirname(__file__)
    return os.path.join(__dirname__, path)

def init():
    Gui.addIconPath(joinDir("Resources/icons"))

def addCommand():
    from NewSCADCommands import SCADLibsFeature

    wb = Gui.getWorkbench("OpenSCADWorkbench")
    if wb is not None:
        Gui.addCommand("SCADLibsCommand", SCADLibsFeature())
        print(dir(wb))
        # addIconPath
        # addIcon
        #sclibs = Gui.addCommand("SCADLibsCommand", SCADLibsCommand)
        #print(sclibs)

def listWBs():
    print(Gui.listWorkbenches())

class accessLibs:
    def Activated(self):
        print(f"Access Libs Active")

    def IsActive(self):
        if FreeCAD.ActiveDocument is None:
            return False
        else:
            return True
    def GetResources(self):
        return {
            "Pixmap": "OpenSCADaccessLibsesetWorld",
            "MenuText": QtCore.QT_TRANSLATE_NOOP(
                "GDML_ResetWorld", "Resize World to contain all volumes"
            ),
            "ToolTip": QtCore.QT_TRANSLATE_NOOP(
                "GDML_ResetWorld", "Resize World to contain all volumes"
            ),
        }        
