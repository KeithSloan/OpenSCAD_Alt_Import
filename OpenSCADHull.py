import FreeCAD, FreeCADGui, Part


from FreeCAD import Units
from pivy import coin

printverbose = False

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
        print('attach')
        obj.addExtension('App::GeoFeatureGroupExtensionPython')
        obj.Proxy = self

    def onDocumentRestored(self, obj):
        self.Object = obj

    def execute(self, obj):
        print('Hull execute : '+obj.Label)
        # Group jas been set to items on stack at time of hull request
        if hasattr(obj,'Group') :
           print('Has Group')
           if len(obj.Group) > 1 :
              obj.Shape = createHull(obj.Group)
              print(f"return from execute")
              return
        else :
           print('Error Invalid hull request')

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
    #print('Check Object Shape')
    if obj.Shape.isNull() == True :
       if printverbose: print(f'{obj.Name} Shape is Null - recompute')
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

def getHeight(obj) :
    if hasattr(obj,'Height') :
       return obj.Height
    if hasattr(obj,'Radius') :
       return obj,Radius
    if hasattr(obj,'Radius1') :
       return obj,Radius1

def chkDisplaced(obj1, obj2) :
    a = obj1.Placement.Base
    b = obj2.Placement.Base
    lenApart = b.sub(a).Length
    height = getHeight(obj1)
    return lenApart > height

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

def hullTwoEqCircles(obj1, obj2, flag2D) :
    # Used by 2D and Cylinder
    print('hullTwoEqCircles')
    r = obj1.Radius
    print(f"(Radius : {r}")
    v1 = obj1.Placement.Base
    v2 = obj2.Placement.Base
    nm = someNormal(v1 - v2)
    #print(f"Normal {nm}")
    ln = v1-v2
    dv = ln.cross(nm)
    #print(f"dv {dv}")
    dn = dv.normalize()
    #print(f"Normalised {dn}")
    dr = dn.multiply(r)
    #print(f"dr : {dr}")
    t11 = v1.sub(dr)
    #print(t11)
    t12 = v1.add(dr)
    t21 = v2.add(dr)
    t22 = v2.sub(dr)
    l1 = Part.makeLine(t11,t12)
    l2 = Part.makeLine(t12,t21)
    l3 = Part.makeLine(t21,t22)
    l4 = Part.makeLine(t22,t11)
    wire = Part.Wire([l1,l2,l3,l4])
    #print(wire)
    #face = Part.makeFace(wire)
    face = Part.Face(wire)
    #return(face)
    if flag2D:
        return obj1.Shape.fuse(face.fuse(obj2.Shape))
    else:
        s1 = Part.makeCircle(obj1.Radius,obj1.Placement.Base)
        s2 = Part.makeCircle(obj2.Radius,obj2.Placement.Base)    
        return s1.fuse(face.fuse(s2))

def hullTwoCircles(obj1, obj2, flag2D) :
    print(f'hullTwoCircles 2D {flag2D}')
    if obj1.Radius == obj2.Radius :
       return(hullTwoEqCircles(obj1, obj2, flag2D))

    # Thanks to wmayer
    # swap obj1 and obj2 so that obj1 is the bigger circle
    if obj2.Radius.Value > obj1.Radius.Value:
        obj2, obj1 = obj1, obj2
    print(f"Hull Two Circles r1 {obj1.Radius.Value} r2 {obj2.Radius.Value}")
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
    print(f"Two Circles Wire {wire}")
    #face = Part.makeFace(wire)
    face = Part.Face(wire)
    return face

def hullTwoEqSpheres(obj1, obj2) :
    print('hullTwoEqSpheres')
    vh = obj2.Placement.Base - obj1.Placement.Base
    #print(vh.Length)
    #mycyl = Part.makeCylinder(obj1.Radius,vh.Length)
    mycyl = Part.makeCylinder(obj1.Radius,vh.Length,obj1.Placement.Base,vh,360)
    return mycyl

def someNormal(v):
    'Return some unit vector normal to v'
    xaxis = FreeCAD.Vector(1, 0, 0)
    yaxis = FreeCAD.Vector(0, 1, 0)
    zaxis = FreeCAD.Vector(0, 0, 1)
    axes =[xaxis, yaxis, zaxis]
    if v.Length <= 1e-15:
        return zaxis
    else:
        for axis in axes:
            vc = v.normalize().cross(axis)
            if vc.Length > 0.5: # at least one must be >= sqrt(2/3)
                break
        return vc.normalize()

