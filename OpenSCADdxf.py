import ezdxf
from ezdxf import recover, query, disassemble
import FreeCAD
from FreeCAD import Vector, Rotation #treat as vectors; need rotation for ellipse
import Part
#import Draft
import numpy as np #for unique function

def importOpenSCADdxf_POINT(an_entity):
    #print("POINT")
    # Get a point and return a small circle
    location = Vector(an_entity.dxf.location)
    location[2] = 0.0 #ensure will be on plane z=0

    if location:
        #return [Part.Point(location).toShape()] #send back a vertex
        return None
    else:
        print("prob with point")
        return None

def importOpenSCADdxf_LINE(an_entity):
    #print("LINE")
    start = Vector(an_entity.dxf.start)
    end = Vector(an_entity.dxf.end)
    start[2]=0.0 #force flat
    end[2]=0.0 #force flat
    if start != end:  #ensure it isn't effectively a point
        try:
            aline = Part.makeLine( tuple([start[0],start[1],0.0]), tuple([end[0],end[1],0.0])) #makes Edge object
            return [aline]
        except:
            print("problem in line??")
            print(an_entity.dxfattribs())
            print(start)
            print(end)
            return None
    else: #else we found a point???
        #print("START==END?")
        #return [Part.Point(start).toShape()] #we're going to ignore these for now anyway
        return None

def importOpenSCADdxf_POLYLINE(an_entity):
    #print("POLYLINE")
    # Get the points of the POLYLINE
    verts = an_entity.vertices

    verts = [tuple(v.dxf.location) for v in verts]
    if an_entity.is_closed:
        verts += [verts[0]]

    if len(verts)>0:
        return Part.makePolygon(verts).Edges #returns a list of Edges
    else:
        print("NO LENGTH")
        return None

def importOpenSCADdxf_LWPOLYLINE(an_entity):
    #TODO : this probably needs a lot of cleanup
    if an_entity.is_closed == True:
        #print("CLOSED LWPOLYLINE")
        # Convert the lwpolyline to a list of vertices; TODO CHECK THIS
        with an_entity.points("xy") as points:
            vertices = [tuple([p[0], p[1], 0.0]) for p in points] #Vector?

        if len(vertices)>1:
            if vertices[0] != vertices[1]:
                vertices += [vertices[0]] #because it should be closed
                return Part.makePolygon(vertices).Edges #returns a List

            else:
                print("CLOSED LWPOLYLINE is a POINT??")
                return None

        else:
            print("LESS THAN 2 VERTICES FOUND FOR CLOSED LWPOLYLINE",len(vertices))
            return None

    else:
        #print("OPEN LWPOLYLINE")
        #print(an_entity.dxfattribs())
        lwpentity=an_entity
        if lwpentity[0] != lwpentity[-1]:
            lwpentity.append(lwpentity[0]) #close polygon
        lwpentity.close()
        # Convert the lwpolyline to a list of vertices; TODO CHECK THIS
        with lwpentity.points("xy") as points:
            vertices = [tuple([p[0], p[1], 0.0]) for p in points] #Vector?

        if len(vertices)>1:
            try:
                return Part.makePolygon(vertices).Edges #returns a list
            except:
                print("problem in open lwpolyline?")
                return None

        else:
            print("POLYLINE of 1 Vertex????")
            return None

def importOpenSCADdxf_SPLINE(an_entity):
    #print("SPLINE")
    control_points=()
    if an_entity.control_point_count()>0:                    
        control_points = an_entity.control_points
        control_points=tuple(control_points)
        aspline = Part.BSplineCurve()
        aspline.buildFromPoles(control_points, an_entity.closed, 3)
        thespline = aspline.toShape() #TODO CHECK THIS; this is an Edge object
        return [thespline] #it needs to be a list; TODO: how check to ensure valid return object?
    else:
        print("No control pts?")
        return None

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
        return None

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

    elpart1=an_entity.dxf.start_param
    elpart2=an_entity.dxf.end_param

    if (elpart1 != elpart2) and (np.isclose(elpart1,elpart2)==True):
      #elpart1=(an_entity.dxf.start_param+an_entity.dxf.end_param)/2
      #elpart2=elpart1
      elpart1=None
      elpart2=None

    if Vector(minor_axis) != Vector(0,0,0):
        # Create an ellipse wire
        ellipse=Part.Ellipse(major_axis,minor_axis,Vector(0,0,0))
        if (elpart1 != None) and (elpart2 != None):
            #print("ARC OF ELLIPSE")
            #print(an_entity.dxf.start_param)
            #print(an_entity.dxf.end_param)
            ellipse=Part.ArcOfEllipse(ellipse, 2*np.pi-elpart2, 2*np.pi-elpart1) #DXF is ccw
        ellipse=ellipse.toShape()
        ellipse=ellipse.translate(center)
        return [ellipse] #bc not yet a List
    else:
        return None

