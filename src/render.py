import constants as c
import numpy as np
from graphical_objects.ponto3d import Ponto3D
from graphical_objects.objeto3d import Object3D
from typing import cast

class Renderer:
    def __init__(self, viewport, application):
        self._3dperspective = c.PARALLEL_PROJECTION
        self._viewport = viewport
        self._application = application

        self._cop = Ponto3D(0, 0, 0)

        self._projection_matrix = None

        self._focal_distance = 500

    def extract_angles_from_vector(vpn):
        # Assuming vpn is normalized
        # Get the pitch (rotation around X axis)
        pitch = np.arcsin(-vpn[1])
        
        # Get the yaw (rotation around Y axis)
        yaw = np.arctan2(vpn[0], vpn[2])
        
        # Roll (rotation around Z) typically requires additional info
        # Often set to 0 or computed from VUP and VPN
        roll = 0
        
        return pitch, yaw, roll

    # Then in your renderer:
    def recompute(self):
        cop_translation = self.translation_matrix(-self._cop.x, -self._cop.y, -self._cop.z)
        
        # Extract angles from the direction vector
        pitch, yaw, roll = extract_angles_from_vector(self._viewport.vpn)
        
        # Use these angles for rotation matrices
        rotate_x = Ponto3D.rotate_x_matrix(pitch)
        rotate_y = Ponto3D.rotate_y_matrix(yaw)
        rotate_z = Ponto3D.rotate_z_matrix(roll)
        
        aligned = rotate_z @ rotate_y @ rotate_x
        self._projection_matrix = self.perspective_matrix(self._focal_distance) @ aligned @ cop_translation




    def render_3d_object(self, obj):

        vpn = self._viewport.vpn / np.linalg.norm(self._viewport.vpn)
        theta_x = np.arctan2(vpn[1], vpn[2])
        theta_y = np.arctan2(vpn[0], vpn[2])

        obj = cast(Object3D, object)
            
        segments = []

        for segment in obj.segments:

            updated_segment = []

            for point in segment:

                if self._3dperspective == c.PARALLEL_PROJECTION:
                    point_2d = self._render_parallel_projection(obj, theta_x, theta_y)

                elif self._3dperspective == c.PERSPECTIVE_PROJECTION:
                    point_2d = self._render_perspective_projection(obj)
                else:
                    raise ValueError("Invalid projection type")

                updated_segment.append(point_2d)

            aligned = self.align_z_axis(updated_segment)

            segments.append(self.normalize(aligned))

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

        return rotated

    def normalize(self, vertices):
        x_min, y_min = self._viewport.window_bounds[0][:2]
        x_max, y_max = self._viewport.window_bounds[1][:2]

        window_width, window_height = x_max - x_min, y_max - y_min

        normalized_vertices = [
            ((x - x_min) / window_width, (y - y_min) / window_height)
            for x, y in vertices
        ]

        return normalized_vertices
    
    @staticmethod
    def perspective_matrix(self, focal_distance):
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, -1/focal_distance],
            [0, 0, 0, 1]
        ], dtype=float)

    @staticmethod
    def translation_matrix(dx, dy, dz):
        return np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ], dtype=float)