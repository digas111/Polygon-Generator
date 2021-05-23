"""
    Things to consider:
        - Polygon with n-vertices:
        - Coordinates of the vertices are non-negative and smaller than M
        - Output is the vertices of the polygon in CCW (DCEL)

    TO DO:
        [x] - CCW order 3 points
        [] - Polygon with n-vertices: (n ≥ 3) or give error
        [] - 
"""

import math as m

class Vertex:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incidentEdge = None

class Face:

    def __init__(self, edge):
        self.edge = edge

class HalfEdge:

    def __init__(self,origin,twin,incidentFace,next,prev):
        self.origin = origin
        self.twin = twin
        self.incidentFace = incidentFace
        self.next = next
        self.prev = prev

def tree_vertices_to_ccw_edges(points):

        if len(points) != 3:
            #give error
            pass
        
        xsorted = sorted(points, key=lambda tup: tup[0])
        first = xsorted.pop(0)
        ysorted = sorted(xsorted, key=lambda tup: tup[1])
        second = ysorted.pop(0)
        third = ysorted.pop(0)
        #return [first] + ysorted
        return [(first,second),(second,third),(third,first)]


class DCEL:
    def __init__(self):
        self.vertices = []
        self.faces = []
        self.halfEdges = []

    def build_dcel(self, points):

        # Add vertices

        for point in points:
            self.vertices.append(Vertex(point[0],point[1]))

        # Add HalfEdge

        for vertice in self.vertices:
            self.halfEdges.append()




        pass



def main():
    triangle1 = [(1,2),(3,0),(4,1)]
    print(str(tree_vertices_to_ccw_edges(triangle1)))

if __name__ == "__main__":
    main()