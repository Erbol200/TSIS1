class Ball:
    def __init__(self,x,y,radius):
        self.x=x
        self.y=y
        self.radius=radius
        self.speed=5
    
    def move(self,dx,dy):
        self.x+=dx
        self.y+=dy
            