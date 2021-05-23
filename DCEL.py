#!/usr/bin/env python
#Copyright 2008, Angel Yanguas-Gil

__all__ = ['Dcel', 'Vertex', 'Hedge', 'Face']

from xygraph import Xygraph

import math as m

class DcelError(Exception): pass

class Vertex:
    """Minimal implementation of a vertex of a 2D dcel"""

    def __init__(self, px, py):
        self.x = px
        self.y = py
        self.hedgelist = []

    def sortincident(self):
        self.hedgelist.sort(hsort, reverse=True)


class Hedge:
    """Minimal implementation of a half-edge of a 2D dcel"""

    def __init__(self,v1,v2):
        #The origin is defined as the vertex it points to
        self.origin = v2
        self.twin = None
        self.face = None
        self.nexthedge = None
        self.angle = hangle(v2.x-v1.x, v2.y-v1.y)
        self.prevhedge = None
        self.length = m.sqrt((v2.x-v1.x)**2 + (v2.y-v1.y)**2)


class Face:
    """Implements a face of a 2D dcel"""

    def __init__(self):
        self.wedge = None
        self.data = None
        self.external = None

    def area(self):
        h = self.wedge
        a = 0
        while(not h.nexthedge is self.wedge):
            p1 = h.origin
            p2 = h.nexthedge.origin
            a += p1.x*p2.y - p2.x*p1.y
            h = h.nexthedge

        p1 = h.origin
        p2 = self.wedge.origin
        a = (a + p1.x*p2.y - p2.x*p1.y)/2
        return a

    def perimeter(self):
        h = self.wedge
        p = 0
        while (not h.nexthedge is self.wedge):
            p += h.length
            h = h.nexthedge
        return p

    def vertexlist(self):
        h = self.wedge
        pl = [h.origin]
        while(not h.nexthedge is self.wedge):
            h = h.nexthedge
            pl.append(h.origin)
        return pl

    def isinside(self, p):
        """Determines whether a point is inside a face"""

        h = self.wedge
        inside = False
        if lefton(h, p):
            while(not h.nexthedge is self.wedge):
                h = h.nexthedge
                if not lefton(h, p):
                    return False
            return True
        else:
            return False


class Dcel(Xygraph):
    """
    Implements a doubly-connected edge list
    """

    def __init__(self, vl=[], el=[], clip=None):
        Xygraph.__init__(self, vl, el)
        self.vertices = []
        self.hedges = []
        self.faces = []
        if vl != []:
            if clip is not None:
                self.clip(clip)
            self.build_dcel()


    def build_dcel(self):
        """
        Creates the dcel from the list of vertices and edges
        """

#Step 1: vertex list creation
        for v in self.vl:
            self.vertices.append(Vertex(v[0], v[1]))