def importOpenSCADdxf_ARC(an_entity):
    #print("ARC")
    center = an_entity.dxf.center
    radius = an_entity.dxf.radius
    start_angle = np.deg2rad(an_entity.dxf.start_angle) #radians
    end_angle = np.deg2rad(an_entity.dxf.end_angle)  #radians
    if radius>0:
        if start_angle != end_angle:
            # Create the arc wire
            circle = Part.Circle(Vector(center), Vector(0, 0, 1), radius) #returns circle; Edge with .toShape, fwiw
            anarc = Part.ArcOfCircle(circle, start_angle, end_angle).toShape() #an Edge object
            return [anarc]  #bc its not already a List
        else:
            return None
    else:
        return None

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
                wire.add(Part.Line(Vector(start[0], start[1], 0.0), Vector(end[0], end[1], 0)))
            elif segment[0] == 'Arc':
                center = segment[1]
                radius = segment[2]
                start_angle = segment[3]
                end_angle = segment[4]
                wire.add(Part.ArcOfCircle(Vector(center[0], center[1], 0.0), Vector(0, 0, 1), radius, start_angle, end_angle))

    return [wire] #Edges???

def importOpenSCADdxf_INSERT(an_entity):
    #new_entity = an_entity.explode()
    new_entity = [e for e in an_entity.block()]
    #c=[processEntity(a) for a in new_entity if a.dxftype()!='INSERT'] #list of entities that should then be processed
    c=list()
    for a in new_entity:
        if a.dxftype() not in ['INSERT']:
            anent=returnEnts(a)[0]
            #print("######################",anent)
            aresult = processEntity(anent, None)
            if aresult != None : #and isinstance(aresult,Part.Vertex)==False:
                c.append(aresult)
        else:
            importOpenSCADdxf_INSERT(a)                
    ##while any([isinstance(a,list)==True for a in c]):
    ##    #print("Flattening in INSERT...")
    ##    c=[item for sublist in c for item in sublist] #flatten hmm  ... if isinstance(c[0],list)==True?
    #for i in c:
    #  print("     type : ",c)
    return c

def importOpenSCADdxf_TEXT(an_entity):
    # _label_ = Draft.make_label(target_point=FreeCAD.Vector(-0.9317530393600464, 0.6405777335166931, 0.0), placement=FreeCAD.Placement(FreeCAD.Vector(-1.2595092058181763, 0.5948442816734314, 0.0), FreeCAD.Rotation(0.0, 0.0, 0.0, 1.0)), target_object=FreeCAD.ActiveDocument.Dimension001, subelements=None, label_type='Custom', direction='Vertical', distance=-0.392545148730278)

    #_dim_ = Draft.make_linear_dimension(FreeCAD.Vector(0.0, 0.0, 0.0), FreeCAD.Vector(-0.24974219501018524, -0.21259427070617676, 0.0), dim_line=FreeCAD.Vector(-0.6689651012420654, 0.1608951836824417, 0.0))

    #pl = FreeCAD.Placement()
    #pl.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
    #pl.Base = an_entity.insert
    #_text_ = Draft.make_text([an_entity.text], placement=pl)
    ## Gui.Selection.addSelection('Unnamed','Text')
    #Draft.autogroup(_text_)
    return None

