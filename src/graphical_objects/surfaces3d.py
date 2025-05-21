from graphical_objects.objeto3d import Object3D
import numpy as np

class BezierSurface(Object3D):
    def __init__(self, name, id, points, color: str, fill=False):
        coordinates = self.generate(points)
        self.set_type("BezierSurface")
        super().__init__(name, id, coordinates, color, fill)
    
    def generate(self, points):
        """
        Generate coordinates for a Bezier surface from control points.
        Takes a list of points in the format [(x0,y0,z0), (x1,y1,z1), ...] and returns
        a list of line segments between adjacent points in the determined order.
        
        Args:
            points: List of (x,y,z) tuples representing control points
            
        Returns:
            List of coordinates defining the surface's line segments
        """
        if len(points) < 16:  # Need at least 4x4 control points
            return points
        
        # Define Bezier matrix
        M = np.array([
            [-1,  3, -3, 1],
            [ 3, -6,  3, 0],
            [-3,  3,  0, 0],
            [ 1,  0,  0, 0]
        ])
        
        Mt = M.transpose()
        segments = []
        step = 0.05  # Sampling density
        
        # Process control points in 4x4 patches
        for i in range(0, len(points) - 15, 16):  # Adjusted to process 16 points at a time
            # Extract control points for this patch
            patch_points = points[i:i+16]
            
            # Create coordinate matrices for x, y, z
            Gx = np.zeros((4, 4))
            Gy = np.zeros((4, 4))
            Gz = np.zeros((4, 4))
            
            # Fill the matrices with control point coordinates
            for r in range(4):
                for c in range(4):
                    idx = r * 4 + c
                    Gx[r, c] = patch_points[idx][0]  # x coordinate
                    Gy[r, c] = patch_points[idx][1]  # y coordinate
                    Gz[r, c] = patch_points[idx][2]  # z coordinate
            
            # Generate surface points
            surface_points = []
            s_values = np.arange(0, 1 + step, step)
            
            for s in s_values:
                row_points = []
                S = np.array([s**3, s**2, s, 1])
                S_M = S @ M
                
                for t in np.arange(0, 1 + step, step):
                    T = np.array([t**3, t**2, t, 1]).reshape(4, 1)
                    Mt_T = Mt @ T
                    
                    # Calculate point coordinates
                    x = S_M @ Gx @ Mt_T
                    y = S_M @ Gy @ Mt_T
                    z = S_M @ Gz @ Mt_T
                    
                    row_points.append((float(x), float(y), float(z)))
                
                surface_points.append(row_points)
            
            # Create line segments for this patch
            for r in range(len(surface_points)):
                for c in range(len(surface_points[0]) - 1):
                    # Horizontal segments
                    segments.append((surface_points[r][c], surface_points[r][c+1]))
            
            for c in range(len(surface_points[0])):
                for r in range(len(surface_points) - 1):
                    # Vertical segments
                    segments.append((surface_points[r][c], surface_points[r+1][c]))
        
        # Flatten segments into coordinates list
        coordinates = []
        for start, end in segments:
            coordinates.extend([start, end])
        
        return coordinates