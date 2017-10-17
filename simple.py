from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import math 
def drawFunc():
    glClear(GL_COLOR_BUFFER_BIT)
    glRotatef(1, 0, 1, 0)
    glutWireTeapot(0.5)
    x = 10
    y = 10
    radius = 10
    smoothness = 10
    circle(x, y, radius, smoothness)
    glFlush()

def circle(x, y, radius, smoothness):
    ''' Draw a circle.
    Parameters - x - x co-ordinate
                y - y co-ordinate
                radius - radius of the circle
                smoothness - number of triangles to use'''

    glBegin(GL_TRIANGLE_FAN)
    glColor3f(1.0, 0.0, 0.0)
    for i in range(0, smoothness):    
        angle = i * math.pi * 2.0 / smoothness
        glVertex2f(x + radius * math.cos(angle), y + radius * math.sin(angle))
    glEnd() 

glutInit()
glutInitDisplayMode(GLUT_SINGLE | GLUT_RGBA)
glutInitWindowSize(400, 400)
glutCreateWindow("First")
glutDisplayFunc(drawFunc)
glutIdleFunc(drawFunc)
glutMainLoop()
