from OpenSCADFeatures import CGALFeatureObject

def minkowski(p):

    if len(p[6]) == 2 and p[6][1].TypeId == 'Part::Sphere':
       obj1 = p[6][0]
       obj2 = p[6][1]
       print(dir(obj2))
       return obj1

    # - For minkowski Just indicate first shape needs editing

    if len(p[6]) == 2 :
       # return just first object
       #print(dir(p[6][0]))
       #print(dir((p[6][1]).ViewObject))
       #print(p[6][0].TypeId)
       p[6][0].ViewObject.ShapeColor = (1.,0.,0.)
       setObjColor(p[6][0],(1.,0.,0.))
       setOutListColor(p[6][0],(1.,0.,0.))
       #print(p[6][1].TypeId)
       p[6][1].ViewObject.ShapeColor = (0.,1.,0.)
       setObjColor(p[6][1],(0.,1.,0.))
       setOutListColor(p[6][1],(1.,0.,0.))
       #p[6][1].ViewObject.hide()
       p[0] = [p[6][0]]

    else:
       return CGALFeatureObject(p[1],p[6],p[3])

