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
#*                                                                         *
#***************************************************************************

import FreeCAD
#from OpenSCADFeatures import CGALFeature

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


def minkowski(p):
    ''' for reference only
    minkowski_action : minkowski LPAREN keywordargument_list RPAREN OBRACE block_list EBRACE'''
    print(f"Minkowski")
    if len(p[6]) == 2 :     # Two objects on stack
        print(p[6][1].TypeId)
        if p[6][1].TypeId == "Part::Sphere" and hasattr(p[6][0],"Shape"):
            obj = p[6][0]
            radius = p[6][1].Radius.Value
            if hasattr(obj.Shape, "Edges"):
                # Use Offset as minkowski enlarges 
                newObj = FreeCAD.ActiveDocument.addObject("Part::Offset",\
                            "Offset_" + p[1])
                newObj.Source = obj
                newObj.Value = radius
                newObj.Mode = 'Skin'
                newObj.Join = 'Arc'
                newObj.Intersection = False
                newObj.SelfIntersection = False
                newObj.Fill = False
                FreeCAD.ActiveDocument.removeObject(p[6][1].Name)
                p[0] = [newObj]
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
    newObj=FreeCAD.ActiveDocument.addObject("Part::FeaturePython",p[1])
    from OpenSCADFeatures import CGALFeature
    #CGALFeature(myobj,name,children,str(arguments))
    p[0] = [ CGALFeature(newObj,p[1],p[6],p[3]) ]
