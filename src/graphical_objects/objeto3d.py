import numpy as np
from graphical_objects.wireframe import Wireframe
from graphical_objects.ponto3d import Ponto3D

class Object3D(Wireframe):
    def __init__(self, name, id, coordinates: list[tuple[str, str, str]], color: str, fill=False):
        """
        Initialize a 3D object as a wireframe model.
        
        Args:
            segments: Optional list of line segments, where each segment
                      is a pair (tuple or list) of Ponto3D objects.
        """
        self._name = name
        self._id = id
        self._color = color
        self._clipped_vertices = None
        self._type = "3DObject"
        self.vertices = coordinates
        self.segments = []
        for i in range(0, len(coordinates) - 1, 2):
            self.add_segment(coordinates[i], coordinates[i + 1])
        self.in_window = [False] * len(self.segments)
        
    def add_segment(self, point1, point2):
        """
        Add a line segment to the object.
        
        Args:
            point1: Ponto3D object for the first point of the segment
            point2: Ponto3D object for the second point of the segment
        """
        if isinstance(point1, tuple):
            point1 = Ponto3D(point1[0], point1[1], point1[2])
        if isinstance(point2, tuple):
            point2 = Ponto3D(point2[0], point2[1], point2[2])

        self.segments.append((point1.clone(), point2.clone()))
        for p in (point1, point2):
            if p not in self.vertices:
                self.vertices.append(p)
        
    def add_segments(self, segments):
        """
        Add multiple line segments to the object.
        
        Args:
            segments: List of pairs of Ponto3D objects
        """
        for p1, p2 in segments:
            self.add_segment(p1, p2)
    
    def _apply_point_transformation(self, transformation, *args, **kwargs):
        """
        Apply a transformation to all points in the object.
        
        Args:
            transformation: Name of the transformation method from Ponto3D class
            *args, **kwargs: Arguments to pass to the transformation method
        """
        new_segments = []
        for p1, p2 in self.segments:
            # Apply transformation to copies of points to avoid modifying originals
            new_p1 = p1.clone()
            new_p2 = p2.clone()
            
            # Call the specified method on each point
            getattr(new_p1, transformation)(*args, **kwargs)
            getattr(new_p2, transformation)(*args, **kwargs)
            
            new_segments.append((new_p1, new_p2))
        
        self.segments = new_segments
        return self
    
    def translate(self, dx, dy, dz):
        """
        Translate the entire object by the specified coordinates.
        
        Args:
            dx, dy, dz: Displacement along each axis
        """
        return self._apply_point_transformation('translate', dx, dy, dz)
    
    def scale(self, sx, sy=None, sz=None, origin=None):
        """
        Scale the object by the specified factors.
        
        Args:
            sx, sy, sz: Scale factors for each axis
            origin: Optional point around which to perform the scaling
        """
        return self._apply_point_transformation('scale', sx, sy, sz, origin=origin)
    
    def rotate(self, angle_x=0, angle_y=0, angle_z=0, origin=None):
        """
        Rotate the object around the X, Y and Z axes.
        
        Args:
            angle_x, angle_y, angle_z: Rotation angles in degrees
            origin: Optional point around which to perform the rotation
        """
        return self._apply_point_transformation('rotate', 
                                               angle_x, angle_y, angle_z, 
                                               origin=origin)
    
    def rotate_around_axis(self, axis_start, axis_end, angle_degrees):
        """
        Rotate the object around an arbitrary axis defined by two points.
        
        Args:
            axis_start: Ponto3D that defines the start of the rotation axis
            axis_end: Ponto3D that defines the end of the rotation axis
            angle_degrees: Rotation angle in degrees
        """
        # Calculate the direction vector of the axis
        axis_vector = np.array([
            axis_end.x - axis_start.x,
            axis_end.y - axis_start.y,
            axis_end.z - axis_start.z
        ])
        
        # Normalize the direction vector
        axis_length = np.linalg.norm(axis_vector)
        if abs(axis_length) < 1e-10:
            raise ValueError("Axis points cannot be coincident")
        
        axis_vector = axis_vector / axis_length
        
        # Extract the components of the direction vector
        u, v, w = axis_vector
        
        # Convert angle to radians
        angle_rad = np.radians(angle_degrees)
        cos_angle = np.cos(angle_rad)
        sin_angle = np.sin(angle_rad)
        
        # Calculate the components of the Rodrigues rotation matrix
        # Formula for rotation around an arbitrary axis passing through the origin
        rot_matrix = np.array([
            [cos_angle + u*u*(1-cos_angle), u*v*(1-cos_angle) - w*sin_angle, u*w*(1-cos_angle) + v*sin_angle, 0],
            [v*u*(1-cos_angle) + w*sin_angle, cos_angle + v*v*(1-cos_angle), v*w*(1-cos_angle) - u*sin_angle, 0],
            [w*u*(1-cos_angle) - v*sin_angle, w*v*(1-cos_angle) + u*sin_angle, cos_angle + w*w*(1-cos_angle), 0],
            [0, 0, 0, 1]
        ], dtype=float)
        
        # If the axis doesn't pass through the origin, we need to adjust for this
        if not (abs(axis_start.x) < 1e-10 and abs(axis_start.y) < 1e-10 and abs(axis_start.z) < 1e-10):
            # Translation to origin
            t1 = np.array([
                [1, 0, 0, -axis_start.x],
                [0, 1, 0, -axis_start.y],
                [0, 0, 1, -axis_start.z],
                [0, 0, 0, 1]
            ], dtype=float)
            
            # Translation back
            t2 = np.array([
                [1, 0, 0, axis_start.x],
                [0, 1, 0, axis_start.y],
                [0, 0, 1, axis_start.z],
                [0, 0, 0, 1]
            ], dtype=float)
            
            # Combine transformations: t2 @ rot_matrix @ t1
            rot_matrix = t2 @ rot_matrix @ t1
        
        # Apply the transformation to all points
        new_segments = []
        for p1, p2 in self.segments:
            new_p1 = p1.clone()
            new_p2 = p2.clone()
            
            new_p1.transform(rot_matrix)
            new_p2.transform(rot_matrix)
            
            new_segments.append((new_p1, new_p2))
        
        self.segments = new_segments
        return self
    
    def __repr__(self):
        """String representation of the 3D object."""
        return f"Object3D with {len(self.segments)} segments"
    
    def clone(self):
        """Create a copy of the object."""
        new_object = Object3D()
        for p1, p2 in self.segments:
            new_object.add_segment(p1, p2)
        return new_object
    
    def center(self):
        """
        Calculate the geometric center (centroid) of the object.
        
        Returns:
            A Ponto3D object representing the center point of the object.
            Returns None if the object has no segments.
        """
        if not self.segments:
            return None
        
        all_points = self.get_vertices()
        
        num_points = len(all_points)
        sum_x = sum(p[0] for p in all_points)
        sum_y = sum(p[1] for p in all_points)
        sum_z = sum(p[2] for p in all_points)
        
        from ponto3d import Ponto3D
        
        return Ponto3D(
            sum_x / num_points,
            sum_y / num_points,
            sum_z / num_points
        )
    
    def get_vertices(self):
        all_points = set()
        for p1, p2 in self.segments:
            # Convert to tuple for hashability (assuming Ponto3D has x, y, z attributes)
            all_points.add((p1.x, p1.y, p1.z))
            all_points.add((p2.x, p2.y, p2.z))
        return list(all_points)
    
    def set_normalized_segments(self, segments):
        self.normalized_segments = segments
    
    def get_normalized_segments(self):
        return self.normalized_segments
    
    def draw(self, canvas):
        lines = self.get_normalized_segments()
        
        for i in range(len(lines)):
                #print(self.in_window)
                if not self.in_window[i]:
                    continue
                x0, y0 = canvas.window_to_viewport(*lines[i][0])
                x1, y1 = canvas.window_to_viewport(*lines[i][1])
                canvas.create_line(
                x0, y0,
                x1, y1,
                fill=self._color
            )