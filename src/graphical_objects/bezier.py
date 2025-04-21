from graphical_objects.wireframe import Wireframe
from typing import List, Tuple, Sequence
import numpy as np
import math

class BezierCurve(Wireframe):
    def __init__(self, name, id, points, color: str, fill: bool = False):
        self.curve_coordinates = []
        self.create_bezier_curve(points)
        super().__init__(name, id, self.curve_coordinates, color, fill)
        self.set_type("Curve")

    def create_bezier_curve(self, points):
        self.curve_coordinates = []
        for i in range(0, len(points) - 3, 3):
            segment_points = self.calculate_bezier_curve(
                points[i], points[i + 1], points[i + 2], points[i + 3]
            )
            if i > 0:
                segment_points = segment_points[1:]
            self.curve_coordinates.extend(segment_points)

    def calculate_bezier_curve(self, point1, point2, point3, point4):
        curve_points = []

        matrix_basis = np.array(([-1, 3, -3, 1],
                       [3, -6, 3, 0],
                       [-3, 3, 0, 0],
                       [1, 0, 0, 0]), dtype=float)

        control_points_x = np.array(([float(point1[0])],
                        [float(point2[0])],
                        [float(point3[0])],
                        [float(point4[0])]), dtype=float)

        control_points_y = np.array(([float(point1[1])],
                        [float(point2[1])],
                        [float(point3[1])],
                        [float(point4[1])]), dtype=float)

        curve_points.append((point1[0], point1[1]))

        step = 0.001
        for i in np.arange(0.0, 1.0 + step, step):
            t2 = i * i
            t3 = t2 * i
            parameter_vector = np.array(([t3, t2, i, 1]), dtype=float)
            basis_x_parameter = np.dot(parameter_vector, matrix_basis)
            curve_point_x = np.dot(basis_x_parameter, control_points_x)[0]
            curve_point_y = np.dot(basis_x_parameter, control_points_y)[0]
            curve_points.append((curve_point_x, curve_point_y))

        curve_points.append((point4[0], point4[1]))

        return curve_points

    def modify(self, new_coords):
        self.coordinates = new_coords
        self.create_bezier_curve(new_coords)
        return self