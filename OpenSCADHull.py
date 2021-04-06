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
        print('Hull Object Group : '+str(obj.Group))
        if not obj.Group:
            obj.Shape = Part.Shape()
        elif len(obj.Group) == 1:
            obj.Shape = obj.Group[0].Shape
        else:
            print('Update Shape??')
            #obj.Shape = obj.Group[0].Shape.fuse(
            #        [o.Shape for o in obj.Group[1:]]).removeSplitter()
            obj.Shape = createHull(obj)

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

def checkObjShape(obj) :
    print('Check Object Shape')
    if obj.Shape.isNull() == True :
       print('Shape is Null - recompute')
       obj.recompute()

def chk2D(obj) :
    return  obj.Shape.Volume == 0

def chkLoftable(obj) :
    print('chkLoftable : '+obj.TypeId)
    if obj.TypeId == 'Part::Cylinder' or \
       obj.TypeId == 'Part::Cone' :
       return True
    else :
       return False

def chkDisplaced(obj1, obj2) :
    a = obj1.Placement.Base
    b = obj2.Placement.Base
    return obj1.Height < b.sub(a).Length

def getWire(obj) :
    d = obj.Placement.Base + obj.Placement.Rotation.Axis.multiply(obj.Height)
    if obj.TypeId == 'Part::Cylinder' :
       r = obj.Radius
    elif obj.TypeId == 'Part::Cone' :
       if d.Length < 0 :
          r = obj.Radius1
       else :
          r = obj.Radius2
    return d, Part.makeCircle(r)

def hullTwoEqCircles(obj1, obj2) :
    print('hullTwoEqCircles')
    r = obj1.Radius
    v1 = obj1.Placement.Base
    v2 = obj2.Placement.Base
    v3 = (v1 + v2) / 2
    l1 = Part.makeLine(v1,v2)
    n1 = l1.normalAt(v1)
    n2 = l1.normalAt(v2)
    t1 = n1.valueAt(r)
    t2 = n1.valueAt(-r)
    s1 = n2.valueAt(r)
    s2 = n2.valueAt(-r)
    l2 = Part.makeLine(t1,t2)
    l3 = Part.makeLine(s1,s2)
    return obj1

def hullTwoCircles(obj1, obj2, name) :
    print('hullTwoCircles')
    # Thanks to wmayer
    # swap obj1 and obj2 so that obj1 is the bigger circle
    if obj2.Radius > obj1.Radius:
        obj2, obj1 = obj1, obj2

    print(obj1.Radius)
    #print(dir(obj1.Radius))
    #print(dir(obj1.Placement))
    #print(dir(obj1.Placement.Rotation))
    c1 = Part.Circle(obj1.Placement.Base, obj1.Placement.Rotation.Axis, \
         obj1.Radius.getValueAs('mm'))
    c2 = Part.Circle(obj2.Placement.Base, obj2.Placement.Rotation.Axis, \
         obj2.Radius.getValueAs('mm'))

    # helper circle located at c1
    c3 = Part.Circle()
    #c3.Center = obj1.Center
    c3.Center = obj1.Placement.Base
    c3.Radius = obj1.Radius - obj2.Radius

    # get the mid point of the line from the center of c1 to c2
    #v1 = obj1.Center
    #v2 = obj2.Center
    v1  = obj1.Placement.Base
    v2  = obj2.Placement.Base
    v3  = (v1 + v2) / 2

    # Thales circle that is located in v3 and goes through
    #  the center points of c1 and c2
    c4 = Part.Circle()
    c4.Center = v3
    c4.Radius = (v1 - v2).Length / 2

    # Intersections of Thales and helper circle
    p1, p2 = c4.intersect(c3)
    t1 = c3.parameter(FreeCAD.Vector(p1.X,p1.Y,p1.Z))
    t2 = c3.parameter(FreeCAD.Vector(p2.X,p2.Y,p2.Z))

    import math
    # for the big circle we need the long arc
    #a1 = obj1.Shape.trim(t2,math.pi*2+t1)
    a1 = c1.trim(t2,math.pi*2+t1)
    a1s = a1.toShape()
    # for the small circle we need the short arc
    #a2 = obj2.Shape.trim(t1,t2)
    a2 = c2.trim(t1,t2)
    a2s = a2.toShape()
    # the edges to connect the end points of the arcs
    l1 = Part.makeLine(c1.value(t1),c2.value(t1))
    l2 = Part.makeLine(c2.value(t2),c1.value(t2))
    wire = Part.Wire([a1.toShape(), l1, a2.toShape(), l2])
    print(wire)
    #face = Part.makeFace(wire)
    face = Part.Face(wire)
    return face

