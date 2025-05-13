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

    def render_3d_object(self, obj):

        if self._3dperspective == c.PARALLEL_PROJECTION:
            self._render_parallel_projection(obj)

        elif self._3dperspective == c.PERSPECTIVE_PROJECTION:
            self._render_perspective_projection(obj)
        else:
            raise ValueError("Invalid projection type")

    def _render_parallel_projection(self, object):

        vpn = self._viewport.vpn / np.linalg.norm(self._viewport.vpn)
        theta_x = np.arctan2(vpn[1], vpn[2])
        theta_y = np.arctan2(vpn[0], vpn[2])

        obj = cast(Object3D, object)
            
        segments = []

        for segment in obj.segments:

            updated_segment = []

            for point in segment:

                point = cast(Ponto3D, point)

                updated_point = point.clone()

                updated_point.translate(-self._viewport.vrp[0], -self._viewport.vrp[1], -self._viewport.vrp[2])

                updated_point.rotate_x(np.degrees(-theta_x))
                updated_point.rotate_y(np.degrees(-theta_y))

                point_2d = updated_point.project_2d()

                updated_segment.append(point_2d)

            aligned = self.align_z_axis(updated_segment)

            segments.append(self.normalize(aligned))

        obj.set_normalized_segments(segments)

    def _render_perspective_projection(self, object):

        vpn = self._viewport.vpn / np.linalg.norm(self._viewport.vpn)
        theta_x = np.arctan2(vpn[1], vpn[2])
        theta_y = np.arctan2(vpn[0], vpn[2])

        obj = cast(Object3D, object)
            
        segments = []

        for segment in obj.segments:

            updated_segment = []

            for point in segment:

                point = cast(Ponto3D, point)

                updated_point = point.clone()

                updated_point.translate(-self._viewport.vrp[0], -self._viewport.vrp[1], -self._viewport.vrp[2])

                updated_point.rotate_x(np.degrees(-theta_x))
                updated_point.rotate_y(np.degrees(-theta_y))

                point_2d = updated_point.project_2d()

                updated_segment.append(point_2d)

            aligned = self.align_z_axis(updated_segment)

            segments.append(self.normalize(aligned))

        obj.set_normalized_segments(segments)

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
