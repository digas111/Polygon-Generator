class Vertex:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


def bambora(v):

    v.x = 5
    v.y = 5


v1 = Vertex(1,3)

print(v1)
bambora(v1)
print(v1)
