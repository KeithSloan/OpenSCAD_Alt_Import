from OpenSCADFeatures import CGALFeatureObject

def minkowski(p):

    if len(p[6]) == 2 and p[6][1].TypeId == 'Part::Sphere':
       obj1 = p[6][0]
       obj2 = p[6][1]
       print(dir(obj2))
       return obj1

    else:
       return CGALFeatureObject(p[1],p[6],p[3])

