import FreeCAD, FreeCADGui, Part
from pivy import coin

class Hull(object):
    def __init__(self, obj=None):
        self.Object = obj
        if obj:
            self.attach(obj)

    def __getstate__(self):
        return

    def __setstate__(self,_state):
        return

    def attach(self,obj):
        obj.addExtension('App::GeoFeatureGroupExtensionPython')
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        self.Object = obj

    def execute(self, obj):
        if not obj.Group:
            obj.Shape = Part.Shape()
        elif len(obj.Group) == 1:
            obj.Shape = obj.Group[0].Shape
        else:
            print('Update Shape??')
            #obj.Shape = obj.Group[0].Shape.fuse(
            #        [o.Shape for o in obj.Group[1:]]).removeSplitter()

class ViewProviderMyGroup(object):
    def __init__(self,vobj=None):
        if vobj:
            vobj.Proxy = self
        else:
            self.ViewObject = None

    def attach(self,vobj):
        vobj.addExtension('Gui::ViewProviderGeoFeatureGroupExtensionPython')
        self.ViewObject = vobj
        try:
            vobj.SwitchNode.defaultChild = 1
        except Exception:
            pass

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def __getstate__(self):
        return None

    def __setstate__(self, _state):
        return None

class ViewProviderMyGroupEx(ViewProviderMyGroup):
    def __init__(self,vobj=None):
        self.group_node = None
        super(ViewProviderMyGroupEx, self).__init__(vobj)

    def attach(self,vobj):
        super(ViewProviderMyGroupEx, self).attach(vobj)
        self.setupShapeGroup()

    def setupShapeGroup(self):
        vobj = self.ViewObject
        if getattr(self, 'group_node', None) or \
                vobj.SwitchNode.getNumChildren() < 2:
            return
        self.group_node = vobj.SwitchNode.getChild(0)
        for i in range(1, vobj.SwitchNode.getNumChildren()):
            node = coin.SoSeparator()
            node.addChild(self.group_node)
            node.addChild(vobj.SwitchNode.getChild(i))
            vobj.SwitchNode.replaceChild(i,node)

    def getDetailPath(self,subname,path,append):
        if not subname or not getattr(self, 'group_node', None):
            raise NotImplementedError
        subs = Part.splitSubname(subname)
        objs = subs[0].split('.')

        vobj = self.ViewObject
        mode = vobj.SwitchNode.whichChild.getValue()
        if mode <= 0:
            raise NotImplementedError

        if append:
            path.append(vobj.RootNode)
            path.append(vobj.SwitchNode)

        node = vobj.SwitchNode.getChild(mode);
        path.append(node)
        if mode > 0:
            if not objs[0]:
                path.append(node.getChild(1))
            else:
                path.append(node.getChild(0))
        if not objs[0]:
            return vobj.getDetailPath(subname,path,False)

        for child in vobj.claimChildren():
            if child.Name == objs[0]:
                sub = Part.joinSubname('.'.join(objs[1:]),subs[1],subs[2])
                return child.ViewObject.getDetailPath(sub,path,True)

    def getElementPicked(self,pp):
        if not getattr(self, 'group_node', None):
            raise NotImplementedError
        vobj = self.ViewObject
        path = pp.getPath()
        if path.findNode(self.group_node) < 0:
            raise NotImplementedError
        for child in vobj.claimChildren():
            if path.findNode(child.ViewObject.RootNode) < 0:
                continue
            return child.Name + '.' + child.ViewObject.getElementPicked(pp)

    def onChanged(self,_vobj,prop):
        if prop == 'DisplayMode':
            self.setupShapeGroup()

def makeHull(list, ex=False):
    doc = FreeCAD.ActiveDocument
    if not doc:
        doc = FreeCAD.newDocument()
    hullObj = doc.addObject('Part::FeaturePython', 'hull')
    Hull(hullObj)
    if ex:
        ViewProviderMyGroupEx(hullObj.ViewObject)
    else:
        ViewProviderMyGroup(hullObj.ViewObject)
    hullObj.Group = list
    hullObj.recompute()
    return hullObj
