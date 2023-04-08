import ezdxf
import FreeCAD
from FreeCAD import Vector, Rotation #treat as vectors; need rotation for ellipse
import Part
#import Draft
import numpy as np #for unique function

def importOpenSCADdxf_LINE(an_entity):
    print("LINE")
    start = Vector(an_entity.dxf.start)
    end = Vector(an_entity.dxf.end)
    if an_entity.dxf.start != an_entity.dxf.end:  #ensure it isn't effectively a point
        aline = Part.makeLine( tuple([an_entity.dxf.start[0],an_entity.dxf.start[1],0.0]),
                             tuple([an_entity.dxf.end[0],an_entity.dxf.end[1],0.0])) #makes Edge object

        #if len(edges)>0:
        #    if aline != edges[-1]:
        #        return [aline] #need to append it as a list because its an Edge
        #    else:
        #        print("DUPLICATE ELEMENT?")
        #        return []
        #else:
        #    return [aline] #need to append it as a list because its an Edge
        return [aline]
    else: #else we found a point???
        print("START==END?") #TODO: trap this??
        return []

def importOpenSCADdxf_POLYGON(an_entity):
    print("POLYGON")
    # Get the points of the POLYGON
    points = [(vertex[0], vertex[1]) for vertex in an_entity.vertices()]
    if len(points)>0:
        # Convert the points to vertices
        vertices = [Vector(p[0], p[1], 0) for p in points]
        if len(vertices)>2:
            #TODO: should also trap to ensure at least 3 are different?
            # Create a wire from the vertices(?)
            apolygon = Part.makePolygon(vertices).Edges[0] #returns a list of Edges
            return apolygon  #its already a list
        else:
            print("VERTICES <2 in POLYGON??")
            return []
    else:
        return []

def importOpenSCADdxf_LWPOLYLINE(an_entity):
    #TODO : this probably needs a lot of cleanup
    if an_entity.is_closed == True:
        print("CLOSED LWPOLYLINE")
        # Convert the lwpolyline to a list of vertices; TODO CHECK THIS
        with an_entity.points("xy") as points:
            vertices = [tuple([p[0], p[1], 0]) for p in points] #Vector?

        if len(vertices)>1:
            if vertices[0] != vertices[1]:
                print(vertices)
                vertices += [vertices[0]] #because it should be closed
                apolygon = Part.makePolygon(vertices).Edges #returns a List
                wire = apolygon
                return wire #its already a list

            else:
                print("CLOSED LWPOLYLINE is a POINT??")
                print(vertices)
                return []

        else:
            print("LESS THAN 2 VERTICES FOUND FOR CLOSED LWPOLYLINE",len(vertices))
            if 1:
                print("CURRENT VERTEX")
                print(vertices)
                print("HOW HANDLE IF AT ALL?")
                return []

    else:
        print("OPEN LWPOLYLINE")
        print(an_entity.dxfattribs())
        lwpentity=an_entity
        if lwpentity[0] != lwpentity[-1]:
            lwpentity.append(lwpentity[0]) #close polygon
        lwpentity.close()
        print(lwpentity.closed)
        # Convert the lwpolyline to a list of vertices; TODO CHECK THIS
        with lwpentity.points("xy") as points:
            vertices = [tuple([p[0], p[1], 0]) for p in points] #Vector?

        if len(vertices)>1:
            apolygon = Part.makePolygon(vertices).Edges #returns 
            wire = apolygon
            #edges.append(wire)
            #print("NOW HERE >>")
            #print(edges)
            return wire #already a list

        else:
            print("POLYLINE of 1 Vertex????")
            return []

def importOpenSCADdxf_SPLINE(an_entity):
    print("SPLINE")
    #https://forum.freecad.org/viewtopic.php?style=10&t=9894
    #https://forum.freecad.org/viewtopic.php?t=35644
    #fits=list()
    #if entity.fit_point_count()>0:
    #  fits = entity.fit_points
    #knots=list()
    #if entity.knot_count()>0:
    #  knots = entity.knots
    control_points=()
    if an_entity.control_point_count()>0:                    
        control_points = an_entity.control_points
    #weights=()
    #weights = entity.weights
    #n = len(control_points)-1
    control_points=tuple(control_points)
    aspline = Part.BSplineCurve()
    aspline.buildFromPoles(control_points, False, 3)
                    
    thespline = aspline.toShape() #TODO CHECK THIS; this is an Edge object
    #edges.append(thespline)
    return [thespline] #it needs to be a list; TODO: how check to ensure valid return object?

