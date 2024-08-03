import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

radius = 1.5
lat_bands, long_bands = 50, 50
ring_params = {'radius': radius, 'thickness': 0.5, 'segments': 100}
additional_ring_params = {'radius': 3.0, 'thickness': 0.2, 'segments': 100}
horizontal_ring_params = {'radius': 2.2, 'thickness': 0.2, 'segments': 100}
num_stars, star_distance, star_size = 150, 100, 1

# creates the vertices, normals, and indices for a 3D sphere.
def create_sphere():
    vertices, normals, indices = [], [], []
    
    # iterates over latitude and longitude bands to calculate normals and vertex positions
    for lat in range(lat_bands + 1):
        theta = lat * np.pi / lat_bands
        sin_theta, cos_theta = np.sin(theta), np.cos(theta)
        for long in range(long_bands + 1):
            phi = long * 2 * np.pi / long_bands
            sin_phi, cos_phi = np.sin(phi), np.cos(phi)
            x, y, z = cos_phi * sin_theta, cos_theta, sin_phi * sin_theta
            normals.append((x, y, z))
            vertices.append((radius * x, radius * y, radius * z))
    for lat in range(lat_bands):
        for long in range(long_bands):
            first, second = (lat * (long_bands + 1)) + long, (lat * (long_bands + 1)) + long + long_bands + 1
            indices.extend([first, second, first + 1, second, second + 1, first + 1])
    return np.array(vertices), np.array(normals), np.array(indices)

# creates the vertices and indices for vertical or horizontal rings
def create_ring(radius, thickness, segments, horizontal=False):
    vertices, indices = [], []
    for i in range(segments + 1):
        theta = i * 2 * np.pi / segments
        x, y, z = (radius * np.cos(theta), radius * np.sin(theta), 0) if horizontal else (radius * np.cos(theta), 0, radius * np.sin(theta))
        vertices.extend([(x, y, z - thickness / 2), (x, y, z + thickness / 2)])
    for i in range(segments):
        next_i = (i + 1) % segments
        indices.extend([i * 2, next_i * 2, next_i * 2 + 1, i * 2, next_i * 2 + 1, i * 2 + 1])
    return np.array(vertices), np.array(indices)

# draws a 3D object of a certain color and width using calculated vertices and indices
def draw_object(vertices, indices, color, line_width=2.0, use_normal=False):
    glEnableClientState(GL_VERTEX_ARRAY)
    glVertexPointerf(vertices)
    glColor3f(*color)
    if use_normal:
        glEnableClientState(GL_NORMAL_ARRAY)
        glNormalPointerf(vertices)
        glDisable(GL_LIGHTING)
    if line_width:
        glLineWidth(line_width)
    glDrawElements(GL_TRIANGLES, len(indices), GL_UNSIGNED_INT, indices)
    glDisableClientState(GL_VERTEX_ARRAY)
    if use_normal:
        glDisableClientState(GL_NORMAL_ARRAY)

# creates a list of random star positions
def generate_stars():
    stars = []
    for _ in range(num_stars):
        theta, phi = np.random.uniform(0, np.pi * 2), np.random.uniform(0, np.pi)
        x, y, z = np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)
        stars.append((star_distance * x, star_distance * y, star_distance * z))
    return stars

# draws stars in the 3D space based on random list
def draw_stars(stars):
    glDisable(GL_LIGHTING)
    glColor3f(1.0, 1.0, 1.0)
    glPointSize(star_size)
    glBegin(GL_POINTS)
    for star in stars:
        glVertex3fv(star)
    glEnd()

# displays an interactable black hole in space surrounded by stars
def main():
  
    # sets up GUI and configures perspective
    pygame.init()
    display = (1200, 675)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Black Hole Interactive")
    gluPerspective(45, (display[0] / display[1]), 0.1, 100.0)
    glTranslatef(0.0, 0.0, -10)
    glEnable(GL_DEPTH_TEST)

    # creating geometric objects
    sphere_vertices, sphere_normals, sphere_indices = create_sphere()
    ring_vertices, ring_indices = create_ring(**ring_params)
    additional_ring_vertices, additional_ring_indices = create_ring(**additional_ring_params)
    horizontal_ring_vertices, horizontal_ring_indices = create_ring(**horizontal_ring_params, horizontal=True)
    stars = generate_stars()

    # setup for rotational movement
    rot_x, rot_y = 0, 0
    rot_x_velocity, rot_y_velocity = 0, 0
    mouse_down = False
    last_mouse_pos = (0, 0)
    camera_rotation_speed = 0.02
    deceleration = 0.95

    # event handling
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_down = True
                    last_mouse_pos = pygame.mouse.get_pos()
            elif event.type == MOUSEBUTTONUP:
                if event.button == 1:
                    mouse_down = False
            elif event.type == MOUSEMOTION and mouse_down:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                dx, dy = mouse_x - last_mouse_pos[0], mouse_y - last_mouse_pos[1]
                rot_x_velocity += dy / 100
                rot_y_velocity += dx / 100
                last_mouse_pos = (mouse_x, mouse_y)

        # change rotation based on user input
        if not mouse_down:
            rot_x_velocity *= deceleration
            rot_y_velocity *= deceleration

        rot_x += rot_x_velocity
        rot_y += rot_y_velocity

        if not mouse_down:
            rot_x += camera_rotation_speed

        # clear screen and apply transformations
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glPushMatrix()
        glRotatef(rot_x, 1, 0, 0)
        glRotatef(rot_y, 0, 1, 0)

        # draw shapes in 3D space
        draw_stars(stars)
        draw_object(sphere_vertices, sphere_indices, (0.06, 0.06, 0.06), use_normal=True)
        draw_object(ring_vertices, ring_indices, (1.0, 0.5, 0.0))
        draw_object(additional_ring_vertices, additional_ring_indices, (1.0, 0.5, 0.0))
        draw_object(horizontal_ring_vertices, horizontal_ring_indices, (1.0, 0.5, 0.0))

        glPopMatrix()
        pygame.display.flip()
        pygame.time.wait(10)

if __name__ == "__main__":
    main()
