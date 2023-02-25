import FreeCAD as App
import FreeCADGui as Gui
import os


def joinDir(path):
    import os

    __dirname__ = os.path.dirname(__file__)
    return os.path.join(__dirname__, path)

    Gui.addIconPath(joinDir("Resources/icons"))

def addTools():
    from NewSCADCommands import SCADLibsFeature

    Gui.addIconPath(joinDir("Resources/icons"))
    Gui.activateWorkbench("OpenSCADWorkbench")
    wb = Gui.getWorkbench("OpenSCADWorkbench")
    if wb is not None:
        print(f"Adding Tools {wb}")
        #Gui.addCommand("SCADLibsCommand", SCADLibsFeature())
        wb.appendToolbar("NewSCAD",['SCADLibsCommand'])
        print(f"Toolbars {wb.listToolbars()}")
        #Gui.activateWorkbench("OpenSCADWorkbench")
        wb.reloadActive()
        Gui.updateGui( )

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
