import math
import random
import sys
import time

import numpy as np
import OpenGL
from OpenGL.GL import *
import pygame
from pygame.locals import *

def createCircles(numCircles):
    circles = []
    minRadius = 5
    maxRadius = 20
    for i in range(numCircles):
        cx = random.random()*width
        cy = random.random()*height
        r = random.random()*(maxRadius - minRadius) + minRadius
        circles.append((cx, cy, r))
    return circles

def createShader(vsStr, fsStr):
    vs = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vs, vsStr)
    glCompileShader(vs)
    check = glGetShaderiv(vs, GL_COMPILE_STATUS)
    if not(check):
        raise RuntimeError(glGetShaderInfoLog(vs))

    fs = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fs, fsStr)
    glCompileShader(fs)
    check = glGetShaderiv(fs, GL_COMPILE_STATUS)
    if not(check):
        raise RuntimeError(glGetShaderInfoLog(fs))

    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)
    check = glGetProgramiv(program, GL_LINK_STATUS)
    if not(check):
        raise RuntimeError(glGetProgramInfoLog(program))

    return program

def updateBufferData(circles, vbo, tbo, ibo, xbo, vertices, texCoords, indices, instances, colors, instanceData, texture):
    iData = np.empty(shape=(len(circles), 24), dtype=np.float32)
    for i, circle in enumerate(circles):
        cx, cy, r = circle
        vertices[i] = [-r, -r, r, -r, -r, r, r, r]
        texCoords[i] = [-1, -1, 1, -1, -1, 1, 1, 1]
        indices[i] = np.array([0, 1, 2, 2, 3, 1], dtype=np.float32)+(4*i)
        instances[i] = [i]*4
        iData[i] = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, cx, cy, 0, 1] + list(colors[i]) + [r, 0, 0, 0]

    iData = iData.flatten()
    instanceData = instanceData.flatten()
    instanceData[0:len(iData)] = iData
    instanceData = np.reshape(instanceData, (512, 512, 4))
    glActiveTexture(GL_TEXTURE0)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA32F, 512, 512, 0, GL_RGBA, GL_FLOAT, instanceData)
    glBindTexture(GL_TEXTURE_2D, 0)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER, tbo)
    glBufferData(GL_ARRAY_BUFFER, texCoords.nbytes, texCoords, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER, xbo)
    glBufferData(GL_ARRAY_BUFFER, instances.nbytes, instances, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

if __name__ == "__main__":
    width = 500
    height = 500
    title = "Pseudo-Instancing Demo"
    pygame.init()
    screen = pygame.display.set_mode((width, height), DOUBLEBUF|OPENGL|HWSURFACE)

    vsStr = """#version 120
    attribute vec2 a_position;
    attribute vec2 a_texCoord;
    attribute int a_instance;
    uniform sampler2D u_texture;
    const int textureSize = 512;
    const int instanceSize = 24;
    varying vec4 v_color;
    varying float v_radius;
    varying vec2 v_texCoord;

    vec2 getIndex(int instanceNumber, int position)
    {
        int indexOneD = instanceNumber * instanceSize/4;
        float y = (indexOneD + position) / textureSize;
        float x = (indexOneD + position) - textureSize * y;
        return vec2(x/textureSize, y/textureSize);
    }

    void main()
    {
        vec4 rgba0 = texture2D(u_texture, getIndex(a_instance, 0));
        vec4 rgba1 = texture2D(u_texture, getIndex(a_instance, 1));
        vec4 rgba2 = texture2D(u_texture, getIndex(a_instance, 2));
        vec4 rgba3 = texture2D(u_texture, getIndex(a_instance, 3));
        vec4 rgba4 = texture2D(u_texture, getIndex(a_instance, 4));
        vec4 rgba5 = texture2D(u_texture, getIndex(a_instance, 5));
        mat4 transform = mat4(rgba0, rgba1, rgba2, rgba3);
        gl_Position = gl_ProjectionMatrix * transform * vec4(a_position, 0, 1);
        v_color = rgba4;
        v_radius = rgba5.r;
        v_texCoord = a_texCoord;
    }
    """

    fsStr = """#version 120
    varying vec4 v_color;
    varying float v_radius;
    varying vec2 v_texCoord;
    void main()
    {
        float d = v_radius - length(v_texCoord*vec2(v_radius, v_radius));
        float t = clamp(d, 0, 1);
        gl_FragColor = vec4(1, 1, 1, t) * v_color;
    }
    """

    numCircles = 500
    circles = createCircles(numCircles)
    shader = createShader(vsStr, fsStr)
    vbo, tbo, ibo, xbo = glGenBuffers(4)
    vertices = np.empty([numCircles, 8], dtype=np.float32)
    texCoords = np.empty([numCircles, 8], dtype=np.float32)
    indices = np.empty([numCircles, 6], dtype=np.int32)
    instances = np.empty([numCircles, 4], dtype=np.int32)

    colors = np.random.rand(numCircles, 4)
    instanceData = np.zeros(shape=(512, 512, 4), dtype=np.float32)
    texture = glGenTextures(1)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_NEAREST)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,GL_NEAREST)
    glBindTexture(GL_TEXTURE_2D, 0)

    glClearColor(1.0, 1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glOrtho(0, width, 0, height, -1, 1)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    while 1:
        start = time.time()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()

        updateBufferData(circles, vbo, tbo, ibo, xbo, vertices, texCoords, indices, instances, colors, instanceData, texture)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)

        a_position = glGetAttribLocation(shader, "a_position")
        a_texCoord = glGetAttribLocation(shader, "a_texCoord")
        a_instance = glGetAttribLocation(shader, "a_instance")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
        u_texture = glGetUniformLocation(shader, "u_texture")
        glUniform1i(u_texture, 0)

        glEnableVertexAttribArray(a_position)
        glEnableVertexAttribArray(a_texCoord)
        glEnableVertexAttribArray(a_instance)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glVertexAttribPointer(a_position, 2, GL_FLOAT, False, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, tbo)
        glVertexAttribPointer(a_texCoord, 2, GL_FLOAT, False, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, xbo)
        glVertexAttribPointer(a_instance, 1, GL_FLOAT, False, 0, None)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ibo)
        glDrawElements(GL_TRIANGLES, 6*numCircles, GL_UNSIGNED_INT, None)
        glDisableVertexAttribArray(a_position)
        glDisableVertexAttribArray(a_texCoord)
        glDisableVertexAttribArray(a_instance)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)

        pygame.display.flip()
        end = time.time()
        fps = int(round(1/(end - start)))
        pygame.display.set_caption(title + ": " + str(fps))
