# just reference, don't use yet
import numpy as np
import math


class Matrix:

    @staticmethod
    def make_identity():
        return np.array(
            [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, 1]]
        ).astype(float)
    
    @staticmethod
    def perspective(fov, aspect, near, far):
        n, f = near, far
        t = np.tan((fov * np.pi / 180) / 2) * near
        b = - t
        r = t * aspect
        l = b * aspect
        assert abs(n - f) > 0
        return np.array((
            ((2*n)/(r-l),           0,           0,  0),
            (          0, (2*n)/(t-b),           0,  0),
            ((r+l)/(r-l), (t+b)/(t-b), (f+n)/(n-f), -1),
            (          0,           0, 2*f*n/(n-f),  0)))

    @staticmethod
    def normalized(v):
        norm = np.linalg.norm(v)
        return v / norm if norm > 0 else v
    
    @staticmethod
    def look_at(eye, target):
        up = np.array((0,1,0))
        zax = Matrix.normalized(eye - target)
        xax = Matrix.normalized(np.cross(up, zax))
        yax = np.cross(zax, xax)
        x = - xax.dot(eye)
        y = - yax.dot(eye)
        z = - zax.dot(eye)
        return np.array(((xax[0], yax[0], zax[0], 0),
                         (xax[1], yax[1], zax[1], 0),
                         (xax[2], yax[2], zax[2], 0),
                         (     x,      y,      z, 1)))

    @staticmethod
    def make_perspective(angle_of_view=60, aspect_ratio=1, near=0.1, far=1000):
        a = angle_of_view * math.pi / 180.0
        d = 1.0 / math.tan(a / 2)
        b = (far + near) / (near - far)
        c = 2 * far * near / (near - far)
        return np.array(
            [[d / aspect_ratio, 0, 0, 0],
             [0, d, 0, 0],
             [0, 0, b, c],
             [0, 0, -1, 0]]
        ).astype(float)