import math
class planet:
    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass
        self.orbit = []
        self.x_vel = 0
        self.y_vel = 0
    def attraction(self, other):
        G = 6*(10**-11)
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        force = ((G*self.mass*other.mass)/distance**2)
        theta = math.atan(dx, dy)
        fx = math.cos(theta) * force
        fy = math.sin(theta) * force
