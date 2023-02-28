#**************************************************************************
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
#*                Thanks Ed Williams, Carlo D                              *
#*                                                                         *
#***************************************************************************

import FreeCAD
#from OpenSCADFeatures import CGALFeature
from OpenSCADHull import checkObjShape

#printverbose = False
printverbose = True

def setObjColor(obj, color):
    # set color for all faces of selected object
    colorlist=[]
    for i in range(len(obj.Shape.Faces)):
        colorlist.append(color)
        #print('[*] Object contains %d faces'%(len(colorlist),))
        obj.ViewObject.DiffuseColor = colorlist

def setOutListColor(obj, color) :
    if obj.OutList != None :
       for i in obj.OutList :
           setOutListColor(i,color)
           setObjColor(i,color)        


def CGALFeatureObj(name, children,arguments=[]):
    from OpenSCADFeatures import CGALFeature
    if printverbose: print(f"CGALFeatureObj name {name} children {children}")
    myobj=FreeCAD.ActiveDocument.addObject("Part::FeaturePython", name)
    CGALFeature(myobj, name, children, str(arguments))
    if FreeCAD.GuiUp:
        for subobj in children:
            subobj.ViewObject.hide()
        if FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/OpenSCAD").\
            GetBool('useViewProviderTree'):
            from OpenSCADFeatures import ViewProviderTree
            ViewProviderTree(myobj.ViewObject)
        else:
            myobj.ViewObject.Proxy = 0
    myobj.recompute()        
    return myobj

def minkowski(p):
    ''' for reference only
    minkowski_action : minkowski LPAREN keywordargument_list RPAREN OBRACE block_list EBRACE'''
    if printverbose: print(f"Minkowski")
    if len(p[6]) == 2 :     # Two objects on stack
        if printverbose:
            print(f"Obj1 {p[6][0].Name} {p[6][0].TypeId}")
            print(f"Obj2 {p[6][1].Name} {p[6][1].TypeId}")
        obj1 = p[6][0]
        obj2 = p[6][1]
        checkObjShape(obj1)
        checkObjShape(obj2)
        if obj2.TypeId == "Part::Sphere" and hasattr(obj1,"Shape"):
            radius = obj2.Radius.Value
            if hasattr(obj1.Shape, "Edges"):
                # Use Offset as minkowski enlarges 
                newObj = FreeCAD.ActiveDocument.addObject("Part::Offset",\
                            "Offset_" + p[1])
                newObj.Source = obj1
                newObj.Value = radius
                newObj.Mode = 'Skin'
                newObj.Join = 'Arc'
                newObj.Intersection = False
                newObj.SelfIntersection = False
                newObj.Fill = False
                if hasattr(obj1, 'ViewObject'):
                    obj1.ViewObject.hide()
                FreeCAD.ActiveDocument.removeObject(obj2.Name)
                #p[0] = [newObj]
                return newObj

        elif obj2.TypeId == "Part::Cylinder" and hasattr(obj1,"Shape"):
            radius = obj2.Radius.Value
            if hasattr(obj1.Shape, "Edges"):
                # Use Offset as minkowski enlarges 
                newObj = FreeCAD.ActiveDocument.addObject("Part::Offset",\
                            "Offset_" + p[1])
                newObj.Source = obj1
                newObj.Value = radius
                newObj.Mode = 'Skin'
                newObj.Join = 'Intersection'
                newObj.Intersection = False
                newObj.SelfIntersection = False
                newObj.Fill = False
                newObj.recompute()
                fEdges = []
                localAxis = obj2.Placement.Rotation.Axis
                print(f"Cylinder axis {localAxis}")
                for i, e in enumerate(newObj.Shape.Edges,start=1):
                    # Only check straight edges
                    if hasattr(e.Curve, 'Direction'):
                        direction = e.Curve.Direction
                        # print(f"Direction {direction}")
                        if localAxis.isEqual(direction, 1e-7) or \
                                localAxis.isEqual(-direction, 1e-7):
                            print(f"Edge {i} is parallel")
                            fEdges.append((i,radius,radius))

                FreeCAD.ActiveDocument.removeObject(obj2.Name)
                if len(fEdges) > 0:
                    print(f"Edges {len(fEdges)}")
                    myFillet = FreeCAD.ActiveDocument.addObject("Part::Fillet","Fillet")
                    myFillet.Base = newObj
                    myFillet.Edges =fEdges
                    newObj.ViewObject.hide()
                    #myFillet.recompute()
                    #p[0] = [myFillet]
                    return myFillet
                else:
                    print(f"Warning : No Edges filleted")    
                    #p[0] = [newObj]
                    return newObj
                return
        #else:    
        #    # - For minkowski Just indicate first shape needs editing
        #    # return just first object     
        #    #print(dir(p[6][0]))
        #    #print(dir((p[6][1]).ViewObject))
        #    #print(p[6][0].TypeId)
        #    p[6][0].ViewObject.ShapeColor = (1.,0.,0.)
        #    setObjColor(p[6][0],(1.,0.,0.))
        #    setOutListColor(p[6][0],(1.,0.,0.))
        #    p[6][1].ViewObject.ShapeColor = (0.,1.,0.)
        #    setObjColor(p[6][1],(0.,1.,0.))
        #    setOutListColor(p[6][1],(1.,0.,0.))
        #    #p[6][1].ViewObject.hide()
        #    p[0] = [p[6][0]]
    print(f"OpenSCAD to perform : Minkowski")
    cgal = CGALFeatureObj(p[1],p[6],p[3])
    # Just return Minkowski object let importCSG put on Stack
    return cgal
