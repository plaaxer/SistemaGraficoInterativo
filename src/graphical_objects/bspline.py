from graphical_objects.wireframe import Wireframe
from typing import List, Tuple, Sequence
import numpy as np
import math

class BSplineCurve(Wireframe):
    def __init__(self, name, id, points, color: str, fill: bool = False):
        self.curve_coordinates = []
        self.create_bspline_curve(points)
        super().__init__(name, id, self.curve_coordinates, color, fill)
        self.set_type("Curve")

    def create_bspline_curve(self, points, step=0.01):
        processed_points = np.array(points)
        curve_points = self._calculate_bspline(processed_points, step)
        self.curve_coordinates = curve_points

    def _calculate_bspline(self, points, step):
        if len(points) < 4:
            return points.tolist()
            
        # B-spline basis matrix
        M = (1/6) * np.array([
            [-1, 3, -3, 1],
            [3, -6, 3, 0],
            [-3, 0, 3, 0],
            [1, 4, 1, 0]
        ])
        
        curve_points = []
        
        for i in range(len(points) - 3):
            # Get control points for this segment
            control_points = points[i:i+4]
            
            # Calculate curve points using forward differences
            segment_curve = self._forward_diff_bspline(control_points, M, step)
            curve_points.extend(segment_curve)
            
        return curve_points
        
    def _forward_diff_bspline(self, control_points, M, step):
        n_steps = math.ceil(1 / step)
        
        # Extract coordinates from control points
        if control_points.shape[1] == 2:  # 2D points
            px = control_points[:, 0]
            py = control_points[:, 1]
            
            # Calculate coefficients
            cx = M @ px
            cy = M @ py
            
            # Setup forward differences
            d1 = step
            d2 = d1 * step
            d3 = d2 * step
            
            # Create forward difference matrix
            E = np.array([
                [0, 0, 0, 1],
                [d3, d2, d1, 0],
                [6*d3, 2*d2, 0, 0],
                [6*d3, 0, 0, 0]
            ])
            
            # Calculate initial values
            Dx = E @ cx
            Dy = E @ cy
            
            # Generate curve points
            curve_points = []
            x, y = Dx[0], Dy[0]
            
            for _ in range(n_steps):
                curve_points.append((x, y))
                
                # Update using forward differences
                x += Dx[1]
                Dx[1] += Dx[2]
                Dx[2] += Dx[3]
                
                y += Dy[1]
                Dy[1] += Dy[2]
                Dy[2] += Dy[3]
                
            return curve_points
            
        elif control_points.shape[1] == 3:  # 3D points
            px = control_points[:, 0]
            py = control_points[:, 1]
            pz = control_points[:, 2]
            
            # Calculate coefficients
            cx = M @ px
            cy = M @ py
            cz = M @ pz
            
            # Setup forward differences
            d1 = step
            d2 = d1 * step
            d3 = d2 * step
            
            # Create forward difference matrix
            E = np.array([
                [0, 0, 0, 1],
                [d3, d2, d1, 0],
                [6*d3, 2*d2, 0, 0],
                [6*d3, 0, 0, 0]
            ])
            
            # Calculate initial values
            Dx = E @ cx
            Dy = E @ cy
            Dz = E @ cz
            
            # Generate curve points
            curve_points = []
            x, y, z = Dx[0], Dy[0], Dz[0]
            
            for _ in range(n_steps):
                curve_points.append((x, y, z))
                
                # Update using forward differences
                x += Dx[1]
                Dx[1] += Dx[2]
                Dx[2] += Dx[3]
                
                y += Dy[1]
                Dy[1] += Dy[2]
                Dy[2] += Dy[3]
                
                z += Dz[1]
                Dz[1] += Dz[2]
                Dz[2] += Dz[3]
                
            return curve_points
            
        else:
            raise ValueError("Points must be 2D or 3D")
        
    def modify(self, new_coords):
        self.coordinates = new_coords
        self.create_bspline_curve(new_coords)
        super().modify(self.curve_coordinates)
        return self
