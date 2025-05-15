import constants as c
import numpy as np
from graphical_objects.ponto3d import Ponto3D
from graphical_objects.objeto3d import Object3D
from typing import cast

class Renderer:
    def __init__(self, viewport, application):
        self._3dperspective = c.PERSPECTIVE_PROJECTION
        self._viewport = viewport
        self._application = application

        self._projection_matrix = None

        self._focal_distance = 2000

        self._cop = Ponto3D(0, 0, 0)
        self.vup = Vector(0, 1, 0)
        self.normal = Vector(0, 0, -1)
        self.angles = Vector(0, 0, 0)

    def recompute(self):

        print("Starting recompute...")

        cop_translation = self.translation_matrix(-self._cop.x, -self._cop.y, -self._cop.z)

        print(f"Angles: {self.angles}")
        print("Angles in degrees:", np.degrees(self.angles.x), np.degrees(self.angles.y), np.degrees(self.angles.z))
        
        rotate_x = Ponto3D.rotate_x_matrix(-self.angles.x)
        rotate_y = Ponto3D.rotate_y_matrix(-self.angles.y)
        rotate_z = Ponto3D.rotate_z_matrix(-self.angles.z)
        
        aligned = rotate_z @ rotate_y @ rotate_x

        perspective = self.perspective_matrix(self._focal_distance)

        print(f"Aligned Matrix: \n{aligned}")

        print(f"Translation Matrix: \n{cop_translation}")

        self._projection_matrix = perspective @ (aligned @ cop_translation)

        print(f"Perspective Matrix: \n{self.perspective_matrix(self._focal_distance)}")
        print(f"Projection Matrix: \n{self._projection_matrix}")

    def rotate(self, angle, axis):

        vup = Ponto3D(self.vup.x, self.vup.y, self.vup.z).to_homogeneous()
        normal = Ponto3D(self.normal.x, self.normal.y, self.normal.z).to_homogeneous()

        print(f"VUP before rotation: {vup}")
        print(f"Normal before rotation: {normal}")

        print(f"Angle: {angle} degrees")
        print(f"Axis: {axis}")

        radians = np.radians(angle)

        if axis == "PITCH":
            rotation_matrix = Ponto3D.rotate_x_matrix(radians)
            self.angles.x = (self.angles.x + radians) % (2*np.pi)

        elif axis == "YAW":
            rotation_matrix = Ponto3D.rotate_y_matrix(radians)
            self.angles.y = (self.angles.y + radians) % (2*np.pi)
        
        elif axis == "ROLL":
            rotation_matrix = Ponto3D.rotate_z_matrix(radians)
            self.angles.z = (self.angles.z + radians) % (2*np.pi)
        
        else:
            raise ValueError("Invalid axis. Use 'PITCH', 'YAW', or 'ROLL'.")
        
        resulting_vup = rotation_matrix @ vup
        resulting_normal = rotation_matrix @ normal
        self.vup = Vector(resulting_vup[0], resulting_vup[1], resulting_vup[2])
        self.normal = Vector(resulting_normal[0], resulting_normal[1], resulting_normal[2])

        self.recompute()

    def render_3d_object(self, object):

        vpn = self._viewport.vpn / np.linalg.norm(self._viewport.vpn)
        theta_x = np.arctan2(vpn[1], vpn[2])
        theta_y = np.arctan2(vpn[0], vpn[2])

        obj = cast(Object3D, object)
            
        segments = []

        for segment in obj.segments:

            updated_segment = []

            for point in segment:

                if self._3dperspective == c.PARALLEL_PROJECTION:
                    point_2d = self._render_parallel_projection(point, theta_x, theta_y)

                elif self._3dperspective == c.PERSPECTIVE_PROJECTION:
                    point_2d = self._render_perspective_projection(point)
                else:
                    raise ValueError("Invalid projection type")

                updated_segment.append(point_2d)
            
            # consertar para a outra tbm
            if self._3dperspective == c.PARALLEL_PROJECTION:
                updated_segment = self.align_z_axis(updated_segment)

            segments.append(self.normalize(updated_segment))

        obj.set_normalized_segments(segments)

    def _render_parallel_projection(self, point, theta_x, theta_y):

        point = cast(Ponto3D, point)
        updated_point = point.clone()

        updated_point.translate(-self._viewport.vrp[0], -self._viewport.vrp[1], -self._viewport.vrp[2])

        updated_point.rotate_x(np.degrees(-theta_x))
        updated_point.rotate_y(np.degrees(-theta_y))

        point_2d = updated_point.project_2d()

        return point_2d

    def _render_perspective_projection(self, point):
        
        point =  cast(Ponto3D, point)
        updated_point = point.clone()
        homogeneous_point = updated_point.to_homogeneous()

        print("Homogeneous point before projection:", np.array2string(homogeneous_point, precision=3, suppress_small=True))
        print("Projection matrix:", np.array2string(self._projection_matrix, precision=3, suppress_small=True))

        homogeneous_point = self._projection_matrix @ homogeneous_point

        print("Updated homogeneous point:", np.array2string(homogeneous_point, precision=3, suppress_small=True))

        homogeneous_point /= homogeneous_point[3]

        point_2d = (homogeneous_point[0], homogeneous_point[1])

        print(f"Point 2D after projection: {point_2d[0]:.3f}, {point_2d[1]:.3f}")	

        return point_2d

    def align_z_axis(self, vertices):
            
        x_min, y_min = self._viewport.window_bounds[0]
        x_max, y_max = self._viewport.window_bounds[1]

        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2

        # faz a translação do mundo (nesse caso, 1 objeto) para o centro da window
        translated = [(x - cx, y - cy) for x, y in vertices]

        # o ângulo de rotação é o ângulo entre a VUP e o eixo Y do mundo
        vx, vy, vz = self._viewport.vup
        angle = -np.arctan2(vx, vy)

        cos_a, sin_a = np.cos(angle), np.sin(angle)

        # rotaciona o mundo por -θ para alinhar o VUP com o eixo Y
        rotated = [
            (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
            for x, y in translated
        ]

        translated_back = [
            (x + cx, y + cy)
            for x, y in rotated
        ]

        return translated_back

    def normalize(self, vertices):
        x_min, y_min = self._viewport.window_bounds[0][:2]
        x_max, y_max = self._viewport.window_bounds[1][:2]

        window_width, window_height = x_max - x_min, y_max - y_min

        normalized_vertices = [
            ((x - x_min) / window_width, (y - y_min) / window_height)
            for x, y in vertices
        ]

        return normalized_vertices
    
    def translate_cop(self, dx, dy, dz):

        self._cop.translate(dx, dy, dz)

        self.recompute()
    
    @staticmethod
    def perspective_matrix(focal_distance):
        return np.array([
            [1, 0, 0,                   0],
            [0, 1, 0,                   0],
            [0, 0, 1,                   0],
            [0, 0, -1/focal_distance, 0]
        ], dtype=float)

    @staticmethod
    def translation_matrix(dx, dy, dz):
        return np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ], dtype=float)
    
class Vector:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar, self.z * scalar)

    def __truediv__(self, scalar):
        return Vector(self.x / scalar, self.y / scalar, self.z / scalar)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vector(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def magnitude(self):
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self):
        mag = self.magnitude()
        if mag == 0:
            return Vector(0, 0, 0)
        return self / mag

    def to_array(self):
        return np.array([self.x, self.y, self.z])

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y}, z={self.z})"