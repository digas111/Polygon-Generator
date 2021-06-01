#top down rigth
# j=0
# for i in range(0,5,3):
#     j+=1
#     for x in range(3+i,3+i+3):
#         for y in range(2+j,2+j+3):
#             print("(" + str(x) + "," + str(y) + ")")




#bottom top left

# p1 = Vertex(6,6)
# p2 = Vertex(2,7)

# maxDist = 5
# declive = int(abs(p1.x-p2.x) / abs(p1.y-p2.y))

# print("Declive = " + str(declive))


# j=0
# for i in range(0,maxDist,declive):
#     j+=1
#     for x in range(p1.x-j,p1.x-j-declive,-1):
#         for y in range(p1.y-i,p1.y-i-declive,-1):
#             print("(" + str(x) + "," + str(y) + ")")


#top down left

# p1 = Vertex(8,12)
# p2 = Vertex(3,3)

# maxDist = 5
# declive = abs(p1.y-p2.y)/abs(p1.x-p2.x)

# print("Declive = " + str(declive))

# j=0
# for i in range(0,maxDist,declive):
#     j+=1
#     for x in range(p2.x+j,p2.x+j+declive):
#         for y in range(p2.y-i,p1.y-i-declive,-1):
#             print("(" + str(x) + "," + str(y) + ")")


import random
import matplotlib.pyplot as plt

class Vertex:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"

################
#função que calcula o reflexo ao point sobre a reta definida por point1 e point2
    def mirror(self, point1, point2):
        m = (point2.y - point1.y) / (point2.x - point1.x)
        c = (point2.x * point1.y - point1.x * point2.y) / (point2.x - point1.x)

        d = (self.x + (self.y - c) * m) / (1 + m * m)

        self.x = 2 * d - self.x
        self.y = 2 * d * m - self.y + 2 * c

# insideTri uses the barycentric coordinate system to find if point4 is inside the triangle formed by point1,2,3
def insideTri(point1, point2, point3, point4):

    denominator = ((point2.y-point3.y)*(point1.x-point3.x) + (point3.x-point2.x) * (point1.y - point3.y))
    a = ((point2.y - point3.y) * (point4.x - point3.x) + (point3.x-point2.x) * (point4.y-point3.y)) / denominator
    b = ((point3.y-point1.y) * (point4.x - point3.x) + (point1.x - point3.x) * (point4.y - point3.y)) / denominator
    c = 1 - a - b 
    return 0 <= a and a <= 1 and 0 <= b and b <= 1 and 0 <= c and c <= 1

class Triangle:

    def __init__(self,v1,v2,v3):
        self.v1 = v1
        self.v2 = v2
        self.v3 = v3

    def get_xy(self):

        x = [self.v1.x,self.v2.x,self.v3.x,self.v1.x]
        y = [self.v1.y,self.v2.y,self.v3.y,self.v1.y]

        return x,y

v1 = Vertex(3,8)
v2 = Vertex(6,1)

minDist = 2

v1.x += minDist
v2.x += minDist


m = Vertex((v1.x+v2.x)/2, (v1.y+v2.y)/2) # Mid point
o = Vertex((v1.x-m.x)*3**0.5, (v1.y-m.y)*3**0.5)

v3 = Vertex(m.x+o.y,m.y-o.x)
v4 = Vertex(m.x-o.y,m.y+o.x)

print(v3)
print(v4)


t1 = Triangle(v1,v2,v3)
t2 = Triangle(v1,v2,v4)

polyX,polyY = t1.get_xy()

polyX2,polyY2 = t2.get_xy()

polyX += polyX2
polyY += polyY2

xs = []
ys = []

for i in range(0,100):

    r1 = random.uniform(0,1)
    r2 = random.uniform(0,1)

    newv = Vertex(r1 * (v1.x-v3.x) + r2 * (v2.x-v3.x),r1 * (v1.y-v3.y) + r2 * (v2.y-v3.y))

    newv.x += v3.x
    newv.y += v3.y

    if not insideTri(v1,v2,v3,newv):
        print("Not inside daddy")
        print("old: " + str(newv))
        newv.mirror(v1,v2)
        print("new: " + str(newv))

    xs.append(newv.x)
    ys.append(newv.y)

    #print("(" + str(x) + "," + str(y) + ")")

plt.plot(polyX,polyY)
plt.scatter(xs,ys)
plt.show()