def importOpenSCADdxf_SOLID(an_entity):
    #print("SOLID")
    # Get the points of the SOLID
    verts = an_entity.vertices(True)
    verts = [tuple(v) for v in verts]

    if len(verts)>0:
        return Part.makePolygon(verts).Edges #returns a list of Edges
    else:
        print("NO VERTICES FOR SOLID")
        return None

def importOpenSCADdxf_MLEADER(an_entity):
    new_entity = an_entity.explode()
    #c=[processEntity(a) for a in new_entity if a.dxftype()!='INSERT'] #list of entities that should then be processed
    c=list()
    for a in new_entity:
        if a.dxftype() not in ['MLEADER','MULTILEADER']:
            anent=returnEnts(a)[0]          
            aresult = processEntity(anent, None)
            if aresult != None : #and isinstance(aresult,Part.Vertex)==False:
                c.append(aresult)
    #while any([isinstance(a,list)==True for a in c]):
    #    #print("Flattening in MLEADER...")
    #    c=[item for sublist in c for item in sublist] #flatten hmm  ... if isinstance(c[0],list)==True?
    return c

def importOpenSCADdxf_MLINE(an_entity):
    new_entity = an_entity.explode()
    #c=[processEntity(a) for a in new_entity if a.dxftype()!='INSERT'] #list of entities that should then be processed
    c=list()
    for a in new_entity:
        if a.dxftype() not in ['MLINE']:
            anent=returnEnts(a)[0]         
            aresult = processEntity(anent, None)
            if aresult != None : #and isinstance(aresult,Part.Vertex)==False:
                c.append(aresult)
    #while any([isinstance(a,list)==True for a in c]):
    #    #print("Flattening in MLINE...")
    #    c=[item for sublist in c for item in sublist] #flatten hmm  ... if isinstance(c[0],list)==True?
    return c

def importOpenSCADdxf_LEADER(an_entity):
    new_entity = an_entity.explode()
    #c=[processEntity(a) for a in new_entity if a.dxftype()!='INSERT'] #list of entities that should then be processed
    c=list()
    #new_entity = [e for e in new_entity]
    for a in new_entity:
        if a.dxftype() not in ['LEADER']:
            anent=returnEnts(a)[0]
            aresult = processEntity(anent, None)
            if aresult != None : #and isinstance(aresult,Part.Vertex)==False:
                c.append(aresult)
    #while any([isinstance(a,list)==True for a in c]):
    #    #print("Flattening in LEADER...")
    #    c=[item for sublist in c for item in sublist] #flatten hmm  ... if isinstance(c[0],list)==True?
    return c

def importOpenSCADdxf_DIMENSION(an_entity):
    new_entity = an_entity.explode()
    #c=[processEntity(a) for a in new_entity if a.dxftype()!='INSERT'] #list of entities that should then be processed
    c=list()
    for a in new_entity:
        if a.dxftype() not in ['DIMENSION']:
            anent=returnEnts(a)[0]        
            aresult = processEntity(anent, None)
            if aresult != None : #and isinstance(aresult,Part.Vertex)==False:
                c.append(aresult)
    #while any([isinstance(a,list)==True for a in c]):
    #    #print("Flattening in DIMENSION...")
    #    c=[item for sublist in c for item in sublist] #flatten hmm  ... if isinstance(c[0],list)==True?
    return c

def importOpenSCADdxf_UNSUPPORTED(an_entity):
    print(an_entity.dxftype())
    print(an_entity.dxfattribs())
    global myent
    myent = an_entity
    return None

