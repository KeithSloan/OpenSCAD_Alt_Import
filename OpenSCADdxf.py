def importEZDXFface(filename,layer=None,doc=None):
    import ezdxf
    import Part
    fdoc = doc or FreeCAD.activeDocument()
    ddoc = ezdxf.readfile(filename)
    msp = ddoc.modelspace()    
    lines = msp.query('LINE')
    splines = msp.query('SPLINE')
    plines = msp.query('POLYLINE')
    lwplines = msp.query('LWPOLYLINE')
     
    faces=list()
    face_l=None
    face_p=None
    face_lwp=None
    
    if len(lines)>0:
        elements = []
        for l in lines:
            if l.dxf.start != l.dxf.end:
                poly = Part.makeLine(tuple(l.dxf.start), tuple(l.dxf.end)) #makes Edge object
            else:
                print("START==END")
            #poly = Part.Wire(poly) #makes Wire object
            elements.append(poly)  #creates list of Wires for use in Part.Face
        face_l=Part.Wire(elements) #L
        
    '''
    if len(splines)>0:                  
        for s in splines:
            print("SPLINE")
            #s.control_points
            #s.fit_points
    '''
    
    if len(plines)>0:
        for p in plines:
            #print("POLYLINE")
            verts = p.vertices
            verts = [tuple(v.dxf.location) for v in verts]
            if p.is_closed:
                verts += [verts[0]]
            poly = Part.makePolygon(verts)
        face_p=poly #P
    
    if len(lwplines)>0:
        elements=[]
        for lwp in lwplines:
            #print("LWPOLYLINE")
            with lwp.points("xy") as points: #xyseb
                for p in points: #TODO: vectorize??
                    poly = tuple([p[0], p[1], 0])
                    elements.append(poly)
                poly = Part.makePolygon(elements) #makes a Wire
        face_lwp=poly #LWP
        
    if face_l != None:
        faces.append(face_l)
    if face_p != None:
        faces.append(face_p)
    if face_lwp != None:
        faces.append(face_lwp)
        
    faces=Part.Face(faces)
    
    #if (len(ddoc.entities) != len(lines)+len(splines)+len(plines)+len(swplines):
    #    print("NOT ALL ENTITIES DEALT WITH")  

    return faces 
