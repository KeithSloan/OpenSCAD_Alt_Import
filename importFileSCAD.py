#***************************************************************************
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
__title__="FreeCAD OpenSCAD Workbench - CSG importer SCAD Object"
__author__ = "Keith Sloan <keith@sloan-home.co.uk>"
__url__ = ["http://www.sloan-home.co.uk/ImportSCAD"]

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

from PySide import QtGui, QtCore

#import OpenSCADObjects
#import importCSG
from OpenSCADObjects import SCADBase, ViewSCADProvider

from importAltCSG import processCSG

params = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OpenSCAD")
printverbose = params.GetBool('printverbose',False)
print(f'Verbose = {printverbose}')

class ImportType(QtGui.QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QtGui.QHBoxLayout()
		self.label = QtGui.QLabel('Import Type')
		self.layout.addWidget(self.label)
		self.importType = QtGui.QComboBox()
		self.importType.addItem('Brep')
		self.importType.addItem('Mesh')
		self.importType.addItem('Opt')
		self.layout.addWidget(self.importType)
		self.setLayout(self.layout)

class IntegerValue(QtGui.QWidget):
	def __init__(self, label, value):
		super().__init__()
		self.layout = QtGui.QHBoxLayout()
		self.label = QtGui.QLabel(label)
		self.value = QtGui.QLineEdit()
		self.value.setText(str(value))
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.value)
		self.setLayout(self.layout)

class Buttons(QtGui.QWidget):
	def __init__(self):
		super().__init__()
		self.layout = QtGui.QHBoxLayout()
		# cancel button
		cancelButton = QtGui.QPushButton('Cancel', self)
		cancelButton.clicked.connect(self.onCancel)
		cancelButton.setAutoDefault(True)
		self.layout.addWidget(cancelButton)

		# OK button
		okButton = QtGui.QPushButton('Okay', self)
		okButton.clicked.connect(self.onOk)
		self.layout.addWidget(okButton)
		self.setLayout(self.layout)

	def onCancel(self):
		self.result = 'cancel'

	def onOk(self):
		self.result = 'ok'

class OpenSCADimportOptions(QtGui.QDialog):
	def __init__(self):
	#def __init__(self, parent):
		super(OpenSCADimportOptions, self).__init__()
		self.initUI()

	def initUI(self):
		self.result = None
		# create our window
		# define window           xLoc,yLoc,xDim,yDim
		self.setGeometry(150, 250, 300, 300)
		self.setWindowTitle("FC OpenSCAD import Options")
		self.setMouseTracking(True)
		self.layout = QtGui.QVBoxLayout()
		self.layout.addWidget(ImportType())
		self.layout.addWidget(IntegerValue('FnMax', 16))
		self.layout.addWidget(IntegerValue('TimeOut', 30))
		self.layout.addWidget(Buttons())
		self.setLayout(self.layout)
		self.show()


def open(filename,currentdoc=None):
    "called when freecad opens a file."
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]
    dialog = OpenSCADimportOptions()
    dialog.exec_()
    print(f"Result {dialog.result}")
    if dialog.result is not None :
    	FreeCAD.Console.PrintMessage('Creating SCAD File Object from : '+filename+'\n')
    	#doc = FreeCAD.ActiveDocument
    	if currentdoc is None:
        	doc=FreeCAD.newDocument(objectName)    
    	else:
        	doc=FreeCAD.getDocument(currentdoc)    
    	if doc is None:
        	doc=FreeCAD.newDocument(filename)

    	obj = doc.addObject("Part::FeaturePython", objectName)
    	scadObj = SCADBase(obj, filename, mode='Mesh', fnmax=16, timeout=30)
    	ViewSCADProvider(obj.ViewObject)
    	if hasattr(obj, 'Proxy'):
        	obj.Proxy.executeFunction(obj)
    	FreeCAD.ActiveDocument.recompute()
    	FreeCADGui.SendMsgToActiveView("ViewFit")
    
def insert(filename, currentdoc):
    open(filename, currentdoc)
