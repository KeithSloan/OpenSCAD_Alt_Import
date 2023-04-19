# -*- coding: utf8 -*-
#***************************************************************************
#*                                                                         *
#*   Copyright (c) 2023 Matt Considine                                     *
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
__title__="FreeCAD OpenSCAD Workbench - Dxf importer"
__author__ = "Matt Considine"
__author__ = "Keith Sloan <keith@sloan-home.co.uk>"
__url__ = ["http://www.sloan-home.co.uk/ImportCSG"]

import ezdxf
import FreeCAD
from FreeCAD import Vector, Rotation #treat as vectors; need rotation for ellipse
import Part
#import Draft
import numpy as np #for unique function

def importOpenSCADdxf_LINE(an_entity):
    #print("LINE")
    start = Vector(an_entity.dxf.start)
    end = Vector(an_entity.dxf.end)
    if an_entity.dxf.start != an_entity.dxf.end:  #ensure it isn't effectively a point
        aline = Part.makeLine( tuple([an_entity.dxf.start[0],an_entity.dxf.start[1],0.0]),
                             tuple([an_entity.dxf.end[0],an_entity.dxf.end[1],0.0])) #makes Edge object
        return [aline]
    else: #else we found a point???
        print("START==END?") #TODO: trap this??
        return []

def importOpenSCADdxf_POLYLINE(an_entity):
    #print("POLYLINE")
    # Get the points of the POLYLINE
    verts = an_entity.vertices
        
    verts = [tuple(v.dxf.location) for v in verts]
    if an_entity.is_closed:
        verts += [verts[0]]
        
    if len(verts)>0:
        apolygon = Part.makePolygon(verts).Edges #returns a list of Edges
        return [apolygon] 
    else:
        print("NO LENGTH")
        return []

def importOpenSCADdxf_LWPOLYLINE(an_entity):
    #TODO : this probably needs a lot of cleanup
    if an_entity.is_closed == True:
        #print("CLOSED LWPOLYLINE")
        # Convert the lwpolyline to a list of vertices; TODO CHECK THIS
        with an_entity.points("xy") as points:
            vertices = [tuple([p[0], p[1], 0]) for p in points] #Vector?

        if len(vertices)>1:
            if vertices[0] != vertices[1]:
                vertices += [vertices[0]] #because it should be closed
                apolygon = Part.makePolygon(vertices).Edges #returns a List
                wire = apolygon
                return wire #its already a list

            else:
                print("CLOSED LWPOLYLINE is a POINT??")
                return []

        else:
            print("LESS THAN 2 VERTICES FOUND FOR CLOSED LWPOLYLINE",len(vertices))
            return []

    else:
        #print("OPEN LWPOLYLINE")
        #print(an_entity.dxfattribs())
        lwpentity=an_entity
        if lwpentity[0] != lwpentity[-1]:
            lwpentity.append(lwpentity[0]) #close polygon
        lwpentity.close()
        # Convert the lwpolyline to a list of vertices; TODO CHECK THIS
        with lwpentity.points("xy") as points:
            vertices = [tuple([p[0], p[1], 0]) for p in points] #Vector?

        if len(vertices)>1:
            apolygon = Part.makePolygon(vertices).Edges #returns 
            wire = apolygon
            return wire #already a list

        else:
            print("POLYLINE of 1 Vertex????")
            return []

def importOpenSCADdxf_SPLINE(an_entity):
    #print("SPLINE")
    control_points=()
    if an_entity.control_point_count()>0:                    
        control_points = an_entity.control_points
    control_points=tuple(control_points)
    aspline = Part.BSplineCurve()
    aspline.buildFromPoles(control_points, False, 3)
    thespline = aspline.toShape() #TODO CHECK THIS; this is an Edge object
    return [thespline] #it needs to be a list; TODO: how check to ensure valid return object?

def importOpenSCADdxf_CIRCLE(an_entity):
    #print("CIRCLE")
    # Get the center and radius of the circle
    center = an_entity.dxf.center
    radius = an_entity.dxf.radius
    if radius != 0.0:
        # Create a circle wire
        circle = Part.Circle(Vector(center), Vector(0, 0, 1), radius).toShape() #returns Edge list
        return [circle] #bc its not a list yet
    else:
        return []

