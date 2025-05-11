import numpy as np
from math import sin, cos, radians

# interface geral: 3 operações de transformação (translação, escala e rotação)
# https://medium.com/@rcalvarez/an-explanation-of-homogeneous-coordinates-and-spatial-matrices-using-blender-b3b5e2ef4412

class Ponto3D:
    def __init__(self, x, y, z):
        """Initialize a 3D point with x, y, z coordinates."""
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
        self._homogeneous = np.array([x, y, z, 1], dtype=float)
        self._type = "3DPoint"
    
    def __eq__(self, other):
        if not isinstance(other, Ponto3D):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __hash__(self):
        return hash((self.x, self.y, self.z))

    def __repr__(self):
        """String representation of the 3D point."""
        return f"Ponto3D({self.x:.3f}, {self.y:.3f}, {self.z:.3f})"
    
    def __eq__(self, other):
        """Check if two points are equal."""
        if not isinstance(other, Ponto3D):
            return False
        return np.allclose([self.x, self.y, self.z], [other.x, other.y, other.z])
    
    def __iter__(self):
        """Make the point iterable to easily access its coordinates."""
        yield self.x
        yield self.y
        yield self.z
    
    def to_array(self):
        """Convert to numpy array (non-homogeneous)."""
        return np.array([self.x, self.y, self.z])
    
    def to_homogeneous(self):
        """Return the homogeneous coordinates as an array [x, y, z, 1]."""
        return self._homogeneous.copy()
    
    def _apply_transform(self, matrix):
        """Apply a 4x4 transformation matrix to the point and update its coordinates."""
        result = matrix @ self._homogeneous
        # nomaliza para coordenadas homogêneas
        if abs(result[3]) > 1e-10:  # evita divisão por zero para aproximações numéricas muito pequenas
            result = result / result[3]
        self.x, self.y, self.z = result[0], result[1], result[2]
        self._homogeneous = np.array([self.x, self.y, self.z, 1], dtype=float)
        return self
    
    def translate(self, dx, dy, dz):
        """Translate the point by dx, dy, dz."""
        matrix = np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ], dtype=float)
        return self._apply_transform(matrix)
    
    def scale(self, sx, sy=None, sz=None, origin=None):
        """
        Scale the point by sx, sy, sz factors.
        If origin is specified, scaling happens relative to that point.
        """
        # caso scale uniforme, sx = sy = sz
        sy = sx if sy is None else sy
        sz = sx if sz is None else sz
        
        scale_matrix = np.array([
            [sx, 0, 0, 0],
            [0, sy, 0, 0],
            [0, 0, sz, 0],
            [0, 0, 0, 1]
        ], dtype=float)
        
        if origin is None:
            # escalonamento a partir da origem (0, 0, 0)
            return self._apply_transform(scale_matrix)
        else:

            t1 = np.array([
                [1, 0, 0, -origin.x],
                [0, 1, 0, -origin.y],
                [0, 0, 1, -origin.z],
                [0, 0, 0, 1]
            ], dtype=float)
            
            # 1. translacionar ponto para a origem
            # 2. escalonar
            # 3. translacionar de volta
            
            t2 = np.array([
                [1, 0, 0, origin.x],
                [0, 1, 0, origin.y],
                [0, 0, 1, origin.z],
                [0, 0, 0, 1]
            ], dtype=float)
            
            # matriza de transformação composta
            transform = t2 @ scale_matrix @ t1
            return self._apply_transform(transform)
    
    def rotate_x(self, angle_degrees, origin=None):
        """Rotate around the X axis by the given angle in degrees."""
        angle = radians(angle_degrees)
        
        rotation = self.rotate_x_matrix(angle)
        
        return self._rotate_around_origin(rotation, origin)
    
    def rotate_y(self, angle_degrees, origin=None):
        """Rotate around the Y axis by the given angle in degrees."""
        angle = radians(angle_degrees)
        
        rotation = self.rotate_y_matrix(angle)
        
        return self._rotate_around_origin(rotation, origin)
    
    def rotate_z(self, angle_degrees, origin=None):
        """Rotate around the Z axis by the given angle in degrees."""
        angle = radians(angle_degrees)
        
        rotation = self.rotate_z_matrix(angle)
        
        return self._rotate_around_origin(rotation, origin)
    
    def _rotate_around_origin(self, rotation_matrix, origin=None):
        """Apply rotation around a specific origin point."""
        if origin is None:
            # rotacionar em torno da origem (0, 0, 0)
            return self._apply_transform(rotation_matrix)
        else:

            t1 = np.array([
                [1, 0, 0, -origin.x],
                [0, 1, 0, -origin.y],
                [0, 0, 1, -origin.z],
                [0, 0, 0, 1]
            ], dtype=float)
            
            # translaciona, aplica a rotação e depois translaciona de volta

            t2 = np.array([
                [1, 0, 0, origin.x],
                [0, 1, 0, origin.y],
                [0, 0, 1, origin.z],
                [0, 0, 0, 1]
            ], dtype=float)
            
            transform = t2 @ rotation_matrix @ t1
            return self._apply_transform(transform)
    
    def rotate(self, angle_x=0, angle_y=0, angle_z=0, origin=None):
        """
        Apply a composite rotation around all three axes.
        Rotation is applied in the order: Z, Y, X.
        Angles are in degrees.
        """
        # convertendo para radianos
        rx, ry, rz = map(radians, (angle_x, angle_y, angle_z))
        
        rot_x = self.rotate_x_matrix(rx)
        rot_y = self.rotate_y_matrix(ry)
        rot_z = self.rotate_z_matrix(rz)
        
        # matriz combinada de rotação
        combined_rotation = rot_x @ rot_y @ rot_z
        
        return self._rotate_around_origin(combined_rotation, origin)
    
    def transform(self, matrix):
        """Apply an arbitrary 4x4 transformation matrix to the point."""
        if matrix.shape != (4, 4):
            raise ValueError("Transformation matrix must be 4x4")
        return self._apply_transform(matrix)
    
    def clone(self):
        """Create a new identical point."""
        return Ponto3D(self.x, self.y, self.z)
    
    def distance_to(self, other):
        """Calculate the Euclidean distance to another point."""
        return np.sqrt((self.x - other.x)**2 + 
                       (self.y - other.y)**2 + 
                       (self.z - other.z)**2)
    
    @staticmethod
    def rotate_x_matrix(angle_radians):
        """Return the rotation matrix for a rotation around the X axis."""
        c, s = cos(angle_radians), sin(angle_radians)
        return np.array([
            [1, 0, 0, 0],
            [0, c, -s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotate_y_matrix(angle_radians):
        """Return the rotation matrix for a rotation around the Y axis."""
        c, s = cos(angle_radians), sin(angle_radians)
        return np.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    @staticmethod
    def rotate_z_matrix(angle_radians):
        """Return the rotation matrix for a rotation around the Z axis."""
        c, s = cos(angle_radians), sin(angle_radians)
        return np.array([
            [c, -s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ], dtype=float)
    
    def project_2d(self):
        return (self.x, self.y)