#Step 2: hedge list creation. Assignment of twins and
#vertices
        for e in self.el:
            if e[0] >= 0 and e[1] >= 0:
                h1 = Hedge(self.vertices[e[0]], self.vertices[e[1]])
                h2 = Hedge(self.vertices[e[1]], self.vertices[e[0]])
                h1.twin = h2
                h2.twin = h1
                self.vertices[e[1]].hedgelist.append(h1)
                self.vertices[e[0]].hedgelist.append(h2)
                self.hedges.append(h2)
                self.hedges.append(h1)

        #Step 3: Identification of next and prev hedges
        for v in self.vertices:
            v.sortincident()
            l = len(v.hedgelist)
            if l < 2:
                raise DcelError(
                    "Badly formed dcel: less than two hedges in vertex")
            else:
                for i in range(l-1):
                    v.hedgelist[i].nexthedge = v.hedgelist[i+1].twin
                    v.hedgelist[i+1].prevhedge = v.hedgelist[i]
                v.hedgelist[l-1].nexthedge = v.hedgelist[0].twin
                v.hedgelist[0].prevhedge = v.hedgelist[l-1]

        #Step 4: Face assignment
        provlist = self.hedges[:]
        nf = 0
        nh = len(self.hedges)

        while nh > 0:
            h = provlist.pop()
            nh -= 1
            #We check if the hedge already points to a face
            if h.face == None:
                f = Face()
                nf += 1
                #We link the hedge to the new face
                f.wedge = h
                f.wedge.face = f
                #And we traverse the boundary of the new face
                while (not h.nexthedge is f.wedge):
                    h = h.nexthedge
                    h.face = f
                self.faces.append(f)
        #And finally we have to determine the external face
        for f in self.faces:
            f.external = f.area() < 0


    def findpoints(self, pl, onetoone=False):
        """Given a list of points pl, returns a list of
        with the corresponding face each point belongs to and
        None if it is outside the map.
        """

        ans = []
        if onetoone:
            fl = self.faces[:]
            for p in pl:
                found = False
                for f in fl:
                    if f.external:
                        continue
                    if f.isinside(p):
                        fl.remove(f)
                        found = True
                        ans.append(f)
                        break
                if not found:
                    ans.append(None)

        else:
            for p in pl:
                found = False
                for f in self.faces:
                    if f.external:
                        continue
                    if f.isinside(p):
                        found = True
                        ans.append(f)
                        break
                if not found:
                    ans.append(None)

        return ans

    def load(self, filename):
        """reads a dcel from file using xygraph file format"""
        a = Xygraph.load(self, filename)
        self.build_dcel()
        return a

    def areas(self):
        return [f.area() for f in self.faces if not f.external]

    def perimeters(self):
        return [f.perimeter() for f in self.faces if not f.external]

    def nfaces(self):
        return len(self.faces)

    def nvertices(self):
        return len(self.vertices)

    def nedges(self):
        return len(self.hedges)/2

#Misc. functions


def hsort(h1, h2):
    """Sorts two half edges counterclockwise"""

    if h1.angle < h2.angle:
        return -1
    elif h1.angle > h2.angle:
        return 1
    else:
        return 0


def checkhedges(hl):
    """Consistency check of a hedge list: nexthedge, prevhedge"""

    for h in hl:
        if h.nexthedge not in hl or h.prevhedge not in hl:
            raise DcelError("Problems with an orphan hedge...")


def area2(hedge, point):
    """Determines the area of the triangle formed by a hedge and
    an external point"""

    pa = hedge.twin.origin
    pb=hedge.origin
    pc=point
    return (pb.x - pa.x)*(pc[1] - pa.y) - (pc[0] - pa.x)*(pb.y - pa.y)


def lefton(hedge, point):
    """Determines if a point is to the left of a hedge"""

    return area2(hedge, point) >= 0


def hangle(dx,dy):
    """Determines the angle with respect to the x axis of a segment
    of coordinates dx and dy
    """

    l = m.sqrt(dx*dx + dy*dy)
    if dy > 0:
        return m.acos(dx/l)
    else:
        return 2*m.pi - m.acos(dx/l)


if __name__=='__main__':
    import sys
    d = Dcel()
    d.load(sys.argv[1])
    for a,p in zip(d.areas(), d.perimeters()):
        print a,p


#
#
#

import math as m

# Utils
def findHAngle(dx, dy):
  """Determines the angle with respect to the x axis of a segment
  of coordinates dx and dy
  """
  l = m.sqrt(dx*dx + dy*dy)
  if dy > 0:
    return m.acos(dx/l)
  else:
    return 2*m.pi - m.acos(dx/l)


class Vertex:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.hedges = []  # list of halfedges whose tail is this vertex

  def __eq__(self, other):
    if isinstance(other, Vertex):
      return self.x == other.x and self.y == other.y
    return NotImplemented

  def sortHedges(self):
    self.hedges.sort(key=lambda a: a.angle, reverse=True)

  def __repr__(self):
    return "({0},{1})".format(self.x, self.y)


class Hedge:
  # v1 -> v2
  def __init__(self, v1, v2):
    self.prev = None
    self.twin = None
    self.next = None
    self.tail = v1
    self.face = None
    self.angle = findHAngle(v2.x-v1.x, v2.y-v1.y)

  def __eq__(self, other):
    return self.tail == other.tail and \
        self.next.tail == other.next.tail

  def __repr__(self):
    if self.next is not None:
      return "({0},{1})->({2},{3})".format(self.tail.x, self.tail.y,
                                           self.next.tail.x,
                                           self.next.tail.y)
    else:
      return "({0},{1})->()".format(self.tail.x, self.tail.y)


