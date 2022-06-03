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

    def _transform(self, phi, dx, dy):
        e1, e2, e3 = ['{:1.2E}'.format(e) for e in (phi, dx, dy)]
        line = 'ROT-DEFI                       {:>9} {:>9} {:>9}          GLOB\n'
        self._lines[8] = line.format(e1, e2, e3)

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
        file.close()
