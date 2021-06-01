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

    ------------------------------

        -

"""

import random
import matplotlib.pyplot as plt

class Vertex:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incidentEdge = None

    #função que calcula o reflexo ao point sobre a reta definida por point1 e point2
    def mirror(self, point1, point2):
        if(point2.x == point1.x):
            if(self.x < point1.x):
                dist = point1.x - self.x
                self.x = self.x + dist*2
                self.y = self.y
            else:
                dist = self.x - point1.x
                self.x = self.x - dist*2
                self.y = self.y
        else:
            m = (point2.y - point1.y) / (point2.x - point1.x)
            c = (point2.x * point1.y - point1.x * point2.y) / (point2.x - point1.x)

            d = (self.x + (self.y - c) * m) / (1 + m * m)

            self.x = 2 * d - self.x
            self.y = 2 * d * m - self.y + 2 * c

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
        self.isOutside = False

class DCEL:

    def __init__(self):
        self.vertices = []
        self.faces = []
        self.halfEdges = []
    
    def __str__(self):
        output = "Vertex:\n"
        output += "| Vertex | Coordinates | IncidentEdge |\n"
        for vertex in self.vertices:
            output += "| v" + str(self.vertices.index(vertex)+1) + " | (" + str(vertex.x) + ", " + str(vertex.y) + ") | e" + str(self.halfEdges.index(vertex.incidentEdge)+1) + " |\n"

        output += "Half-edges\n"
        output += "| Half-edge | Origin | Twin | IncidentFace | Next | Previous | isOutside |\n"
        for edge in self.halfEdges:
            output += "| e" + str(self.halfEdges.index(edge)+1) + " |"
            output += " v" + str(self.vertices.index(edge.origin)+1) + " |"
            output += " e" + str(self.halfEdges.index(edge.twin)+1) + " |"
            output += " f" + str(self.faces.index(edge.incidentFace)+1) + " |"
            output += " e" + str(self.halfEdges.index(edge.next)+1) + " |"
            output += " e" + str(self.halfEdges.index(edge.prev)+1) + " |"
            output += " " + str(edge.isOutside) + " |"
            output += "\n"

        output += "Faces\n"
        output += "| Face | Edge |\n"
        for face in self.faces:
            output += "| f" + str(self.faces.index(face)) + " | e" + str(self.halfEdges.index(face.edge)) + " |\n"

        return output

    def get_outside_edges(self):

        outsideEdges = []

        for edge in self.halfEdges:
            if edge.isOutside:
                outsideEdges.append(edge)

        return outsideEdges

    def insideFaces_to_xy(self):

        x = []
        y = []

        for i in range(1,len(self.faces)):

            fEdge = self.faces[i].edge
            x.append(fEdge.origin.x)
            y.append(fEdge.origin.y)
            
            j = fEdge.next
            while j != fEdge:
                x.append(j.origin.x)
                y.append(j.origin.y)
                j = j.next

            x.append(fEdge.origin.x)
            y.append(fEdge.origin.y)
        
        print(x)
        print(y)

        return x,y

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

            he2.isOutside = True

            self.halfEdges.append(he1)
            self.halfEdges.append(he2)

        #print("Len halfEdges:" + str(len(self.halfEdges)))

        # Add faces

        self.faces.append(Face(self.halfEdges[1]))
        self.faces.append(Face(self.halfEdges[0]))
        
        for i in range(0,len(self.halfEdges)):

            if i%2:
                self.halfEdges[i].incidentFace = self.faces[1]
            else:
                self.halfEdges[i].incidentFace = self.faces[0]

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

        edge.isOutside = False

        vertex = any(elem.x == x and elem.y == y for elem in self.vertices)

        if vertex == False: #is new vertex

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

            he1.isOutside = True
            he2.isOutside = True

            self.vertices.append(v1)
            self.halfEdges.append(he1)
            self.halfEdges.append(he1.twin)
            self.halfEdges.append(he2)
            self.halfEdges.append(he2.twin)
            self.faces.append(he1.incidentFace)

        else:

            he1 = HalfEdge(vertex)
            he1.incidentFace = Face(he1)
            he1.twin = HalfEdge(vertex)
            he1.twin.incidentFace = edge.incidentFace

            for edge2 in self.get_outside_edges:
                if edge2.origin == vertex and edge2.next.origin == edge.origin: # vertex to edge origin
                    #add edge from edge next to vertice
                    he1.next = edge2
                    he1.prev = edge
                    
                    he1.twin.next = edge.next
                    he1.twin.prev = edge2.prev

                    edge2.prev.next = he1.twin
                    edge2.prev = he1
                    edge2.incidentFace = he1.incidentFace

                    edge.next.prev = he1.twin
                    edge.next = he1
                    edge.incidentFace = he1.incidentFace

                    edge2.isOutside = False
                    break
                elif edge2.origin == edge.next.origin and edge2.next.origin == vertex: # edge next origin to vertex
                    #add edge from vertex to edge origin
                    he1.next = edge
                    he1.prev = edge2

                    he1.twin.next = edge2.next
                    he1.twin.prev = edge.prev

                    edge2.next.prev = he1.twin
                    edge2.next = he1
                    edge2.incidentFace = he1.incidentFace
                    
                    edge.prev.next = he1.twin
                    edge.prev = he1
                    edge.incidentFace = he1.incidentFace
                    break

            self.halfEdges.append(he1)
            self.halfEdges.append(he1.twin)
            self.faces.append(he1.incidentFace)


# insideTri uses the barycentric coordinate system to find if point4 is inside the triangle formed by point1,2,3
def insideTri(point1, point2, point3, point4):

    denominator = ((point2.y-point3.y)*(point1.x-point3.x) + (point3.x-point2.x) * (point1.y - point3.y))
    a = ((point2.y - point3.y) * (point4.x - point3.x) + (point3.x-point2.x) * (point4.y-point3.y)) / denominator
    b = ((point3.y-point1.y) * (point4.x - point3.x) + (point1.x - point3.x) * (point4.y - point3.y)) / denominator
    c = 1 - a - b 
    return 0 <= a and a <= 1 and 0 <= b and b <= 1 and 0 <= c and c <= 1

def next_point(dcel):

    edges = dcel.get_outside_edges()

    edge = edges[random.randint(0,len(edges)-1)]
    v1 = Vertex(edge.origin.x,edge.origin.y)
    v2 = Vertex(edge.next.origin.x,edge.next.origin.y)

    minDist = 2

    v1.x += minDist
    v2.x += minDist

    m = Vertex((v1.x+v2.x)/2, (v1.y+v2.y)/2) # Mid point
    o = Vertex((v1.x-m.x)*3**0.5, (v1.y-m.y)*3**0.5)

    v3 = Vertex(m.x+o.y,m.y-o.x)
    v4 = Vertex(m.x-o.y,m.y+o.x)

    r1 = random.uniform(0,1)
    r2 = random.uniform(0,1)

    newv = Vertex(r1 * (v1.x-v3.x) + r2 * (v2.x-v3.x),r1 * (v1.y-v3.y) + r2 * (v2.y-v3.y))

    newv.x += v3.x
    newv.y += v3.y

    # if not insideTri(v1,v2,v3,newv):
    #     newv.mirror(v1,v2)

    if v1.y == v2.y:
        if not insideTri(v1,v2,v4,newv):
                newv.mirror(v1,v2)
    else:
        if not insideTri(v1,v2,v3,newv):
                newv.mirror(v1,v2)


    # if v1.x == v2.x:
    #     if v1.y > v2.y: #is right edge
    #         if not insideTri(v1,v2,v3,newv):
    #             newv.mirror(v1,v2)
    #     else: #is left edge
    #         if not insideTri(v1,v2,v4,newv):
    #             newv.mirror(v1,v2)
    # elif v1.y == v2.y:
    #     if v1.x > v2.x: #is bottom edge
    #         if not insideTri(v1,v2,v4,newv):
    #             newv.mirror(v1,v2)
    #     else: #is top edge
    #         if not insideTri(v1,v2,v3,newv):
    #             newv.mirror(v1,v2)
    # elif v1.y > v2.y:
    #     if v1.x < v2.x: #top down right
    #         if not insideTri(v1,v2,v3,newv):
    #             newv.mirror(v1,v2)
    #     else: #top down left
    #         if not insideTri(v1,v2,v4,newv):
    #             newv.mirror(v1,v2)
    # elif v1.y < v2.y:
    #     if v1.x < v2.x: #bottom top right
    #         if not insideTri(v1,v2,v3,newv):
    #             newv.mirror(v1,v2)
    #     else: #bottom top left
    #         if not insideTri(v1,v2,v4,newv):
    #             newv.mirror(v1,v2)


    return edge,newv


def main():

    triangle1 = [(1,2),(2,2),(2,3)]
    print(str(DCEL.tree_vertices_to_ccw_edges(triangle1)))

    myDCEL = DCEL()
    myDCEL.build_triangular_dcel(triangle1)
    print(myDCEL)

    #edg = myDCEL.halfEdges[4]
    #myDCEL.add_vertex(edg,4,3)

    n = int(input("Nº of vertices: "))

    for i in range(0,n):
        edge,vertex = next_point(myDCEL)
        myDCEL.add_vertex(edge,vertex.x,vertex.y)

    print(myDCEL)

    x,y = myDCEL.insideFaces_to_xy()

    plt.plot(x,y)
    plt.show()



if __name__ == "__main__":
    main()