def hullTwoEqSpheres(obj1, obj2) :
    print('hullTwoEqSpheres')
    return obj1

def hullTwoSpheres(obj1, obj2) :
    print('hullTwoSpheres')
    # Same as two circles then revolve
    # Thanks to wmayer
    # swap obj1 and obj2 so that obj1 is the bigger circle
    if obj2.Radius > obj1.Radius:
        obj2, obj1 = obj1, obj2

    print(obj1.Radius)
    #print(dir(obj1.Radius))
    #print(dir(obj1.Placement))
    #print(dir(obj1.Placement.Rotation))
    c1 = Part.Circle(obj1.Placement.Base, obj1.Placement.Rotation.Axis, \
         obj1.Radius.getValueAs('mm'))
    c2 = Part.Circle(obj2.Placement.Base, obj2.Placement.Rotation.Axis, \
         obj2.Radius.getValueAs('mm'))

    # helper circle located at c1
    c3 = Part.Circle()
    #c3.Center = obj1.Center
    c3.Center = obj1.Placement.Base
    c3.Radius = obj1.Radius - obj2.Radius

    # get the mid point of the line from the center of c1 to c2
    #v1 = obj1.Center
    #v2 = obj2.Center
    v1  = obj1.Placement.Base
    v2  = obj2.Placement.Base
    v3  = (v1 + v2) / 2

    # Thales circle that is located in v3 and goes through
    #  the center points of c1 and c2
    c4 = Part.Circle()
    c4.Center = v3
    c4.Radius = (v1 - v2).Length / 2

    # Intersections of Thales and helper circle
    p1, p2 = c4.intersect(c3)
    t1 = c3.parameter(FreeCAD.Vector(p1.X,p1.Y,p1.Z))
    t2 = c3.parameter(FreeCAD.Vector(p2.X,p2.Y,p2.Z))
    t3 = (t1+t2) / 2

    import math
    # for the big circle we need the long arc
    #a1 = obj1.Shape.trim(t2,math.pi*2+t1)
    #a1 = c1.trim(t2+math.pi, t1 +2*math.pi)
    a1 = c1.trim(t3+math.pi,t1+2*math.pi)
    a1s = a1.toShape()
    # for the small circle we need the short arc
    #a2 = obj2.Shape.trim(t1,t2)
    a2 = c2.trim(t1,t3)
    a2s = a2.toShape()
    # the edges to connect the end points of the arcs
    l1 = Part.makeLine(c1.value(t1),c2.value(t1))
    l2 = Part.makeLine(c2.value(t2),c1.value(t3+math.pi))
    wire = Part.Wire([a1.toShape(), l1, a2.toShape(), l2])
    print(wire)
    #face = Part.makeFace(wire)
    #face = Part.Face(wire)
    #Part.show(face)
    #axisLine = v2.sub(v1)
    base = c1.value(t3 + math.pi)
    axisLine = c2.value(t3) - base
    return(wire.revolve(base,axisLine))
    #return(face.revolve(v3,FreeCAD.Vector(0,0,1),180))

    #return(face.revolve(v3,axisLine,360))
    #return(face.revolve(FreeCAD.Vector(0,0,0),axisLine,360))
    #return(face.revolve(face.CenterOfMass,axisLine,360))
    #return face.revolve(v1,v2,360)