def processEntity(passed_entity, trace): #TODO: have this handle the list/not a list parameter
    if trace != None:
        print("CALLED FROM ",trace)

    edge_list = []
    an_edge = None

    if isinstance(passed_entity,list) == False:
        entity_list = [passed_entity]
    else:
        entity_list = passed_entity

    for an_entity in entity_list:
        if an_entity.dxftype() == 'LINE':
            an_edge=importOpenSCADdxf_LINE(an_entity)

        elif an_entity.dxftype() == 'POLYLINE': 
            an_edge=importOpenSCADdxf_POLYLINE(an_entity)

        elif an_entity.dxftype() == 'LWPOLYLINE':
            an_edge=importOpenSCADdxf_LWPOLYLINE(an_entity)

        elif an_entity.dxftype() == "SPLINE":
            an_edge=importOpenSCADdxf_SPLINE(an_entity)

        elif an_entity.dxftype() == 'CIRCLE':
            an_edge=importOpenSCADdxf_CIRCLE(an_entity)

        elif an_entity.dxftype() == 'ELLIPSE':  
            an_edge=importOpenSCADdxf_ELLIPSE(an_entity)

        elif an_entity.dxftype() == 'ARC':
            an_edge=importOpenSCADdxf_ARC(an_entity)

        elif an_entity.dxftype() == 'INSERT':
            an_edge=importOpenSCADdxf_INSERT(an_entity)

        elif an_entity.dxftype() == 'SOLID':
            an_edge=importOpenSCADdxf_SOLID(an_entity)

        elif an_entity.dxftype() == 'POINT':
            an_edge=importOpenSCADdxf_POINT(an_entity)

        elif an_entity.dxftype() in ['MLEADER','MULTILEADER']:
            an_edge=importOpenSCADdxf_MLEADER(an_entity)

        elif an_entity.dxftype() == 'MLINE':
            an_edge=importOpenSCADdxf_MLINE(an_entity)

        elif an_entity.dxftype() == 'LEADER':
            an_edge=importOpenSCADdxf_LEADER(an_entity)

        elif an_entity.dxftype() == 'DIMENSION':
            an_edge=importOpenSCADdxf_DIMENSION(an_entity)

        #elif an_entity.dxftype() in ['HATCH','MTEXT','TEXT','ATTDEF']:
        #    #print("Not supported : ", an_entity.dxftype())

        #elif an_entity.dxftype() in ['REGION','IMAGE']:
        #    #importOpenSCADdxf_UNSUPPORTED(an_entity)

        #else:
        #    #print("Unsupported type : ", an_entity.dxftype())

        if an_edge != None and isinstance(an_edge, Part.Vertex) == False:
            edge_list+=an_edge

    return edge_list

def returnEnts(arecord): #returns a list of things to convert to FC
    if arecord.dxftype() not in  ['INSERT','DIMENSION','LEADER','MLINE','MLEADER']:
        #print("RETURNING NON INSERT")
        if isinstance(arecord, list):
            return arecord
        else:
            return [arecord]
    else:
        #print("RETURNING INSERT")
        #return [e for e in arecord.block()]
        new_entity = arecord.explode()
        new_entity = [e for e in new_entity]
        return new_entity #bc it relocates components

def loadDXF(filepath):
    #based on https://ezdxf.readthedocs.io/en/stable/drawing/recover.html
    #NOTE: This expects ASCII DXF files
    #TODO: test if ZIP and handle that case??

    try:  # Slow path including fixing low level structures:
        print(f"Reading file {filepath}")
        doc, auditor = recover.readfile(filepath) #vs  doc = ezdxf.readfile(filename)
        print(f'Doc {doc}')
    except IOError:
        print(f'Not a DXF file or a generic I/O error.')
        return None
    except ezdxf.DXFStructureError:
        print(f'Invalid or corrupted DXF file : {filepath}.')
        return None

    # DXF file can still have unrecoverable errors, but this is maybe
    # just a problem when saving the recovered DXF file.
    if auditor.has_errors:
        print(f'Found unrecoverable errors in DXF file: {filepath}.')
        auditor.print_error_report()
        return None
    else:
        return doc

def makeFace(e):
    try:  #TODO: figure out why this sometimes is needed
        newwires = Part.Wire(e)
        # Create a face from the wire
        face = Part.Face(newwires)
    except:
        # Create a face from the wire
        try:
            face = Part.Face(e)
        except:
            face = None

    return face