def importOpenSCADdxf_CIRCLE(an_entity):
    print("CIRCLE")
    # Get the center and radius of the circle
    center = an_entity.dxf.center
    radius = an_entity.dxf.radius
    if radius != 0.0:
        # Create a circle wire
        circle = Part.Circle(Vector(center), Vector(0, 0, 1), radius).toShape() #returns Edge list

        #wire = Part.Wire(circle)
        #wires.append(wire)
        return [circle] #bc its not a list yet
    else:
        return []

def importOpenSCADdxf_ELLIPSE(an_entity):
    print("ELLIPSE")   
    # Get the center point, major axis, minor axis, and rotation angle of the ellipse
    center = an_entity.dxf.center
    major_axis = an_entity.dxf.major_axis
    #entity.dxfattribs()
    if an_entity.dxf_attrib_exists('ratio') == True:
        minor_axis = an_entity.dxf.ratio*an_entity.dxf.major_axis #scale axis
        r=FreeCAD.Rotation(Vector(0,0,1),90) #rot 90 deg in X-Y plane, ie around Z axis
        minor_axis=r.multVec(Vector(minor_axis)) #calc minor axis as scaled axis at 90 deg to major axis
    elif an_entity.dxf_attrib_exists('minor_axis') == True:
        minor_axis = an_entity.dxf.minor_axis
    else:  #trap
        minor_axis = major_axis  #probably not a good trap
    #print(center)
    #print(major_axis)
    #print(minor_axis)
    if Vector(minor_axis) != Vector(0,0,0):
        # Create an ellipse wire
        ellipse = Part.Ellipse(Vector(major_axis), Vector(minor_axis),Vector(center) ).toShape() #returns Edges
        return [ellipse] #bc not yet a List
    else:
        return []

def importOpenSCADdxf_ARC(an_entity):
    print("ARC")
    center = an_entity.dxf.center
    #print(center)
    radius = an_entity.dxf.radius
    #print(radius)
    start_angle = np.deg2rad(an_entity.dxf.start_angle) #radians
    #print(start_angle)
    end_angle = np.deg2rad(an_entity.dxf.end_angle)  #radians
    #print(end_angle)
    if radius>0:
        if start_angle != end_angle:
            #p1 = App.Vector(10, 0, 0)
            #p2 = App.Vector(0, 10, 0)
            #p3 = App.Vector(-10, 0, 0)
            # Create the arc wire
            circle = Part.Circle(Vector(center), Vector(0, 0, 1), radius) #returns cirlce; Edge with .toShape, fwiw
            anarc = Part.ArcOfCircle(circle, start_angle, end_angle).toShape() #an Edge object

            # Close the wire to create a polygon??
            #leg1 = Part.makeLine(Vector(center),Vector(anarc.Vertexes[0].X,anarc.Vertexes[0].Y,0.0)) #an Edge object
            #leg2 = Part.makeLine(Vector(center),Vector(anarc.Vertexes[1].X,anarc.Vertexes[1].Y,0.0)) #an Edge object
            #pieslice = Part.Wire([leg1,anarc,leg2]) #Wire object from list of Edges
            return [anarc]  #bc its not already a List
        else:
            return []
    else:
        return []

def importOpenSCADdxf_HATCH(an_entity):
    #absolutely no idea if this will work ...
    print("HATCH")
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

