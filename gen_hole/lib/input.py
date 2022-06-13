from errno import EL3RST
import numpy as np


def rot(x, y, theta):
    cost = np.cos(theta)
    sint = np.sin(theta)

    xnew = x * cost - y * sint
    ynew = x * sint + y * cost

    return xnew, ynew


class Input:
    def __init__(self, file_name):
        file = open(file_name)
        self._lines = file.readlines()
        file.close()

        self._phi = 0
        self._dx = 0
        self._dy = 0

        self._r = 0
        self._h = 0

    def transRandom(self):

        while True:
            phi_rand = np.random.random() * np.pi

            dx_rand = np.random.random() * 16 - 8
            dy_rand = np.random.random() * 16 - 8

            x1 = abs(dx_rand) + 5
            y1 = abs(dy_rand) + 15
            x1, y1 = rot(x1, y1, phi_rand)

            x2 = abs(dx_rand) - 5
            y2 = abs(dy_rand) + 15
            x2, y2 = rot(x2, y2, phi_rand)

            x3 = abs(dx_rand) + 5
            y3 = abs(dy_rand) - 15
            x3, y3 = rot(x3, y3, phi_rand)

            x4 = abs(dx_rand) - 5
            y4 = abs(dy_rand) - 15
            x4, y4 = rot(x4, y4, phi_rand)

            xmax = max(abs(x1), abs(x2), abs(x3), abs(x4))
            ymax = max(abs(y1), abs(y2), abs(y3), abs(y4))

            if xmax < 20 and ymax < 20:
                break

        phi = phi_rand * 180 / np.pi
        dx = dx_rand
        dy = dy_rand
        
        self._transform(phi, dx, dy)
        self._phi = phi
        self._dx = dx
        self._dy = dy

    def defectRandom(self):
        xmargin = 4.3
        ymargin = 13
        zmargin = 0.4

        while True:
            r = np.random.normal() + 0.6
            if 0.4 < r < 1.2:
                break
        xmargin -= r
        ymargin -= r

        while True:
            h = np.random.normal() + 0.25
            if 0.1 < h < 0.4:
                break
        zmargin = h / 2

        x = (2 * np.random.random() - 1) * xmargin
        y = (2 * np.random.random() - 1) * ymargin
        z = (zmargin + 0.4) * np.random.random() - 0.4

        self._hole(x, y, z, h, r)
        self._r = r
        self._h = h

    def _transform(self, phi, dx, dy):
        e1, e2, e3 = ['{:1.2E}'.format(e) for e in (phi, dx, dy)]
        line = 'ROT-DEFI                       {:>9} {:>9} {:>9}          GLOB\n'
        self._lines[8] = line.format(e1, e2, e3)

    def _hole(self, x, y, z, h, r):
        e1, e2, e3, e4, e5 = ['{:1.2E}'.format(e) for e in (x, y, z, h, r)]
        line = 'RCC hole       {} {} {} 0.0 0.0 {} {}\n'
        self._lines[18] = line.format(e1, e2, e3, e4, e5)

    def write(self, file_name):
        file = open(file_name, mode="w")
        for line in self._lines:
            file.write(line)
        file.close()

    def writeInfo(self, file_name):
        file = open(file_name, mode="w")
        file.write("*** transform info ***\n")
        file.write("phi = {:.5E}\n".format(self._phi))
        file.write("dx  = {:.5E}\n".format(self._dx))
        file.write("dy  = {:.5E}\n".format(self._dy))
        file.write("*** defect info ***\n")
        file.write("r  =  {:.5E}\n".format(self._r))
        file.write("h  =  {:.5E}\n".format(self._h))
        file.close()
