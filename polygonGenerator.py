"""
    Things to consider:
        - Polygon with n-vertices:
        - Coordinates of the vertices are non-negative and smaller than M
        - Output is the vertices of the polygon in CCW (DCEL)

    TO DO:
        [x] - CCW order 3 points
        [] - Polygon with n-vertices: (n ≥ 3) or give error
        [] - 

    To add vertex:
        - Choose an edge
        - Get a random point Inside the two semi circules
            - Given by the size of smallest edge and size of the sum two largest edge and the largets angle (inside m range)
        - 

"""

import random
import math

class Vertex:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incidentEdge = None

class Face:

    def __init__(self, edge):
        self.edge = edge

class HalfEdge:

    def __init__(self,origin):
        self.origin = origin
        self.twin = None
        self.incidentFace = None
        self.next = None
        self.prev = None

class DCEL:

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.halfEdges = []
        self.outsideEdges = []
    
    def __str__(self):
        output = "Vertex:\n"
        output += "| Vertex | Coordinates | IncidentEdge |\n"
        for vertex in self.vertices:
            output += "| v" + str(self.vertices.index(vertex)+1) + " | (" + str(vertex.x) + ", " + str(vertex.y) + ") | e" + str(self.halfEdges.index(vertex.incidentEdge)+1) + " |\n"

        output += "Half-edges\n"
        output += "| Half-edge | Origin | Twin | IncidentFace | Next | Previous |\n"
        for edge in self.halfEdges:
            output += "| e" + str(self.halfEdges.index(edge)+1) + " |"
            output += " v" + str(self.vertices.index(edge.origin)+1) + " |"
            output += " e" + str(self.halfEdges.index(edge.twin)+1) + " |"
            output += " f" + str(self.faces.index(edge.incidentFace)+1) + " |"
            output += " e" + str(self.halfEdges.index(edge.next)+1) + " |"
            output += " e" + str(self.halfEdges.index(edge.prev)+1) + " |"
            output += "\n"

        output += "Faces\n"
        output += "| Face | Edge |\n"
        for face in self.faces:
            output += "| f" + str(self.faces.index(face)) + " | e" + str(self.halfEdges.index(face.edge)) + " |\n"

        return output

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

    def build_triangular_dcel(self, points):

        edges = DCEL.tree_vertices_to_ccw_edges(points)

        # Add vertices

        for edge in edges:
            self.vertices.append(Vertex(edge[0][0],edge[0][1]))

        # Add HalfEdge

        for i in range(0,3):
            v1 = self.vertices[i]
            v2 = self.vertices[(i+1)%3]

            he1 = HalfEdge(v1)
            he2 = HalfEdge(v2)

            he1.twin = he2
            he2.twin = he1

            v1.incidentEdge = he1
            v2.incidentEdge = he2

            self.halfEdges.append(he1)
            self.halfEdges.append(he2)

        #print("Len halfEdges:" + str(len(self.halfEdges)))

        # Add faces

        self.faces.append(Face(self.halfEdges[0]))
        self.faces.append(Face(self.halfEdges[1]))

        for i in range(0,len(self.halfEdges)):

            if i%2:
                self.halfEdges[i].incidentFace = self.faces[0]
            else:
                self.halfEdges[i].incidentFace = self.faces[1]

            j = (i+2)%(len(self.halfEdges))
            #print("next of " + str(i) + " is " + str(j))

            self.halfEdges[i].next = self.halfEdges[j]
            if i==0:
                self.halfEdges[i].prev = self.halfEdges[len(self.halfEdges)-2]
            elif i==1:
                self.halfEdges[i].prev = self.halfEdges[len(self.halfEdges)-1]
            else:
                self.halfEdges[i].prev = self.halfEdges[i-2]

    def add_vertex(self,edge,x,y):

        v1 = Vertex(x,y)
        he1 = HalfEdge(edge.next.origin)
        he2 = HalfEdge(v1)
        v1.incidentEdge = he1

        he1.next = he2
        he1.prev = edge
        he1.incidentFace = Face(he1)

        he2.next = edge
        he2.prev = he1
        he2.incidentFace = he1.incidentFace

        he1twin = HalfEdge(v1)
        he2twin = HalfEdge(edge.origin)
        
        he1.twin = he1twin
        he1.twin.twin = he1
        he2.twin = he2twin
        he2.twin.twin = he2

        edge.prev.next = he2.twin
        he2.twin.next = he1.twin
        he2.twin.prev = edge.prev
        he2.twin.incidentFace = edge.incidentFace

        edge.next.prev = he1.twin
        he1.twin.next = edge.next
        he1.twin.prev = he2.twin
        he1.twin.incidentFace = edge.incidentFace

        edge.prev = he2
        edge.next = he1
        edge.incidentFace = he1.incidentFace

        self.vertices.append(v1)
        self.halfEdges.append(he1)
        self.halfEdges.append(he1.twin)
        self.halfEdges.append(he2)
        self.halfEdges.append(he2.twin)
        self.faces.append(he1.incidentFace)

class NewPointArea:

    def get_angle(a,b,c):
        ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]))
        return math.radians(ang + 360) if ang < 0 else math.radians(ang)

def next_point(n,dcel):

    #120º -> 

    # get an edge from the outside face
    edg = dcel.faces[1].edge

    for i in range(0,random(0,n)):
        edg = edg.next

    # get inside triangle for this edge
    triangle = [edg.twin]
    triangle.append(edg.twin.next)
    triangle.append(edg.twin.next.next)
    ang = get_angle((triangle[0].origin.x,triangle[0].origin.y),(triangle[1].origin.x,triangle[1].origin.y),(triangle[2].origin.x,triangle[2].origin.y))



    # find middle of edge
    # get 

    pass

def main():
    triangle1 = [(1,2),(3,0),(4,1)]
    print(str(DCEL.tree_vertices_to_ccw_edges(triangle1)))

    myDCEL = DCEL()
    myDCEL.build_triangular_dcel(triangle1)
    print(myDCEL)
    edg = myDCEL.halfEdges[4]

    myDCEL.add_vertex(edg,4,3)

    print(myDCEL)

if __name__ == "__main__":
    main()