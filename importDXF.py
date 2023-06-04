import FreeCAD, os, Part
if FreeCAD.GuiUp:
    import FreeCADGui
    gui = True
else:
    print("FreeCAD Gui not present.")
    gui = False

# from PySide2 import QtGui, QtCore
from PySide import QtGui, QtCore    

if FreeCADGui:
    try:
        _encoding = QtGui.QApplication.UnicodeUTF8

        def translate(context, text):
            "convenience function for Qt translator"
            return QtGui.QApplication.translate(context, text, None, _encoding)
    except AttributeError:
        def translate(context, text):
            "convenience function for Qt translator"
            return QtGui.QApplication.translate(context, text, None)

    
from OpenSCADdxf import importEZDXFshape

def listOfLayers(filename):
    # return a list of layers
    # dummy return
    return(['Layer1', 'Layer2', 'layer3'])


class layerEntry(QtGui.QWidget):

    def __init__(self, layerName):
        super().__init__()
        print(f'layer Entry : {layerName}')
        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(QtGui.QLabel("Layer : "))
        self.layerName = layerName
        self.hbox.addWidget(QtGui.QLabel(self.layerName))
        self.option = QtGui.QComboBox()
        self.option.addItems(['Sketch','Plain'])
        self.hbox.addWidget(self.option)
        self.setLayout(self.hbox)

class layerScrollList(QtGui.QScrollArea):

    def __init__(self, layerList):
        super().__init__()
        print(f'Init Scroll List {layerList}')
        # Scroll Area which contains the widgets, set as the centralWidget
        # Widget that contains the collection of Vertical Box
        self.widget = QtGui.QWidget()
        self.vbox = QtGui.QVBoxLayout()
        self.layerList = layerList
        for layer in layerList:
            self.addEntry(layer)
        # The Vertical Box that contains the Horizontal Boxes of  labels and buttons
        self.widget.setLayout(self.vbox)

        # Scroll Area Properties
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setWidget(self.widget)

    def addEntry(self, layerName):
        print(f'Add Entry {layerName}')
        self.vbox.addWidget(layerEntry(layerName))


class importOptions(QtGui.QDialog):
    def __init__(self, filename, layerList):
        super(importOptions, self).__init__()
        self.initUI(layerList)

    def initUI(self, layerList):
        #self.result = userCancelled
        # create our window
        # define window           xLoc,yLoc,xDim,yDim
        print(f'import Options')
        self.setGeometry(150, 450, 350, 450)
        self.setWindowTitle("DXF Import Options")
        #self.setMouseTracking(True)
        mainLayout = QtGui.QVBoxLayout(self)
        listLayout = QtGui.QVBoxLayout(self)
        self.layerList = layerScrollList(layerList)
        self.buttonAction = QtGui.QPushButton(translate('Import', 'Action'))
        self.buttonAction.clicked.connect(self.onAction)
        self.buttonCancel = QtGui.QPushButton(translate('Import', 'Cancel'))
        self.buttonCancel.clicked.connect(self.onCancel)
        buttonLayout = QtGui.QHBoxLayout(self)
        buttonLayout.addWidget(self.buttonAction)
        buttonLayout.addWidget(self.buttonCancel)
        listLayout.addWidget(self.layerList)
        mainLayout.addLayout(listLayout)
        mainLayout.addLayout(buttonLayout)
        # now make the window visible
        self.setLayout(mainLayout)
        self.show()

    def getOption(self, layerName):
        print(f'Get option {layerName}')
        print(f'scroll list {self.layerList}')
        print(dir(self.layerList.vbox))
        #print(f'children {self.layerList.vbox.children()}')
        print(f'Number {self.layerList.vbox.count()}')
        #print(f'Contents {self.layerList.vbox.dumpObjectTree()}')
        #print(f'Contents {self.layerList.vbox.dumpObjectInfo()}')
        print(f'Layout {self.layerList.vbox.layout()}')
        print(f'Layout {dir(self.layerList.vbox.layout())}')
        for idx in range(self.layerList.vbox.count()):
            item = self.layerList.vbox.layout().itemAt(idx)
            #entry = item.widget.itemAt(idx)
            #print(f'Layer Name : {itementry.layerName}')
            #print(f'Layer Name : {entry.layerName}')
            #print(f'Option : {entry.option}')
            print(f'item {dir(item)}')
            print(f'item widget {item.widget}')
            print(dir(item.widget))
            print(item.widget.itemAt(0))
            #print(item.widget.itemAt(1))
            #print(item.widget.itemAt(2))
            #print(f'Layer {item.layerName}')
            #print(f'Option {item.entryOptions}')


    def onAction(self):
        print(f'On Action')
        print(f'Process file')
        self.getOption('Layer1')


    def onCancel(self):
        #self.result = userCancelled
        self.close()

def open(filename,acomp=True,thefaces=False): #options not currently used here
    "called when freecad opens a file."
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]    
    global doc
    FreeCAD.Console.PrintMessage('Processing : '+filename+'\n')
    docname = os.path.splitext(os.path.basename(filename))[0]
    doc = FreeCAD.newDocument(docname)
    if filename.lower().endswith('.dxf'):
        layerList = listOfLayers(filename)
        dialog = importOptions(filename, layerList)
        dialog.exec_()
        #doc = loadDXF(filename)
        #obj = doc.addObject("Part::Feature", objectName)
        #obj.Shape = Part.Shape(importEZDXFshape(filename, retcompound=True, retfaces=False))
        FreeCAD.ActiveDocument.recompute()
        return doc
    else:
        FreeCAD.Console.PrintMessage('Not a DXF file : '+filename+'\n')

def insert(filename, docname, acomp=True,thefaces=False):
    "called when freecad imports a file"
    pathText = os.path.splitext(os.path.basename(filename))
    objectName  = pathText[0]
    filePath = pathText[1]    
    global doc, f
    try:
        doc=FreeCAD.getDocument(docname)
    except NameError:
        doc=FreeCAD.newDocument(docname)
    #importgroup = doc.addObject("App::DocumentObjectGroup",groupname)        
    if filename.lower().endswith('.dxf'):
        layerList = listOfLayers(filename)
        dialog = importOptions(filename, layerList)
        dialog.exec_()
        #if acomp==True and thefaces==False:
        #    obj = doc.addObject("Part::Feature", objectName)
        #    obj.Shape = Part.Shape(importEZDXFshape(filename, retcompound=True, retfaces=False))
        #elif acomp==False and thefaces==True:
        #    obj = doc.addObject("App::DocumentObjectGroup", objectName)        
        #    f = importEZDXFshape(filename, retcompound=False, retfaces=True)
        #    f = [Part.show(i) for i in f]
        #    obj.addObjects(f)
        #elif acomp==True and thefaces==True:
        #    obj1 = doc.addObject("Part::Feature", objectName)    
        #    obj2 = doc.addObject("App::DocumentObjectGroup", objectName)                 
        #    c,f = importEZDXFshape(filename, retcompound=True, retfaces=True)
        #    obj1.Shape = Part.Shape(c)
        #    f = [Part.show(i) for i in f]
        #    obj2.addObjects(f)
        FreeCAD.ActiveDocument.recompute()
        return doc
    else:
        FreeCAD.Console.PrintMessage('Not a DXF file : '+filename+'\n')