def getLayerNames(thedoc, inlayers, exlayers):
    #Make sure we have a list of layers to include even if None
    if isinstance(inlayers,list) == False:
        layer=[inlayers]
    #Get list of any layers to exclude even if None
    if isinstance(exlayers,list) == False:
        exlayer=[exlayers]
    #Get list of all layers in DXF
    alldoclayernames = list(np.unique([e.dxf.layer for e in thedoc.entities]))
    print("ALL LAYER NAMES : ",alldoclayernames)

    our_layer_names=list() #where to store layer names we want and exist

    if len(alldoclayernames)>0:  #if there are actually layers to loop through ...
        if layer != [None] :  #layer(s) desired is specified
            #Get the layers we want
            our_layer_names=set(layer).intersection(set(alldoclayernames))
            #Get rid of any to exclude  #TODO: not tested yet
            our_layer_names=set(our_layer_names).difference(set(exlayer))
        else:
            print("Layer name provided not found")
        if len(our_layer_names) == 0:  #if we havent found a specified layer, look for defaults?
            print("No common layer name found; Selecting all")
            #TODO select one with most entities? 1st one? None?
            our_layer_names=alldoclayernames
    return  our_layer_names

def getFlatList(a_nested_list):
    flat_list = a_nested_list
    while any([isinstance(a,list)==True for a in flat_list]): #flatten
        old_list=[]
        for sublist in flat_list:
            if isinstance(sublist,list)==True:
                for item in sublist:
                    old_list+=[item]
            else:
                old_list+=[sublist]
        flat_list=old_list
    return flat_list

def makeholedshape(shapes) : #takes a list of faces

  def AholdsB(A, B): #test for A completely enclosing B
    if ((A.common(B).Area == B.Area) and (A != B)):
      return 1
    else :
      return 0
    
  import numpy as np
  num_shapes = len(shapes) #list of faces to start with
  ra = np.zeros((num_shapes, num_shapes)) # array to hold flag "A holds B"
    
  featurelist=list()
  for i in range(0,num_shapes): #use indexing because we should(?) only need to test a pair once
    obj=shapes[i]  #a face to test ...
    for j in range(i+1, num_shapes): #all other faces to test against
      holdflag = AholdsB(shapes[i],shapes[j]) #0,1=false, true; self=0
      if holdflag == 1: #only need to update array if A holds B
        ra[i,j]=holdflag #update array
        obj=obj.cut(shapes[j]) #iteratively cut out faces "held" by the face being tested
    featurelist.append(obj) #we're done with that so add it to the list

  ra2 = np.apply_along_axis(sum, 0, ra) #find out how many faces are contained by each

  #find indices of faces that should be holes
  #https://www.geeksforgeeks.org/python-get-indices-of-even-elements-from-list/
  holes = [idx for idx, ele in enumerate(ra2) if ((ele % 2 != 0) and (ele > 0))] #odd values = holes (always?)

  #make a new shape out of every face that does or doesn't have holes in it, but that isn't a hole itself
  obj = Part.makeCompound([shp for idx, shp in enumerate(featurelist) if idx not in holes])

  return obj

