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
		self.importType.addItem('Mesh')
		self.importType.addItem('Brep')
		self.importType.addItem('Opt')
		self.layout.addWidget(self.importType)
		self.setLayout(self.layout)

	def getVal(self):
		return self.importType.currentText()

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

	def getVal(self):
		return int(self.value.text())

class BooleanValue(QtGui.QWidget):
	def __init__(self, label, value):
		super().__init__()
		self.layout = QtGui.QHBoxLayout()
		self.label = QtGui.QLabel(label)
		self.value = QtGui.QRadioButton()
		self.value.setChecked(value)
		self.layout.addWidget(self.label)
		self.layout.addWidget(self.value)
		self.setLayout(self.layout)

	def getVal(self):
		if self.value.isChecked():
			return True
		else:
			return False


class OpenSCADimportOptions(QtGui.QDialog):
	def __init__(self,parent=None):
		super(OpenSCADimportOptions, self).__init__(parent)
		self.initUI()

	def initUI(self):
		self.result = None
		# create our window
		# define window           xLoc,yLoc,xDim,yDim
		self.setGeometry(150, 250, 300, 300)
		self.setWindowTitle("FC OpenSCAD import Options")
		self.layout = QtGui.QVBoxLayout()
		self.setMouseTracking(True)
		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, self)
        
	        # Connect the dialog buttons to standard slots
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)
		self.createOnly = BooleanValue('Create Only (Edit)',True)
		self.layout.addWidget(self.createOnly)
		self.importType = ImportType()
		self.layout.addWidget(self.importType)
		self.fnMax = IntegerValue('FnMax', 16)
		self.layout.addWidget(self.fnMax)
		self.timeOut = IntegerValue('TimeOut', 30)
		self.layout.addWidget(self.timeOut)
		self.keepOption = BooleanValue("Keep File",False)
		self.layout.addWidget(self.keepOption)
		self.layout.addWidget(self.buttonBox)
		self.setLayout(self.layout)
		self.show()

	def getValues(self):
		return(
			self.createOnly.getVal(), \
			self.importType.getVal(), \
			self.fnMax.getVal(), \
			self.timeOut.getVal(), \
			self.keepOption.getVal()
			)

	def onCancel(self):
		self.result = 'cancel'
		#QtGui.QGuiApplication.restoreOverrideCursor()

	def onOk(self):
		self.result = 'ok'
		#QtGui.QGuiApplication.restoreOverrideCursor()	

def open(filename):
	import os
	"called when freecad opens a file."
	pathText = os.path.splitext(os.path.basename(filename))
	objectName  = pathText[0]
	filePath = pathText[1]
	FreeCAD.Console.PrintMessage('Creating SCAD File Object from : '+filename+'\n')
	doc=FreeCAD.newDocument(objectName)
	insert(filename,objectName)


def insert(filename, docName):
	"called when freecad inserts a file."
	pathText = os.path.splitext(os.path.basename(filename))
	objectName  = pathText[0]
	doc = FreeCAD.getDocument(docName)
	QtGui.QGuiApplication.setOverrideCursor(QtGui.Qt.ArrowCursor)
	dialog = OpenSCADimportOptions()
	result = dialog.exec_()
	QtGui.QGuiApplication.restoreOverrideCursor()
	if result == QtGui.QDialog.Accepted:
		print(f"Result {dialog.result}")
		print(f"Action")
		options = dialog.getValues()
		print(f"Options {options}")

		# Create SCAD Object
		obj = doc.addObject("Part::FeaturePython", objectName)
		#
		#scadObj = SCADBase(obj, filename, mode='Mesh', fnmax=16, timeout=30)
		# change SCADBase to accept single options call ?
		#
		scadObj = SCADBase(obj, filename, options[1], \
			options[2], options[3], options[4])
		ViewSCADProvider(obj.ViewObject)
		
		if hasattr(obj, 'Proxy'):
			if options[0] == False:
				obj.Proxy.executeFunction(obj)
			elif options[0] == True:
				obj.Proxy.editFile(filename)
		#FreeCAD.ActiveDocument.recompute()
		#obj.recompute()
		doc.recompute()
		FreeCADGui.SendMsgToActiveView("ViewFit")
		#view.sendMessage("ViewFit")