def importEZDXFface(filename=None, doc=None, layer=None, exlayer=None):

    #using exlayer as placeholder for perhaps later specifying 'all layers except ...'
    #explore returning a compound instead of a face????

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
            #if "0" in layernames:
            #    layer_names=['0']
            #elif "Image" in layernames:
            #    layer_names=['Image']
            #elif "Layer1" in layernames:
            #    layer_names=['Layer1']
            #else:
            if 1:
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

                elif entity.dxftype() == 'POLYGON': 
                    an_edge=importOpenSCADdxf_POLYGON(entity)

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

                elif entity.dxftype() == 'HATCH':
                    an_edge=importOpenSCADdxf_HATCH(entity)

                else:
                    print("Unsupported type : ", entity.dxftype())

                if any(an_edge) == True:
                    edges+=an_edge

                    if len(edges)>1:
                        edges = [Part.sortEdges(edges)[0]]  #should only be edges...
                        edges=[item for sublist in edges for item in sublist] #flatten

                    if len(edges)>1:
                        print("CHECKING IF LINE,SPLINE,LWPOLYLINE NEEDS CLOSING")
                        if entity.dxftype() in ['LINE','SPLINE','LWPOLYLINE']:
                            if edges[0].Vertexes[0].X == edges[-1].Vertexes[1].X and edges[0].Vertexes[0].Y == edges[-1].Vertexes[1].Y:
                                print("THIS IS CLOSED")
                                print(edges[0].Vertexes[0].X, edges[0].Vertexes[0].Y)
                                print(edges[0].Vertexes[1].X, edges[0].Vertexes[1].Y)
                                print(edges[-1].Vertexes[0].X, edges[-1].Vertexes[0].Y)
                                print(edges[-1].Vertexes[1].X, edges[-1].Vertexes[1].Y)                
                                entitylist.append(edges)
                                entitytypelist.append(entity.dxftype())                                
                            else:
                                print("THIS IS NOT CLOSED")
                                print("**** IGNORING ENTITY ****")
                                print(edges[0].Vertexes[0].X, edges[0].Vertexes[0].Y)
                                print(edges[0].Vertexes[1].X, edges[0].Vertexes[1].Y)
                                print(edges[-1].Vertexes[0].X, edges[-1].Vertexes[0].Y)
                                print(edges[-1].Vertexes[1].X, edges[-1].Vertexes[1].Y)
                                edges=[]
                        else:
                            entitylist.append(edges)
                            entitytypelist.append(entity.dxftype())
                    else:
                        entitylist.append(edges)
                        entitytypelist.append(entity.dxftype())                        
                else:
                    print("EMPTY EDGE RETURNED???")
            #end of for entity loop
            if ('LINE' in entitytypes) or ('SPLINE' in entitytypes) or ('LWPOLYLINE' in entitytypes):
                entitylist=[item for sublist in entitylist for item in sublist] #flatten

            layerentitylist.append(entitylist)
            layertypelist.append(entitytypelist)
        #end of for layer loop
        
        #TODO: Unltimately, create a compound from the list of faces??
        faces=[]
        face=None
        if len(layerentitylist)>0:
            for i,l in enumerate(layerentitylist):
                entitylist = layerentitylist[i]
                if isinstance(entitylist[0], list) == False:  #make a list of entities
                    entitylist=[entitylist]
                entitytypelist = layertypelist[i]
                entitytypes = list(np.unique(entitytypelist))
                if len(entitylist)==1 and isinstance(entitylist[0],list)==True:
                    entitylist=[entitylist[0]]
                for el in entitylist:
                    el2=el                
                    if 1:
                        print(el2)
                        print("YUP")
                        if isinstance(el2,list) == True:
                            e = Part.sortEdges(el2)
                        else:
                            e=[el2]

                        try:
                            face=Part.Face(Part.Wire(e))
                            faces.append(face)                
                        except:
                            wires=None
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

                        # Create a compound of faces? faces list collects everything though ...
                        ##if len(faces)>0:
                        ##    for f in faces:
                        ##        Part.show(f)
                        ###    compound = Part.makeCompound(faces)
                        ###    Part.show(compound)

                        #Return compound, face; TODO: return layer name, color, labels?
                        return faces[0]
                    else:
                        print("No wires created")
                        return None
            #end of for layers loop
        else:
            print("No layers extracted")
            return None
    else:
        print("No layers found")
    return None