def importOpenSCADdxf_ELLIPSE(an_entity):
    #print("ELLIPSE")  
    #print(an_entity.dxfattribs())    
    center = Vector(an_entity.dxf.center)
    ratio = an_entity.dxf.ratio
    major_axis = Vector(an_entity.dxf.major_axis)
    normalv=Vector(0,0,1)
    if an_entity.dxf_attrib_exists('ratio') == True:
        minor_axis = major_axis.cross(normalv).normalize()*major_axis.Length*ratio
    elif an_entity.dxf_attrib_exists('minor_axis') == True:
        minor_axis = an_entity.dxf.minor_axis
    else:  #trap
        minor_axis = major_axis  #probably not a good trap

    if ratio>1:
        tempaxis=major_axis    
        major_axis=minor_axis
        minor_axis=tempaxis
    elif ratio==1:
        radius = np.sqrt(major_axis[0]**2+major_axis[1]**2+major_axis[2]**2)
        ellipse=Part.Circle(center, normalv, radius).toShape()
        return [ellipse]
                
    if Vector(minor_axis) != Vector(0,0,0):
        # Create an ellipse wire
        ellipse=Part.Ellipse(major_axis,minor_axis,Vector(0,0,0))
        if an_entity.dxf.start_param != 0.0 or an_entity.dxf.end_param != 2*np.pi:
            ellipse=Part.ArcOfEllipse(ellipse, an_entity.dxf.start_param-np.pi/2, an_entity.dxf.end_param-np.pi/2)
        ellipse=ellipse.toShape()
        ellipse=ellipse.translate(center)
        return [ellipse] #bc not yet a List
    else:
        return []

def importOpenSCADdxf_ARC(an_entity):
    #print("ARC")
    center = an_entity.dxf.center
    radius = an_entity.dxf.radius
    start_angle = np.deg2rad(an_entity.dxf.start_angle) #radians
    end_angle = np.deg2rad(an_entity.dxf.end_angle)  #radians
    if radius>0:
        if start_angle != end_angle:
            # Create the arc wire
            circle = Part.Circle(Vector(center), Vector(0, 0, 1), radius) #returns cirlce; Edge with .toShape, fwiw
            anarc = Part.ArcOfCircle(circle, start_angle, end_angle).toShape() #an Edge object
            return [anarc]  #bc its not already a List
        else:
            return []
    else:
        return []

def importOpenSCADdxf_HATCH(an_entity):
    #absolutely no idea if this will work ...
    #print("HATCH")
    # Get the boundary path of the hatch
    paths = an_entity.paths

    # Create a wire from the boundary path
    wire = Part.Wire()
    for path in paths:
        for segment in path:
            if segment[0] == 'Line':
                start = segment[1]
                end = segment[2]
                wire.add(Part.Line(Vector(start[0], start[1], 0), Vector(end[0], end[1], 0)))
            elif segment[0] == 'Arc':
                center = segment[1]
                radius = segment[2]
                start_angle = segment[3]
                end_angle = segment[4]
                wire.add(Part.ArcOfCircle(Vector(center[0], center[1], 0), Vector(0, 0, 1), radius, start_angle, end_angle))

    return [wire] #Edges???

