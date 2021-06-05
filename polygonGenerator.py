"""
Code by: Diogo Ribeiro & Armando Martins
Advanced Topics in Algorithms - FCUP, University of Porto
"""

import random
import matplotlib.pyplot as plt
import pylab as pl
from matplotlib import collections as mc

class Vertex:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.incidentEdge = None

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

    # Mirrors the vertex by the axis given by point1 and point2
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
    
    # Returns the DCEL as a string
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
            output += "| f" + str(self.faces.index(face)+1) + " | e" + str(self.halfEdges.index(face.edge)+1) + " |\n"

        return output

    # Returns the edges of the polygon (outside edges of the DCEL)
    def get_outside_edges(self):

        outsideEdges = []

        for edge in self.halfEdges:
            if edge.isOutside:
                outsideEdges.append(edge)

        return outsideEdges

    # Returns the lines that represent every edge in the DCEL
    def get_lines(self):

        lines = []

        for edge in self.halfEdges:
            p1 = (edge.origin.x,edge.origin.y)
            p2 = (edge.next.origin.x,edge.next.origin.y)
            lines.append([p1,p2])

        return lines

    # Checks if the traingle given by the edge "edge" and the vertex "v1" intercects any edge in "edges"
    def new_point_intersect(self,ce,v1,edges):

        edges.remove(ce)

        for edge in edges:
            if edge.next.origin != ce.origin:
                if segments_intersect(edge.origin,edge.next.origin,ce.origin,v1):
                    return True
            if edge.origin != ce.next.origin:
                if segments_intersect(edge.origin,edge.next.origin,v1,ce.next.origin):
                    return True

        return False

    # builds a DCEL from a triangle (3 points)
    def build_triangular_dcel(self, points):

        edges = tree_vertices_to_ccw_edges(points)

        v1 = Vertex(edges[0][0][0],edges[0][0][1])
        v2 = Vertex(edges[1][0][0],edges[1][0][1])
        v3 = Vertex(edges[2][0][0],edges[2][0][1])

        he1 = HalfEdge(v1)
        he2 = HalfEdge(v2)
        he3 = HalfEdge(v3)

        v1.incidentEdge = he1
        v2.incidentEdge = he2
        v3.incidentEdge = he3

        he1.twin = HalfEdge(v2)
        he2.twin = HalfEdge(v3)
        he3.twin = HalfEdge(v1)
        
        he1.next = he2
        he1.prev = he3
        he1.twin.prev = he2.twin
        he1.twin.next = he3.twin
        he1.twin.twin = he1

        he2.next = he3
        he2.prev = he1
        he2.twin.prev = he3.twin
        he2.twin.next = he1.twin
        he2.twin.twin = he2

        he3.next = he1
        he3.prev = he2
        he3.twin.prev = he1.twin
        he3.twin.next = he2.twin
        he3.twin.twin = he3

        he1.twin.isOutside = True
        he2.twin.isOutside = True
        he3.twin.isOutside = True

        #outside face
        f1 = Face(he1.twin)

        #inside face
        f2 = Face(he1)

        he1.incidentFace = f2
        he2.incidentFace = f2
        he3.incidentFace = f2

        he1.twin.incidentFace = f1
        he2.twin.incidentFace = f1
        he3.twin.incidentFace = f1

        self.vertices.append(v1)
        self.vertices.append(v2)
        self.vertices.append(v3)

        self.halfEdges.append(he1)
        self.halfEdges.append(he2)
        self.halfEdges.append(he3)
        self.halfEdges.append(he1.twin)
        self.halfEdges.append(he2.twin)
        self.halfEdges.append(he3.twin)

        #outside face
        self.faces.append(f1)

        #inside face
        self.faces.append(f2)

    # Adds the triangle given by the edge "edge" and the vertex "(x,y)" to the DCEL
    def add_vertex(self,edge,x,y):
        
        #check if edge is edge of external face
        if self.faces[0].edge == edge:
            self.faces[0].edge = edge.next

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

        he1.twin = HalfEdge(v1)
        he2.twin = HalfEdge(edge.origin)

        he1.twin.prev = he2.twin
        he1.twin.next = edge.next
        he1.twin.isOutside = True
        he1.twin.incidentFace = edge.incidentFace
        he1.twin.twin = he1

        he2.twin.prev = edge.prev
        he2.twin.next = he1.twin
        he2.twin.isOutside = True
        he2.twin.incidentFace = edge.incidentFace
        he2.twin.twin = he2

        edge.next.prev = he1.twin
        edge.prev.next = he2.twin

        edge.next = he1
        edge.prev = he2
        edge.incidentFace = he1.incidentFace
        edge.isOutside = False

        self.vertices.append(v1)
        self.halfEdges.append(he1)
        self.halfEdges.append(he2)
        self.halfEdges.append(he1.twin)
        self.halfEdges.append(he2.twin)

        self.faces.append(he1.incidentFace)

    # Checks if the vertex "v1" is colinear with any edge in "edges"
    def collinear_with_polygon(self,v1,edges):

        for edge in edges:
            a = v1.x * (edge.origin.y - edge.next.origin.y) + edge.origin.x * (edge.next.origin.y - v1.y) + edge.next.origin.x * (v1.y - edge.origin.y)
            if a == 0:
                return True

        return False

#######
# This part of the code is inspired by
# https://stackoverflow.com/questions/2049582/how-to-determine-if-a-point-is-in-a-2d-triangle
# Last checked in 5/6/2021
#######
def sign (v1, v2, v3):
    return (v1.x - v3.x) * (v2.y - v3.y) - (v2.x - v3.x) * (v1.y - v3.y);