class Face:
  def __init__(self):
    self.halfEdge = None
    self.name = None


class DCEL:
  def __init__(self):
    self.vertices = []
    self.hedges = []
    self.faces = []

  # Returns vertex object given x and y
  def findVertex(self, x, y):
    for v in self.vertices:
      if v.x == x and v.y == y:
        return v
    return None

  # Returns Halfedge whole vertices are v1 and v2
  # v1 and v2 are tuples
  def findHalfEdge(self, v1, v2):
    for halfEdge in self.hedges:
      nextEdge = halfEdge.next
      if (halfEdge.tail.x == v1[0] and halfEdge.tail.y == v1[1]) and (nextEdge.tail.x == v2[0] and nextEdge.tail.y == v2[1]):
        return halfEdge

    return None

  def build_dcel(self, points, segments):

    #  For each point create a vertex and add it to vertices
    for point in points:
      self.vertices.append(Vertex(point[0], point[1]))

    # For each input segment, create to hedges and assign their
    # tail vertices and twins

    # Structures of segment is [(0, 5), (2, 5)]
    for segment in segments:
      startVertex = segment[0]
      endVertex = segment[1]

      v1 = self.findVertex(startVertex[0], startVertex[1])
      v2 = self.findVertex(endVertex[0], endVertex[1])

      h1 = Hedge(v1, v2)
      h2 = Hedge(v2, v1)

      h1.twin = h2
      h2.twin = h1

      v1.hedges.append(h1)
      v2.hedges.append(h2)

      self.hedges.append(h1)
      self.hedges.append(h2)

    # For each endpoint, sort the half-edges whose
    # tail vertex is that endpoint in clockwise order.

    for vertex in self.vertices:
      vertex.sortHedges()

      noOfHalfEdges = len(vertex.hedges)

      if noOfHalfEdges < 2:
        return Exception("Invalid DCEL. There should be at least two half edges for a vertex")

      # For every pair of half-edges e1, e2 in clockwise order,
      # assign e1->twin->next = e2 and e2->prev = e1->twin.
      for i in range(noOfHalfEdges - 1):
        e1 = vertex.hedges[i]
        e2 = vertex.hedges[i+1]

        e1.twin.next = e2
        e2.prev = e1.twin

      # for the last and first halfedges pair
      e1 = vertex.hedges[noOfHalfEdges - 1]
      e2 = vertex.hedges[0]

      e1.twin.next = e2
      e2.prev = e1.twin

    # For every cycle, allocate and assign a face structure.
    faceCount = 0
    for halfEdge in self.hedges:

      if halfEdge.face == None:
        print('here')
        faceCount += 1

        f = Face()
        f.name = "f" + str(faceCount)

        f.halfEdge = halfEdge
        halfEdge.face = f

        h = halfEdge
        while (not h.next == halfEdge):
          h.face = f
          h = h.next
        h.face = f

        self.faces.append(f)

  # Given a half, find all the regions
  # The format of segment is [(0, 5), (2, 5)]

  def findRegionGivenSegment(self, segment):
    # We need to find the half edge whose vertices
    # are that of the passed segment
    v1 = segment[0]
    v2 = segment[1]
    startEdge = self.findHalfEdge(v1, v2)

    h = startEdge
    while (not h.next == startEdge):
      print(h, end="--->")
      h = h.next
    print(h, '--->', startEdge)


def main():
  points = [(0, 5), (2, 5), (3, 0), (0, 0)]

  segments = [
      [(0, 5), (2, 5)],
      [(2, 5), (3, 0)],
      [(3, 0), (0, 0)],
      [(0, 0), (0, 5)],
      [(0, 5), (3, 0)],
  ]

  myDCEL = DCEL()
  myDCEL.build_dcel(points, segments)

  myDCEL.findRegionGivenSegment([(3, 0), (0, 5)])


main()