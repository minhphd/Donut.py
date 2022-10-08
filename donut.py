import numpy as np
from math import sin, cos, sqrt
import curses

def draw_donut(R1, R2, init_r):
    dic = {}
    theta_arr = np.arange(0, 2*np.pi + 0.1, 0.1).tolist()
    circle = []
    surface_normal = []
    i = 0
    # draw the initial circle
    for theta in theta_arr:
        r0 = [1,0,0]
        norm_r = vector_rotate(r0, theta, axis_z)
        r = init_r + axis_x * (R1 + R2) + norm_r * R2
        circle.append(r)
        surface_normal.append(norm_r)

    # rotate the circle around an axis to create the torus
    for idx, point in enumerate(circle):
        for theta in theta_arr:
            n0 = surface_normal[idx]
            r = init_r + vector_rotate(-point + init_r, theta, axis_y)
            n = vector_rotate(n0, theta, axis_y)
            dic[i] = {"coord": r, "n": n}
            i += 1

    return dic, i


def rotation_matrix(axis, theta):
    axis = np.asarray(axis)
    axis = axis / sqrt(np.dot(axis, axis))
    a = cos(theta / 2.0)
    b, c, d = -axis * sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])

def vector_rotate(vec, angle, axis):
    M0 = rotation_matrix(axis, angle)
    return np.dot(M0, vec)

if __name__ == "__main__":
    rows, cols = (40, 80)
    scale = ".,-~:;=!*#$@"
    R1, R2 = (7,7)
    axis_x, axis_y, axis_z = (np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1]))
    init_r = np.array([cols/2,0,cols/2])
    light = np.array([0,-1,1])
    dic, i = draw_donut(R1, R2, init_r)
    for idx in range(i):
        r0 = dic[idx]["coord"] - init_r
        n0 = dic[idx]["n"]
        r = vector_rotate(r0, -np.pi/3, axis_x) + init_r
        n = vector_rotate(n0, -np.pi/3, axis_x)
        dic[idx] = {"coord": r, "n": n}

    def draw(terminal):
        terminal.clear()
        terminal.refresh()
        theta = 0
        k = 0
        terminal.nodelay(True)
        while k != ord('q'):
            points = []
            shade = []
            k = terminal.getch()
            for idx in range(i):
                r0 = dic[idx]["coord"] - init_r
                n0 = dic[idx]["n"]
                r = vector_rotate(vector_rotate(r0, theta, axis_x), theta, axis_z) + init_r
                n = vector_rotate(vector_rotate(n0, theta, axis_x), theta, axis_z)
                points.append(r.tolist())
                shade.append(np.dot(n, light))

            terminal.clear()
            curses.resize_term(rows, cols)
            terminal.border(0)
            shade = [x for _, x in sorted(zip(points, shade), key=lambda pair: pair[0][1])]
            points.sort(key=lambda x: x[1])
            min_illu, max_illu  = min(shade), max(shade)
            for idx in range(i):
                x, y, z = points[idx]
                illu = (shade[idx] - min_illu)*11/(max_illu - min_illu)
                string = scale[round(illu)]
                terminal.addstr(round(z * rows/cols), round(x), string, curses.A_BOLD)
            theta += 0.15
            terminal.move(0,0)
            terminal.refresh()


    curses.wrapper(draw)