def hullSphereCyclinderEqRad(obj0, obj1):
    myComp = Part.makeCompound([obj1, obj0])
    return myComp
    
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

    #find normal to working plane
    n = someNormal(obj1.Placement.Base - obj2.Placement.Base)
    c1 = Part.Circle(obj1.Placement.Base, n, \
         obj1.Radius.getValueAs('mm'))
    c2 = Part.Circle(obj2.Placement.Base, n, \
         obj2.Radius.getValueAs('mm'))

    # helper circle located at c1
    #c3 = Part.Circle()
    #c3.Center = obj1.Center
    #c3.Center = obj1.Placement.Base
    #c3.Radius = obj1.Radius - obj2.Radius
    c3 = Part.Circle(obj1.Placement.Base, n, \
        obj1.Radius - obj2.Radius)                        

    # get the mid point of the line from the center of c1 to c2
    #v1 = obj1.Center
    #v2 = obj2.Center
    v1  = obj1.Placement.Base
    v2  = obj2.Placement.Base
    v3  = (v1 + v2) / 2

    # Thales circle that is located in v3 and goes through
    #  the center points of c1 and c2
    #c4 = Part.Circle()
    #c4.Center = v3
    #c4.Radius = (v1 - v2).Length / 2
    c4 = Part.Circle(v3, n, (v1-v2).Length/2)

    # Intersections of Thales and helper circle
    p1, p2 = c4.intersect(c3)
    t1 = c3.parameter(FreeCAD.Vector(p1.X,p1.Y,p1.Z))
    t2 = c3.parameter(FreeCAD.Vector(p2.X,p2.Y,p2.Z))
    t3 = (t1+t2) / 2

    from math import pi
    # for the big circle we need the long arc
    #a1 = obj1.Shape.trim(t2,pi*2+t1)
    #a1 = c1.trim(t2+pi, t1 +2*pi)
    a1 = c1.trim(t3+pi,t1+2*pi)
    a1s = a1.toShape()
    # for the small circle we need the short arc
    #a2 = obj2.Shape.trim(t1,t2)
    a2 = c2.trim(t1,t3)
    a2s = a2.toShape()
    # the edges to connect the end points of the arcs
    l1 = Part.makeLine(c1.value(t1),c2.value(t1))
    l2 = Part.makeLine(c2.value(t3),c1.value(t3+pi))
    wire = Part.Wire([a1.toShape(), l1, a2.toShape(), l2])
    print(wire)
    #face = Part.makeFace(wire)
    #face = Part.Face(wire)
    #Part.show(face)
    #axisLine = v2.sub(v1)
    base = c1.value(t3 + pi)
    axisLine = c2.value(t3) - base
    return(wire.revolve(base,axisLine))
    #return(face.revolve(v3,FreeCAD.Vector(0,0,1),180))

    #return(face.revolve(v3,axisLine,360))
    #return(face.revolve(FreeCAD.Vector(0,0,0),axisLine,360))
    #return(face.revolve(face.CenterOfMass,axisLine,360))
    #return face.revolve(v1,v2,360)

### Check Placements    

def chkParallel(group):
    print('check Parallel')
    rot1   = group[0].Placement.Rotation
    print(rot1)
    for obj in group[1:] :
        rot2 = obj.Placement.Rotation
        print(rot2)
        if FreeCAD.Rotation.isSame(rot1, rot2, 1e-15) == False :
           return False
    return True
    # true if rot1 = rot2
    #return abs((rot1.multiply(rot2.inverted())).Angle) < 1e-15
    #return FreeCAD.Rotation.isSame(rot1, rot2, 1e-15)

def chkCollinear(group) :       # Assumes already checked parallel
    print('Check Colinear')
    obj1 = group[0]
    ax1 = obj1.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
    for obj2 in group[1:] :
       dv = obj1.Placement.Base - obj2.Placement.Base #displacement
       #symmetry axis direction of cylinder or cone
       ax2 = obj2.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
       # Axis parallel to displacement?
       align1 = dv.cross(ax1).Length <= 1e-15*dv.Length
       print(align1)
       align2 = dv.cross(ax2).Length <= 1e-15*dv.Length
       print(align2)
       if align1 == False or align2 ==  False :
          return False
    #isAligned = align1 and align2  # both lined up
    return True

def chkOrthoganal(obj1, obj2) :
    dv = obj1.Placement.Base - obj2.Placement.Base #displacement
    ax1 = obj1.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
    return ax1.dot(dv) <= 1e-15*dv.Length

def chkCircular(group) :
    print('Check Circular')
    for obj in group :
       if obj.TypeId not in ['Part::Cylinder','Part::Cone'] :
          return False
    return True

def getCircularDetails(obj):
    print('Get circular Details')
    if hasattr(obj,'Radius') :
       return obj.Height.Value, obj.Radius.Value, obj.Radius.Value
    if hasattr(obj,'Radius1') :
       return obj.Height.Value, obj.Radius1.Value, obj.Radius2.Value
    print('Not circular')

def createRevolveHull(coordlist) :
    points = sorted(coordlist, key = lambda x: x[2]) # sort by z-coord
    top = [points[0], points[1]]
    for p in points[2:]:
        top.append(p)
        while len(top) > 2 and not _isConvex(*top[-3:],2,1):
            del top[-2]
    #print(top)
    # close polygon
    top.append(top[0])
    poly = Part.makePolygon(top)
    revHull = poly.revolve(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,0,1),360)
    return revHull