def importEZDXFshape(filename=None, doc=None, layer=None, exlayer=None, flattenlayers=False):

    #using exlayer as placeholder for perhaps later specifying 'all layers except ...'
    # Return either a single face or the Shape of a compound if more than one Face

    # Load the DXF file using ezdxf
    #TODO: load in recover mode assuming it needs fixing?
    #TODO : deal with any units specified in DXF?
    #NOT DEALT WITH : 3D objects, linewidths, colors, user data

    doc = ezdxf.readfile(filename)
    msp = doc.modelspace()

    # Get list of all layers
    layernames = list(np.unique([e.dxf.layer for e in doc.entities]))
    print("ALL LAYER NAMES : ",layernames)
    if len(layernames)>0:  #if there are actually layers to loop through ...

        layer_names=list()

        if layer != None :  #layer(s) desired is specified
          if layer in layernames:  #TODO adjust for multiple layer request or exclusion
            layer_names=[layer] #ok, just take that one layer
          else:
            print("Layer name provided not found")

        if len(layer_names) == 0:  #if we havent found a specified layer, look for defaults
            print("No common layer name found; Selecting all")
            #TODO select one with most entities? 1st one? None?
            layer_names=layernames

        layerentitylist=[] #list of list of processed entities per layer
        layertypelist=[] #list of lists of entity types as they appear per layer

        for count, alayer in enumerate(layer_names):  #for the layer(s) we want ....
            # Initialize an empty list to hold the faces, entities and entity names
            entitylist=[]
            entitytypelist=[]
            entities = msp.query(f'*[layer=="{alayer}"]') #get all the entities on that layer
            entitytypes = list(np.unique([e.dxftype() for e in entities]))
            for entity in entities: #loop through all the entities, process and store in lists
                edges = []
                an_edge = []

                if entity.dxftype() == 'LINE':
                    an_edge=importOpenSCADdxf_LINE(entity)

                elif entity.dxftype() == 'POLYLINE': 
                    an_edge=importOpenSCADdxf_POLYLINE(entity)

                elif entity.dxftype() == 'LWPOLYLINE':
                    an_edge=importOpenSCADdxf_LWPOLYLINE(entity)

                elif entity.dxftype() == "SPLINE":
                    an_edge=importOpenSCADdxf_SPLINE(entity)

                elif entity.dxftype() == 'CIRCLE':
                    an_edge=importOpenSCADdxf_CIRCLE(entity)

                elif entity.dxftype() == 'ELLIPSE':  
                    an_edge=importOpenSCADdxf_ELLIPSE(entity)

                elif entity.dxftype() == 'ARC':
                    an_edge=importOpenSCADdxf_ARC(entity)

                #elif entity.dxftype() == 'HATCH':
                #    an_edge=importOpenSCADdxf_HATCH(entity) #not working bc of PolyLinePath??

                elif entity.dxftype() in ['HATCH','TEXT','DIMENSION','REGION','INSERT','ATTDEF']:
                    continue

                else:
                    print("Unsupported type : ", entity.dxftype())

                if any(an_edge) == True:
                    edges+=an_edge

                    if len(edges)>1:
                        edges = [Part.sortEdges(edges)[0]]  #should only be edges...
                        edges=[item for sublist in edges for item in sublist] #flatten
                        #print(edges)
                        #edges = [Part.sortEdges(edges)]  #should only be edges...
                        
                    if len(edges)>1:
                        #print("CHECKING IF LINE,SPLINE,LWPOLYLINE NEEDS CLOSING")
                        if entity.dxftype() in ['LINE','SPLINE','LWPOLYLINE','POLYLINE']:
                            if edges[0].Vertexes[0].X == edges[-1].Vertexes[1].X and edges[0].Vertexes[0].Y == edges[-1].Vertexes[1].Y:
                                #print("THIS IS CLOSED")
                                #print(edges[0].Vertexes[0].X, edges[0].Vertexes[0].Y)
                                #print(edges[0].Vertexes[1].X, edges[0].Vertexes[1].Y)
                                #print(edges[-1].Vertexes[0].X, edges[-1].Vertexes[0].Y)
                                #print(edges[-1].Vertexes[1].X, edges[-1].Vertexes[1].Y)                
                                entitylist.append(edges)
                                entitytypelist.append(entity.dxftype())                                
                            else:
                                print("THIS IS NOT CLOSED")
                                print("**** IGNORING ENTITY ****")
                                #print(edges[0].Vertexes[0].X, edges[0].Vertexes[0].Y)
                                #print(edges[0].Vertexes[1].X, edges[0].Vertexes[1].Y)
                                #print(edges[-1].Vertexes[0].X, edges[-1].Vertexes[0].Y)
                                #print(edges[-1].Vertexes[1].X, edges[-1].Vertexes[1].Y)
                                edges=[]
                        else:
                            entitylist.append(edges)
                            entitytypelist.append(entity.dxftype())
                    else:
                        entitylist.append(edges)
                        entitytypelist.append(entity.dxftype())                        
                #else:
                #    print("EMPTY EDGE RETURNED???")
            #end of for entity loop
            if len(entitylist)>0:
                if ('LINE' in entitytypes) or ('SPLINE' in entitytypes) or ('LWPOLYLINE' in entitytypes) or ('POLYLINE' in entitytypes) :
                    entitylist=[item for sublist in entitylist for item in sublist] #flatten
                layerentitylist.append(entitylist)
                layertypelist.append(entitytypelist)
        #end of for layer loop
        
        #TODO: Unltimately, create a compound from the list of faces??
        faces=[]
        face=None
        if len(layerentitylist)>0:
            if flattenlayers and len(layerentitylist)>1:
                layerentitylist=[item for sublist in layerentitylist for item in sublist] #flatten
                layerentitylist=[Part.sortEdges(layerentitylist)[0]]  #should only be edges...         
            for i,l in enumerate(layerentitylist):
                entitylist = layerentitylist[i] # this section needs cleanup?
                if isinstance(entitylist[0], list) == False:  #make a list of entities
                    entitylist=[entitylist]
                if len(entitylist)==1 and isinstance(entitylist[0],list)==True:
                    entitylist=[entitylist[0]]
                for el in entitylist:
                    if isinstance(el,list) == True:
                        e = Part.sortEdges(el)
                    else:
                        e=[el2]

                    #wires=None
                    for i, e2 in enumerate(e): #only make a face from non-lines
                        try:  #TODO: figure out why this sometimes is needed
                            newwires = Part.Wire(e2)
                            # Create a face from the wire
                            face = Part.Face(newwires)
                            if face != None:
                                faces.append(face)
                        except:
                            # Create a face from the wire
                            try:
                                face = Part.Face(e2)
                                # Append the face to the list of faces
                                if face != None:
                                    faces.append(face)
                            except:
                                face = None

            #end of for layers loop
            # If more than one Face create a compound Shape
            if len(faces)>0:
                compound = Part.makeCompound(faces)
                return compound
            ##    Part.show(compound)

            return faces[0]

        else:
            print("No layers extracted")
            return None
    else:
        print("No layers found")
        return None


