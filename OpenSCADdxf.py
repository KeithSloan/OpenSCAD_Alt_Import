def importEZDXFface(filename=None,layer=None,doc=None,exlayers=None):
  import numpy as np
  from FreeCAD import Vector
  import Part
  from ezdxf import recover
  #ddoc = ezdxf.readfile(filename)
  #try:
  ddoc, auditor = recover.readfile(filename)
  #except IOError:
  #    print(f'Not a DXF file or a generic I/O error.')
  #    #sys.exit(1)
  #except ezdxf.DXFStructureError:
  #    print(f'Invalid or corrupted DXF file.')
  #    #sys.exit(2)

  # DXF file can still have unrecoverable errors, but this is maybe just
  # a problem when saving the recovered DXF file.
  if auditor:
    if auditor.has_errors:
      auditor.print_error_report()

  #layernames = [layer.dxf.name for layer in ddoc.layers] #doesn't catch everything??
  layernames = np.unique([e.dxf.layer for e in ddoc.entities])
  print("ALL LAYER NAMES : ",layernames)
  layer_names=list()
  if layer != None :
    if layer in layernames:
      layer_names=[layer] #ok, just take that one layer
    else:
      print("Invalid layer name")
  else:
    layer_names=layernames #TODO: should only take 1??
  #if len(layer_names)>0:
  #  print(layer_names)
  faces=list()
  if len(layer_names)>0:
    #msp = ddoc.modelspace()
    elements=list()
    for e in ddoc.entities:  #loop through all entities
      if e.dxf.layer in layer_names: #select relevant layer
        if e.dxftype() == "LINE":
          if e.dxf.start != e.dxf.end:  #ensure it isn't effectively a point
            #aline = Part.makeLine(Vector(e.dxf.start), Vector(e.dxf.end)) #makes Edge object
            aline = Part.makeLine( Vector(e.dxf.start[0],e.dxf.start[1],0),
                                   Vector(e.dxf.end[0],e.dxf.end[1],0)) #makes Edge object
            awire=Part.Wire(aline)
            if len(elements)>0:
              if awire != elements[-1]:
                elements.append(awire)  #creates list of Wires for use in Part.Face  
              else:
                print("DUPLICATE ELEMENT?")
            else:
              elements.append(awire)  #creates list of Wires for use in Part.Face            
          else: #else we found a point???
            print("START==END?") #TODO: trap this??
            print("CURRENT START/END : ", e.dxf.start, e.dxf.end)
            print("PRIOR START : ", elements[-1].Vertexes[0].X, elements[-1].Vertexes[0].Y)
            print("PRIOR END : ", elements[-1].Vertexes[1].X, elements[-1].Vertexes[1].Y)
            print("FIRST START : ", elements[0].Vertexes[0].X, elements[0].Vertexes[0].Y)
            print("FIRST END : ", elements[0].Vertexes[1].X, elements[0].Vertexes[1].Y)
                        
        if e.dxftype() == "SPLINE":
          if 1:
            #print("SPLINE")
            #https://forum.freecad.org/viewtopic.php?style=10&t=9894
            #https://forum.freecad.org/viewtopic.php?t=35644
            #fits=list()
            #if e.fit_point_count()>0:
            #  fits = e.fit_points
            #knots=list()
            #if e.knot_count()>0:
            #  knots = e.knots
            control_points=()
            if e.control_point_count()>0:                    
              control_points = e.control_points
            #weights=()
            #weights = e.weights
            #weights = [1,1,1,1]
            #n = len(control_points)-1
            control_points=tuple(control_points)
            aspline = Part.BSplineCurve()
            aspline.buildFromPoles(control_points, False, 3)
            elements.append(Part.Wire(aspline.toShape()))

        if e.dxftype() == "POLYLINE":          
          if 1:
            #print("POLYLINE")
            verts = e.vertices
            verts = [tuple(v.dxf.location) for v in verts]
            if e.is_closed:
              verts += [verts[0]]
              poly = Part.makePolygon(verts)
            elements.append(poly)
            
        if e.dxftype() == "LWPOLYLINE":            
          if 1:
            elements2=[]
            if 1:
              #print("LWPOLYLINE")
              with e.points("xy") as points: #xyseb
                  for p in points: #TODO: vectorize??
                      #print("P = ", p)
                      poly = tuple([p[0], p[1], 0])
                      elements2.append(poly)
              #print("LWPOLY LEN : ",len(elements2))
              if len(elements2)>1: #could get a point???
                  poly = Part.makePolygon(elements2) #makes a Wire
                  elements.append(poly)
    
    try:  #TODO: figure out why this sometimes is needed
      faces = Part.Face(elements)
    except:
      faces = Part.Wire(elements)
      faces = Part.Face(faces)    
  else:
    print("No layers available")
     
  return faces


