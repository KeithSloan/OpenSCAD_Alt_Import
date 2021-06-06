import sys
# add folder containing FreeCAD.pyd, FreeCADGui.pyd to sys.path
#sys.path.append("C:/Program Files/FreeCAD 0.18/bin") # example for Windows
#sys.path.append("/usr/lib/freecad-daily/lib") # example for Linux
#sys.path.append("/usr/lib/freecad-daily/Mod") # example for Linux
#sys.path.append("/usr/lib/freecad/lib") # example for Linux
sys.path.append("/Applications/FreeCAD 0.19.1.app/Contents/Resources/lib") # exas8mple for Mac
sys.path.append("/Applications/FreeCAD 0.19.1.app/Contents/Resources/lib/python3.8/site-packages") # example for Mac
sys.path.append("/Applications/FreeCAD 0.19.1.app/Contents/Resources/Mod") # example for Mac
import FreeCAD
import FreeCADGui
import Part
#import Draft
import Import

print(dir(Import))

if len(sys.argv)<3:
  print ("Usage: sys.argv[0] <in_file> <out_file>")
  sys.exit(1)

iname=sys.argv[1]
oname=sys.argv[2]

print('Importing : '+iname)
FreeCAD.loadFile(iname)
App.ActiveDocument.saveAs('/tmp/saveFC')
# iterate through all objects
expObjCol = []
for obj in App.ActiveDocument.Objects:
  print('Object : '+obj.Name)
  print(obj.Visibility)
  print(dir(obj))
  # if hasattr(obj,'ViewObject') and hasattr(obj,'Shape') :
  #   print(obj.ViewObject)
  if obj.Visibility == True :
     print('Export : '+obj.Name)
     print(obj.ViewObject)
     col = obj.ViewObject.ShapeColor
     colors = [ col for i in range(len(obj.Shape.Faces))]
     expObjCol.append((obj, colors))

print('Exporting STEP file : '+oname)
print('This can be a very slow process')
print('for large files Please be patient')
#Import.export([o],"/tmp/test4.step")
print(len(expObjCol))
Import.export(expObjCol,oname)
sys.exit(0)