def insideTri(v1, v2, v3, pt):

    d1 = sign(pt, v1, v2);
    d2 = sign(pt, v2, v3);
    d3 = sign(pt, v3, v1);

    has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0);
    has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0);

    return not(has_neg and has_pos)

#######

#######
# This part of the code is inspired by geeksforgeeks
# https://www.geeksforgeeks.org/check-if-two-given-line-segments-intersect/
# Last checked in 5/6/2021
#######

def onSegment(p, q, r):
    if ( (q.x <= max(p.x, r.x)) and (q.x >= min(p.x, r.x)) and 
           (q.y <= max(p.y, r.y)) and (q.y >= min(p.y, r.y))):
        return True
    return False

def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/ 
    # for details of below formula. 
      
    val = (float(q.y - p.y) * (r.x - q.x)) - (float(q.x - p.x) * (r.y - q.y))
    if (val > 0):
        # Clockwise orientation
        return 1
    elif (val < 0):
        # Counterclockwise orientation
        return 2
    else:
        # Colinear orientation
        return 0

def segments_intersect(p1,q1,p2,q2):

    # Find the 4 orientations required for 
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
  
    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True
  
    # Special Cases
  
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True
  
    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True
  
    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True
  
    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True
  
    # If none of the cases
    return False

#######

# Orders 3 points in CCW order
def tree_vertices_to_ccw_edges(points):
    
    xsorted = sorted(points, key=lambda tup: tup[0])
    first = xsorted.pop(0)
    ysorted = sorted(xsorted, key=lambda tup: tup[1])
    second = ysorted.pop(0)
    third = ysorted.pop(0)
    return [(first,second),(second,third),(third,first)]

# Generates a new possible next point to create the next triangle to be glued to the polygon
def next_point(edges):

    edge = edges[random.randint(0,len(edges)-1)]
    v1 = Vertex(edge.origin.x,edge.origin.y)
    v2 = Vertex(edge.next.origin.x,edge.next.origin.y)

    #makes sure the point is not too close to the edge
    minDist = 2

    if v1.x == v2.x:
        if v1.y > v2.y: #is right edge
            v1.x += minDist
            v2.x += minDist
        else: #is left edge
            v1.x -= minDist
            v2.x -= minDist
    elif v1.y == v2.y:
        if v1.x > v2.x: #is bottom edge
            v1.y -= minDist
            v2.y -= minDist
        else: #is top edge
            v1.y += minDist
            v2.y += minDist
    elif v1.y > v2.y:
        if v1.x < v2.x: #top down right
            v1.x += minDist
            v2.x += minDist
        else: #top down left
            v1.x += minDist
            v2.x += minDist
    elif v1.y < v2.y:
        if v1.x < v2.x: #bottom top right
            v1.x -= minDist
            v2.x -= minDist
        else: #bottom top left
            v1.x -= minDist
            v2.x -= minDist

    m = Vertex((v1.x+v2.x)/2, (v1.y+v2.y)/2) # Mid point
    o = Vertex((v1.x-m.x)*3**0.5, (v1.y-m.y)*3**0.5)

    v3 = Vertex(m.x+o.y,m.y-o.x)
    v4 = Vertex(m.x-o.y,m.y+o.x)

    r1 = random.uniform(0,1)
    r2 = random.uniform(0,1)

    newv = Vertex(r1 * (v1.x-v3.x) + r2 * (v2.x-v3.x),r1 * (v1.y-v3.y) + r2 * (v2.y-v3.y))

    newv.x += v3.x
    newv.y += v3.y

    if insideTri(v1,v2,v4,newv):
        newv.mirror(v1,v2)

    newv.x = round(newv.x)
    newv.y = round(newv.y)
    
    return edge,newv

# Checks if the point's coordinates are between 0 and m
def is_inside_box(v1,m):

    if v1.x < 0 or v1.x > m or v1.y < 0 or v1.y > m:
        return False

    return True

# Generates the starting polygon based on the window size (m)
def starting_polygon(m):

    s = round(m/2)
    return [(s,s),(s+1,s),(s,s+1)]

def main():

    n = int(input("Nº of vertices: "))

    while n < 3:
        print("Polygon needs at least 3 vertices!!")
        n = int(input("Nº of vertices: "))

    m = int(input("Max value for vertices coordinates: "))

    triangle = starting_polygon(m)

    myDCEL = DCEL()
    myDCEL.build_triangular_dcel(triangle)

    for i in range(0,n-3):
        outsideEdges = myDCEL.get_outside_edges()
        for j in range(0,500):
                edge,vertex = next_point(outsideEdges)
                if not myDCEL.new_point_intersect(edge,vertex,outsideEdges):
                    if is_inside_box(vertex,m):
                        if not myDCEL.collinear_with_polygon(vertex,outsideEdges):
                            break
        if j==499:
            print("Could not create polygon with that many vertices in that space")
            return
        myDCEL.add_vertex(edge,vertex.x,vertex.y)

    print(myDCEL)

    # shows the DCEL in matplotlib
    lines = myDCEL.get_lines()
    lc = mc.LineCollection(lines)
    fig, ax = pl.subplots()
    ax.add_collection(lc)
    ax.autoscale()
    ax.margins(0.1)
    fig.canvas.manager.set_window_title("Polygon with " + str(n) + " vertices with coordinates between 0 and " + str(m))
    plt.show()

if __name__ == "__main__":
    main()