def hullTwoEqSpheres(obj1, obj2) :
    print('hullTwoEqSpheres')
    #   print(dir(p[5][0].Shape))
    #   a = p[5][0].Shape.CenterOfMass
    #   b = p[5][1].Shape.CenterOfMass
    #   print('a : '+str(a))
    #   print('b : '+str(b))
    #   plane1 = planeFromNormalPoints(a,b)
    #   myloft = doc.addObject('Part::Plane',p[1])
    #   myloft.Length = 100
    #   myloft.Width = 50
    #   myloft.Placement.Base = a
    #   myloft.Placement.Rotation = FreeCAD.Rotation(FreeCAD.Vector(0.0,1.0,0.0),90)
    #   #myloft.Shape = plane1
    #   print(dir(myloft))
    #   print(dir(plane1))
    #   #myloft = doc.addObject('Part::Loft',p[1])
    #   #myloft.Sections = [p[5][0], p[5][1]]
    #   #print(dir(myloft))
    #   lofted = True
    #if lofted == False :
    return obj1

def chkParallel(obj1, obj2):
    print('check Parallel')
    rot1   = obj1.Placement.Rotation
    print(rot1)
    rot2 = obj2.Placement.Rotation
    print(rot2)
    # true if rot1 = rot2
    #return abs((rot1.multiply(rot2.inverted())).Angle) < 1e-15
    return FreeCAD.Rotation.isSame(rot1, rot2, 1e-15)

def perpendicular(obj) :
    m1 = obj1.Placement.Rotation.Matrix
    return(FreeCAD.Placement(m1.invert))

def hullLoft(wire1, wire2, name) :
    print('Loft')
    loftShape = Part.makeLoft([wire1,wire2])
    #myLoft = doc.addObject('Part::Loft',name)
    #myLoft.Shape = loftShape
    #myLoft.Solid = False
    #myLoft.Ruled = False
    #myLoft.Closed = False
    #return myLoft
    return loftShape

def createHull(obj) :
    hShape = None
    if len(obj.Group) == 2 :
       obj1 = obj.Group[0]
       obj2 = obj.Group[1]
       print(obj1.TypeId)
       print(obj1.Label)
       print(obj1.Placement)
       print(obj2.TypeId)
       print(obj2.Label)
       print(obj2.Placement)
       checkObjShape(obj1)
       checkObjShape(obj2)
       #print(dir(obj1))
       #print(dir(obj2))
       if chk2D(obj1) and chk2D(obj2) :
          if obj1.Radius == obj2.Radius :
             return hullTwoEqCircles(obj1,obj2)
          else :
             return hullTwoCircles(obj1,obj2,obj.Name)

       if obj1.TypeId == 'Part::Sphere' and obj2.TypeId == 'Part::Sphere' :
          return hullTwoSpheres(obj1,obj2)

       elif chkParallel(obj1,obj2) :
          print('Parallel')
          #if chkConcentric(obj1,obj2) :
          #if obj1.Placement.Rotation == obj2.Placement.Rotation :
          if chkLoftable(obj1) and chkLoftable(obj2) :
             print('Loftable')
             if chkDisplaced(obj1,obj2) :
                print('Loft Displaced')
                d1, wire1 = getWire(obj1)
                d2, wire2 = getWire(obj2)
                wire1.translate(d1)
                wire2.translate(d2)
                return hullLoft(wire1,wire2,obj.Name)

             else :
                print('Loft Overlapped')
          print('Not Loftable')

    print('Not directly handled')
    #from OpenSCADFeatures import CGALFeature
    #myObj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython','Fred')
    #CGALFeature(myObj,'hull',obj.Group)
    # import OpenSCADFeatures
    #return myObj.Shape
    import OpenSCADUtils
    return OpenSCADUtils.process_ObjectsViaOpenSCADShape(FreeCAD.ActiveDocument,\
    obj.Group,'hull',maxmeshpoints=None)

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