def importEZDXFsimple(filename=None, doc=None, inlayer=None, exlayer=None,retcompound=True,retfaces=False):
    dxfunits_table=[[0,'Unitless'],[1,'Inches'],[2,'Feet'],[3,'Miles'],[4,'Millimeters'],
      [5,'Centimeters'],[6,'Meters'],
      [7,'Kilometers'],[8,'Microinches'],[9,'Mils'],[10,'Yards'],[11,'Angstroms'],[12,'Nanometers'],
      [13,'Microns'],[14,'Decimeters'],[15,'Decameters'],[16,'Hectometers'],
      [17,'Gigameters'],[18,'Astronomical units'],[19,'Light years'],[20,'Parsecs']]

    FCunits_table=[[0,'mm'],[1,'m'],[2,'in'],[3,'in'],[4,'cm'],[5,'ft'],[6,'mm'],[7,'ft'],[8,'mm']]

    doc = loadDXF(filename)
    msp = doc.modelspace()
    if doc != None:
        if doc.units:
            print("DRAWING UNITS : ", doc.units,",", dxfunits_table[doc.units][1])
            print("FREECAD UNITS : ", FreeCAD.Units.getSchema())    
        entitylist=[]
        faces=[]
        points=[]
        edgefrompoints=[]
        edges=[]
        defaultlayerexists = False
        if "Default" in doc.layers:
            defaultlayerexists = True        
        layer_names = getLayerNames(doc,inlayer,exlayer)
        #allents0 = doc.chain_layouts_and_blocks() #this picks up things not in modelspace
        #allents = msp.query('*')
        for a_layer in layer_names:
            each_layer = a_layer
            if a_layer == '0':
                if defaultlayerexists:
                    each_layer='Default'
            #entities = msp.query(f'*[layer=="{each_layer}"]') 
            #layerents=[e for e in allents if e.dxf.layer==each_layer]
            #if entity.dxf.layer in layer_names:
            ##based on: https://www.github.com/mozman/ezdxf/issues/910
            plines=query.EntityQuery(disassemble.recursive_decompose(msp),query=f'*[layer=="{each_layer}"]')
            entities = [x for x in plines]
            for entity in entities:
                edges=[]
                #print(entity.dxf.layer, entity.dxftype())
                #print(entity)
                anent=returnEnts(entity)
                #print("ANENT LEN ",len(anent))
                #print(anent)
                if anent != None:
                    if isinstance(anent,list)==True:
                        #print("here")
                        for a in anent:
                            edges+=processEntity(a, None)
                    else:
                        print("over here")
                        edges = processEntity(anent, None)            
                #print(entity.dxftype())
                #edges = processEntity(entity,trace=None)
                #while any([isinstance(a,list)==True for a in edges]): #flatten
                #    edges=[item for sublist in edges for item in sublist]                
                #print("EDGE LEN ",len(edges))
                if edges:
                    if len(edges)==1:
                        if isinstance(edges[0],Part.Vertex)==True:
                            points+=edges
                        else:
                            entitylist+=edges                        
                    else:
                        if len(points)>1:  #were onto a new entity; collect points in an edge
                            if len(points)==2:
                                edgefrompoints=[Part.makeLine(points[1].Point,points[0].Point)] #needs to be a list
                            else:
                                for i in range(len(points)-1):
                                    edgefrompoints.append(points[i+1].Point.sub(points[i].Point))
                                edgefrompoints=Part.makePolygon(edgefrompoints).Edges
                            #edgefrompoints=Part.sortEdges(edgefrompoints) ########### [0]
                            entitylist+=edgefrompoints #is a list #dont add for now ...?
                            points=[]
                            edgefrompoints=[]
                        ##print(entity.dxftype())
                        #print((edges))
                        #edges = Part.sortEdges(edges)[0]  #should only be edges... sortEdges wraps in list
                        #print((edges))
                        entitylist+=[edges]
            #end of for entity loop
            entitylist=getFlatList(entitylist)
            #entitylist=Part.sortEdges(entitylist)[0] #sort            
        #end of layer loop
        #entitylist = getFlatList(entitylist)
        #entitylist=Part.sortEdges(entitylist) #sort
        #print(entitylist)
        if len(entitylist)>0:
            #for el in entitylist:
            if 1:
                el=entitylist
                global myel
                myel = el
                #print("MY EL ",myel)
                if isinstance(el,list) == True:
                    e = Part.sortEdges(el)
                else:
                    e = Part.sortEdges([el])
                for e2 in e: #only make a face from non-lines
                    face = makeFace(e2)
                    if face != None:
                        faces+=[face]
                    #else:
                    #    global myface
                    #    myface = e2
                    #    print("no face made") 
                if len(faces)>0:
                    if retcompound==True and retfaces==False:
                        return Part.Compound(faces)
                    elif retcompound==False and retfaces==True:
                        return faces
                    else:
                        return Part.Compound(faces), faces                    
                else:
                    print("couldnt make faces?")
                    return       
        else:
            print("No entities to import found")
            return
    else:
        print("Invalid file?")
        return