def _isConvex(p, q, r, ind1, ind2):
    'return True if the vectors pq to qr is a right turn ie convex'
    return q[ind1]*r[ind2] + p[ind1]*q[ind2] + r[ind1]*p[ind2] - \
            (q[ind1]*p[ind2] + r[ind1]*q[ind2] + p[ind1]*r[ind2]) < 0

def chkPerpendicular(obj) :
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

def checkGroupShapes(group):
	print("Check Group Shapes")
	for i in group:
		checkObjShape(i)

def createHull(group) :
    hShape = None
    obj0 = group[0]
    if len(group) == 2 :
       obj1 = group[1]
       checkObjShape(obj0)
       checkObjShape(obj1)
       if chk2D(obj0) and chk2D(obj1) :
          print('Both 2D')
          if obj0.Radius == obj1.Radius :
             return hullTwoEqCircles(obj0, obj1, True)
          else :
             return hullTwoCircles(obj0, obj1, True)

       if obj0.TypeId == 'Part::Sphere' and obj1.TypeId == 'Part::Sphere' :
          if obj0.Radius == obj1.Radius :
             return hullTwoEqSpheres(obj0,obj1)
          else :
             return hullTwoSpheres(obj0,obj1)

    if chkParallel(group) :
       print('Parallel')
       if chkCollinear(group) :
          print('Collinear')
          if chkCircular(group) :
             print('Circular')
             pointLst = []
             for obj in group :
                 h,r1,r2 = getCircularDetails(obj)
                 #print('h  : '+str(h))
                 ax1 = obj.Placement.Rotation.multVec(FreeCAD.Vector(0,0,1))
                 #print('ax1 : '+str(ax1))
                 ax = obj.Placement.Base.dot(ax1)
                 #print('ax  : '+str(ax))
                 bx = ax + h
                 pointLst.append(FreeCAD.Vector(0,0,ax))
                 pointLst.append(FreeCAD.Vector(0,r1,ax))
                 pointLst.append(FreeCAD.Vector(0,r2,bx))
                 pointLst.append(FreeCAD.Vector(0,0,bx))
             print(pointLst)
             revHull = createRevolveHull(pointLst)
             # rotate from z-axis to collinear axis
             revHull.Placement.Rotation = obj0.Placement.Rotation
             print(obj0.Placement.Rotation)
             print(revHull.Placement.Rotation)
             return revHull

       if len(group) == 2 : 
          obj0 = group[0]
          obj1 = group[1]
          if chkOrthoganal(obj0,obj1) :
             print('Orthoganal')
             if obj0.TypeId == 'Part::Cylinder' and \
                obj1.TypeId == 'Part::Cylinder' :
                if obj0.Height == obj1.Height :
                   print('Hull two Cyls')
                   face = hullTwoCircles(obj0, obj1, False)
                   print(f"Face created {face}")
                   #return face
                   return face.extrude(FreeCAD.Vector(0,0,obj0.Height.Value))

             if (
                obj0.TypeId == 'Part::Cylinder' and \
                obj1.TypeId == 'Part::Sphere'
                 or
                obj0.TypeId == 'Part::Sphere' and
                obj1.TypeId == 'Part::Cylinder'
                ) :
                print('Hull Cylinder Sphere')
                if obj1.Radius > obj0.Radius:
                    obj1, obj0 = obj0, obj2
                    return hullSphereCyclinderEqRad(obj0, obj1)
                else:
                    print('Need code')


    print('Not directly handled')
    print(group)
    for obj in group :
       print(obj.Name)
    #from OpenSCADFeatures import CGALFeature
    #myObj = FreeCAD.ActiveDocument.addObject('Part::FeaturePython','Fred')
    #CGALFeature(myObj,'hull',obj.Group)
    # import OpenSCADFeatures
    #return myObj.Shape
    import OpenSCADUtils
    print('Process OpenSCAD Shapes via OpenSCAD')
    return OpenSCADUtils.process_ObjectsViaOpenSCADShape(FreeCAD.ActiveDocument,\
    group,'hull',maxmeshpoints=None)

def makeHull(hullList, ex=False):
    print('makeHull')
    print(list)
    doc = FreeCAD.ActiveDocument
    if not doc:
        doc = FreeCAD.newDocument()
    hullObj = doc.addObject('Part::FeaturePython', 'hull')
    hullObj.Shape = createHull(hullList)
    #Hull(hullObj)
    if ex:
        ViewProviderMyGroupEx(hullObj.ViewObject)
    else:
        ViewProviderMyGroup(hullObj.ViewObject)
    # Make Group the objects to be Hulled
    #hullObj.Group = list
    hullObj.recompute(True)
    # Just return Hull Object let importCSG put on Stack
    return hullObj