def importEZDXFshape(filename=None, doc=None, inlayer=None, exlayer=None, flattenlayers=True, explodelayers=False, explodez=1.0,retcompound=True,retfaces=False, withholes=True):

    #TODO : deal with any units specified in DXF?
    #NOT DEALT WITH : 3D objects, linewidths, colors, user data
    dxfunits_table=[[0,'Unitless'],[1,'Inches'],[2,'Feet'],[3,'Miles'],[4,'Millimeters'],[5,'Centimeters'],[6,'Meters'],
      [7,'Kilometers'],[8,'Microinches'],[9,'Mils'],[10,'Yards'],[11,'Angstroms'],[12,'Nanometers'],
      [13,'Microns'],[14,'Decimeters'],[15,'Decameters'],[16,'Hectometers'],
      [17,'Gigameters'],[18,'Astronomical units'],[19,'Light years'],[20,'Parsecs']]

    FCunits_table=[[0,'mm'],[1,'m'],[2,'in'],[3,'in'],[4,'cm'],[5,'ft'],[6,'mm'],[7,'ft'],[8,'mm']]
    #Load the DXF file using ezdxf    
    doc = loadDXF(filename)

    if doc != None:
        if doc.units:
            print("DRAWING UNITS : ", doc.units,",", dxfunits_table[doc.units][1])
            print("FREECAD UNITS : ", FreeCAD.Units.getSchema())
        #Get the modelspace
        msp = doc.modelspace()
        #allents = doc.chain_layouts_and_blocks()
        allents=msp.query('*')

        ##Make sure we have a list of layers to include even if None
        #if isinstance(layer,list) == False:
        #    layer=[layer]
        ##Get list of any layers to exclude even if None
        #if isinstance(exlayer,list) == False:
        #    exlayer=[exlayer]
        ##Get list of all layers in DXF
        #layernames = list(np.unique([e.dxf.layer for e in doc.entities]))
        #print("ALL LAYER NAMES : ",layernames)

        #if len(layernames)>0:  #if there are actually layers to loop through ...
        if 1:
            #layer_names=list() #where to store layer names we want and exist

            #if layer != [None] :  #layer(s) desired is specified
            #    #Get the layers we want
            #    layer_names=set(layer).intersection(set(layernames))
            #    #Get rid of any to exclude  #TODO: not tested yet
            #    layer_names=set(layer_names).difference(set(exlayer))
            #else:
            #    print("Layer name provided not found")

            #if len(layer_names) == 0:  #if we havent found a specified layer, look for defaults?
            #    print("No common layer name found; Selecting all")
            #    #TODO select one with most entities? 1st one? None?
            #    layer_names=layernames
            defaultlayerexists = False
            if "Default" in doc.layers:
                defaultlayerexists = True
            layer_names = getLayerNames(doc,inlayer,exlayer)
            layerentitylist=[] #list of list of processed entities per layer

            ##for each_layer in layer_names:  #for the layer(s) we want ....
            for a_layer in layer_names:
                each_layer = a_layer
                if a_layer == '0':
                  if defaultlayerexists:
                    each_layer='Default'
                # Initialize an empty list to hold the faces, entities and entity names
                entitylist=list()
                points=[]
                edgefrompoints=[]                
                ##entities = msp.query(f'*[layer=="{each_layer}"]') #get all the entities on that layer
                plines=query.EntityQuery(disassemble.recursive_decompose(msp),query=f'*[layer=="{each_layer}"]')
                entities = [x for x in plines]
                for entity in entities: #loop through all the entities, process and store in lists
                #layerents=[e for e in allents if e.dxf.layer==each_layer]
                #for entity in layerents:
                    edges=[]
                    #print(entity.dxf.layer, entity.dxftype())
                    #print(entity)
                    anent=returnEnts(entity)
                    #print("ANENT LEN ",len(anent))
                    #print(anent)
                    if isinstance(anent,list)==True:
                        for a in anent:
                            edges+=processEntity(a, None)
                    else:
                        edges = processEntity(anent, None)

                    #if edges:
                    #    if len(edges)>1:
                    #        edges = Part.sortEdges(edges)[0]  #should only be edges... sortEdges wraps in list
                    #    
                    #    entitylist+=edges
                    #print("LEN EDGES ",len(edges))
                    if edges:
                    #if 1==2:
                        edges=getFlatList(edges)
                        if len(edges)==1:
                            if isinstance(edges[0],Part.Vertex)==True:
                                points+=edges
                            else:
                                entitylist+=edges                        
                        else:
                            if len(points)>1:  #were onto a new entity; collect points in an edge
                                if len(points)==2:
                                    edgefrompoints=[Part.makeLine(points[1].Point,points[0].Point)] #needs to be a list
                                else:
                                    for i in range(len(points)-1):
                                        edgefrompoints.append(points[i+1].Point.sub(points[i].Point))
                                    edgefrompoints=Part.makePolygon(edgefrompoints).Edges
                                    edgefrompoints=Part.sortEdges(edgefrompoints)[0]
                                entitylist+=edgefrompoints
                                points=[]
                                edgefrompoints=[]
                            #if len(edges)>1:
                            #    print(entity.dxftype())
                            #    print(edges)
                            #    #edges = Part.sortEdges(edges)[0]  #should only be edges... sortEdges wraps in list
                            entitylist+=edges                    
                #end of for entity loop
                if len(entitylist)>0:
                    #print(len(entitylist))
                    ##while any([isinstance(a,list)==True for a in entitylist]): #flatten
                    ##    entitylist=[item for sublist in entitylist for item in sublist]
                    #print(len(entitylist))
                    #entitylist=Part.sortEdges(entitylist)[0] #sort #drops items out????
                    #print("---------------",len(entitylist))
                    layerentitylist.append(entitylist) #WANT to add as a list so we can differentiate among layers
            #for i in range(len(layerentitylist)):
            #    print("LAYERENTLIST LEN ",len(layerentitylist[i]))
            #end of for layer loop
            faces=[]
            face=None
            global mylayerlist #export everything we got
            mylayerlist = layerentitylist
            print("NUMBER OF LAYERS : ",len(layerentitylist))
            if len(layerentitylist)>0:
                #if flattenlayers==True :
                #    while any([isinstance(a,list)==True for a in layerentitylist]):
                #        print("Flattening...")
                #        layerentitylist=[item for sublist in layerentitylist for item in sublist] #flatten
                #    layerentitylist=Part.sortEdges(layerentitylist)[0]  #should only be edges...
                #    print("FLATTENED EVERYTHING.  NUMBER OF ENTITIES : ",len(layerentitylist))

                for i in range(len(layerentitylist)):
                    entitylist = layerentitylist[i]
                    entitylist = getFlatList(entitylist)
                    #print(entitylist)
                    e=Part.sortEdges(entitylist)
                    for e2 in e: #only make a face from non-lines
                        face = makeFace(e2)
                        if face != None:
                            faces+=[face]                    
                    #if 1:
                    #    entitylist = layerentitylist[i] #This should be a list of entities in the ith layer
                    #    if isinstance(entitylist[0], list) == False:  #make a list of entities
                    #        print("making a list")
                    #        entitylist=[entitylist]
                    #    elif len(entitylist)==1 and isinstance(entitylist[0],list)==True: #is it a list of a list??
                    #        print("list of list?")
                    #        entitylist=[entitylist[0]]
                    #if len(entitylist)>1:
                    #    print("WHY ARE WE HERE???????????????")
                    #for el in entitylist:
                    #    if isinstance(el,list) == True:
                    #        e = Part.sortEdges(el)
                    #    else:
                    #        e = Part.sortEdges([el])

                    #    for e2 in e: #only make a face from non-lines
                    #        face = makeFace(e2)
                    #        if face != None:
                    #            faces+=[face]

                        ##faces+=[makeFace(item) for sublist in e for item in sublist] # += concats, doesn't wrap in list like append
                        ##myfaces+=[makeFace(item) for sublist in e for item in sublist]
                #end of for layers loop

                # If more than one Face create a compound Shape
                if len(faces)>0:
                    print("withholes : ",withholes)
                    if withholes == False:
                        compound = Part.makeCompound(faces)
                    else:
                        compound = makeholedshape(faces)
                    if retcompound==True and retfaces==False:
                        if compound:
                            return compound
                        else:
                            return None
                    elif retcompound==False and retfaces==True:
                        return faces
                    else:
                        if compound:
                            return compound, faces
                        else:
                            print("Shouldnt get here?")
                            return None, faces
                else:
                    print("Problem with faces/compound creation")
                    return None, None

            else:
                print("No layers extracted")
                return None
        else:
            print("No layers found")
            return None
    else:
        print("Invalid file")
        return None
