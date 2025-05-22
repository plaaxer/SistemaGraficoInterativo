import constants as c
import numpy as np
from graphical_objects.ponto3d import Ponto3D
from graphical_objects.objeto3d import Object3D
from typing import cast
import math

class Renderer:
    def __init__(self, viewport, application):
        self._3dperspective = c.PERSPECTIVE_PROJECTION
        self._viewport = viewport
        self._application = application

        self._cop = Ponto3D(0, 0, -800)

        self._projection_matrix = None

        self._focal_distance = 500

        self._near_plane = 10.0
        self._far_plane = 5000.0

    def recompute(self):

        print("Starting recompute...")

        cop_translation = self.translation_matrix(-self._cop.x, -self._cop.y, -self._cop.z)

        print(f"Current camera location: {self._cop}")
        
        pitch, yaw, roll = self.extract_angles_from_vector(self._viewport.vpn, self._viewport.vup)

        # para os casos de yaw = 90 e yaw = 270, pode ser que o método acima retorne 0. verificar
        # tais edge cases
        if abs(self._viewport.vpn[2]) < 0.001 and abs(self._viewport.vpn[0]) > 0.9:
            if self._viewport.vpn[0] > 0:
                yaw = math.pi/2
            else:
                yaw = 3*math.pi/2
            print(f"Edge case detected! Setting yaw to {math.degrees(yaw):.2f} degrees")

        print(f"Pitch: {np.degrees(pitch)}, Yaw: {np.degrees(yaw)}, Roll: {np.degrees(roll)}")
        
        rotate_x = Ponto3D.rotate_x_matrix(pitch)
        rotate_y = Ponto3D.rotate_y_matrix(yaw)
        rotate_z = Ponto3D.rotate_z_matrix(roll)
        
        aligned = rotate_z @ rotate_y @ rotate_x

        perspective = self.perspective_matrix(self._focal_distance)

        print(f"Aligned Matrix: \n{aligned}")

        print(f"Translation Matrix: \n{cop_translation}")

        self._view_matrix = aligned @ cop_translation

        self._projection_matrix = perspective @ (self._view_matrix)

        print(f"Perspective Matrix: \n{self.perspective_matrix(self._focal_distance)}")
        print(f"Projection Matrix: \n{self._projection_matrix}")	

    def render_3d_object(self, object):

        vpn = self._viewport.vpn / np.linalg.norm(self._viewport.vpn)
        theta_x = np.arctan2(vpn[1], vpn[2])
        theta_y = np.arctan2(vpn[0], vpn[2])

        obj = cast(Object3D, object)
            
        segments = []

        for segment in obj.segments:

            updated_segment = []

            clipped_segment = False

            for point in segment:

                if self._3dperspective == c.PARALLEL_PROJECTION:
                    point_2d = self._render_parallel_projection(point, theta_x, theta_y)

                elif self._3dperspective == c.PERSPECTIVE_PROJECTION:
                    point_2d = self._render_perspective_projection(point)
                else:
                    raise ValueError("Invalid projection type")
                
                if point_2d is None:
                    clipped_segment = True
                    break

                updated_segment.append(point_2d)
            
            if clipped_segment:
                print("Segment clipped, skipping...")
                continue

            # consertar para a outra tbm
            if self._3dperspective == c.PARALLEL_PROJECTION:
                updated_segment = self.align_z_axis(updated_segment)

            segments.append(self.normalize_vertices(updated_segment))

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

        #updated_point.translate(-self._cop.x, -self._cop.y, -self._cop.z)

        homogeneous_point = updated_point.to_homogeneous()

        #print("Homogeneous point before projection:", np.array2string(homogeneous_point, precision=3, suppress_small=True))
        #print("Projection matrix:", np.array2string(self._projection_matrix, precision=3, suppress_small=True))

        camera_point = self._view_matrix @ homogeneous_point

        w_camera = camera_point[3]

        if camera_point[2] < self._near_plane * w_camera or camera_point[2] > self._far_plane * w_camera:
            print(f"Point is outside the clipping range: {camera_point[2]:.3f}")
            return None

        clipped_point = self._projection_matrix @ homogeneous_point

        clipped_point /= clipped_point[3]

        point_2d = (clipped_point[0], clipped_point[1])

        #print(f"Point 2D after projection: {point_2d[0]:.3f}, {point_2d[1]:.3f}")

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

    def normalize_vertices(self, vertices):
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

        # UTILIZAÇÃO DE IA: feito utilizando Gemini Flash com prompt:
    # "Write a function to extract pitch, yaw, and roll angles from a view direction vector (vpn) and an up vector (vup)."
    def extract_angles_from_vector(self, vpn_tuple, vup_tuple):

        print("VPN:", vpn_tuple)
        print("VUP:", vup_tuple)

        """
        Extracts pitch, yaw, and roll angles from a view direction vector (vpn)
        and an up vector (vup).

        Args:
            vpn_tuple: A tuple or list representing the view direction vector (x, y, z).
                       Assumed to be normalized or will be normalized internally.
            vup_tuple: A tuple or list representing the camera's up vector (x, y, z).
                       Assumed to be normalized or will be normalized internally.

        Returns:
            A tuple containing (pitch, yaw, roll) in radians.
        """
        # Convert input tuples to NumPy arrays
        vpn = np.array(vpn_tuple, dtype=float)
        vup = np.array(vup_tuple, dtype=float)

        # Ensure vpn and vup are normalized
        vpn = vpn / np.linalg.norm(vpn)
        vup = vup / np.linalg.norm(vup)

        # --- Calculate Pitch and Yaw ---
        # Assuming the camera is initially looking along the negative Z axis
        # and the up vector is along the positive Y axis.
        # Yaw is rotation around the global Y-axis.
        # Pitch is rotation around the camera's local X-axis.

        # Pitch (rotation around X axis)
        # This is derived from rotating the initial (0, 0, -1) vector.
        # The Y component of the rotated vector is sin(-pitch).
        # vpn.y = -sin(pitch) => pitch = -arcsin(vpn.y)
        # Using -vpn[1] matches the common convention where positive pitch
        # looks downwards if Y is up and Z is forward/backward. If Y is up
        # and -Z is forward, positive pitch typically means looking upwards.
        # Let's stick to the original logic's apparent convention for now.
        # A more standard approach often involves atan2(vpn.y, sqrt(vpn.x^2 + vpn.z^2))
        # for pitch relative to the horizontal plane.
        # However, the original code's approach is valid for a specific rotation order.
        pitch = np.arcsin(-vpn[1])

        if pitch <=  1e-6 and pitch >= -1e-6:
            # If pitch is close to zero, we can use atan2 for yaw directly.
            # This avoids potential issues with arcsin near the limits.
            # Yaw is the angle in the XZ plane, which is atan2(vpn.x, vpn.z).
            yaw = np.arctan2(vpn[0], vpn[2])
            pitch = 0.0

        # Yaw (rotation around Y axis)
        # This is the angle in the XZ plane.
        # atan2(x, z) gives the angle from the positive Z axis towards the positive X axis.
        yaw = np.arctan2(vpn[0], vpn[2])

        if abs(vpn[2]) < 1e-6:
            # If vpn[2] is close to zero, we are looking straight up or down.
            # In this case, yaw is undefined. We can set it to zero or handle it differently.
            # Let's set yaw to zero for this case.
            yaw = 0.0

        # --- Calculate Roll ---
        # Roll is rotation around the VPN axis. We need to see how the VUP vector
        # is rotated around VPN relative to a "true up" vector in the plane
        # perpendicular to VPN.

        # Calculate the "right" vector perpendicular to the global up (0,1,0) and vpn.
        # This right vector is in the horizontal plane if vpn is not vertical.
        global_up = np.array([0, 1, 0])
        
        # Handle the case where vpn is close to or aligned with global_up
        # If vpn is (0, 1, 0) or (0, -1, 0), the cross product with global_up is zero.
        # In this case, a different global reference (e.g., global_forward) might be needed
        # to establish a perpendicular vector. Let's use a robust approach.
        
        # A stable way to find a perpendicular vector:
        # If vpn is not close to the Y axis, use cross with global_up.
        # If vpn is close to the Y axis, use cross with a global_forward (e.g., 0,0,-1).
        
        # Threshold to check if vpn is close to the Y axis
        y_axis_threshold = 1e-4
        
        if abs(np.dot(vpn, global_up)) > (1.0 - y_axis_threshold):
            # VPN is close to the global Y axis, use a different reference vector
            global_forward = np.array([0, 0, -1])
            right = np.cross(global_up, global_forward) # This will be along the X axis (1, 0, 0)
        else:
             right = np.cross(global_up, vpn)
             
        # Normalize the right vector. Handle potential zero vector if vpn is perfectly vertical.
        right_norm = np.linalg.norm(right)
        if right_norm < 1e-6: # Handle the edge case where right is a zero vector
             # This should ideally not happen with the improved logic above,
             # but as a safeguard, if right is zero, it implies vpn is aligned with global_up.
             # In this specific scenario, the yaw is undefined by this method, and
             # we might need a different approach or convention.
             # For roll, if looking straight up or down, roll is relative to a different axis.
             # Let's assume for this function's context that vpn is not perfectly vertical.
             # If it is, pitch is +/- pi/2, and yaw and roll are degenerate.
             # We can return 0 for yaw and roll in this specific, less common case.
             if abs(vpn[1]) > 1.0 - 1e-6: # Check if looking straight up or down
                 # Pitch is +/- pi/2, yaw and roll are effectively zero/undefined by this method
                 return pitch, 0.0, 0.0
             else:
                 # This case should not be reached with the improved right vector calculation
                 # but as a fallback, if right is zero and vpn is not vertical, something is wrong.
                 # Return zeros or raise an error depending on desired behavior.
                 # For now, return zeros.
                 return pitch, yaw, 0.0 # Keep calculated pitch/yaw, set roll to 0
        else:
             right = right / right_norm


        # Calculate the "true up" vector for this orientation.
        # This is a vector perpendicular to vpn and right, forming an orthogonal basis.
        true_up = np.cross(vpn, right)
        # true_up is already orthogonal to vpn and right, and if vpn and right are normalized
        # and orthogonal, true_up is also normalized. However, re-normalizing adds robustness
        # against floating point errors.
        true_up = true_up / np.linalg.norm(true_up)

        # Project the camera's current up vector onto the plane perpendicular to VPN.
        # This projection removes any component of vup that is along vpn.
        vup_projected = vup - np.dot(vup, vpn) * vpn

        # Handle the case where vup_projected is a zero vector.
        # This happens if vup is parallel to vpn, which is an invalid camera configuration.
        vup_projected_norm = np.linalg.norm(vup_projected)
        if vup_projected_norm < 1e-6:
            # vup is parallel to vpn, this is an invalid state for determining roll.
            # Depending on desired behavior, you might raise an error or return a specific value.
            # Returning 0 roll might be a reasonable default for an invalid up vector.
            print("Warning: Camera up vector is parallel to view direction.")
            return pitch, yaw, 0.0 # Keep calculated pitch/yaw, set roll to 0


        vup_projected = vup_projected / vup_projected_norm

        # Calculate the roll angle.
        # Roll is the angle between true_up and vup_projected in the plane
        # perpendicular to vpn. We can use atan2 for a signed angle.
        # To use atan2, we need coordinates of vup_projected in the basis
        # formed by true_up and right in the plane perpendicular to vpn.
        # The component of vup_projected along true_up is dot(vup_projected, true_up).
        # The component of vup_projected along right is dot(vup_projected, right).

        # Using atan2(y, x) where y is the component along the "up" direction
        # and x is the component along the "right" direction in the view plane.
        # Our "up" direction in this plane is true_up, and our "right" direction is right.
        y_component = np.dot(vup_projected, true_up)
        x_component = np.dot(vup_projected, right)

        roll = np.arctan2(x_component, y_component)


        # The original roll calculation using arccos and a sign check is also valid,
        # but atan2 is generally preferred as it directly gives the signed angle
        # from -pi to +pi and avoids the need for a separate sign check.
        # Keeping the atan2 approach which is more direct and robust.

        return pitch, yaw, roll
    
    def switch_focal_distance(self):
        if self._focal_distance == 500:
            self._focal_distance = 100
        else:
            self._focal_distance = 500
    
    @staticmethod
    def perspective_matrix(focal_distance):
        return np.array([
            [1, 0, 0,                   0],
            [0, 1, 0,                   0],
            [0, 0, 1,                   0],
            [0, 0, 1/focal_distance, 0]
        ], dtype=float)

    @staticmethod
    def translation_matrix(dx, dy, dz):
        return np.array([
            [1, 0, 0, dx],
            [0, 1, 0, dy],
            [0, 0, 1, dz],
            [0, 0, 0, 1]
        ], dtype=float)
    
    def _normalize(self, v):
        norm = np.linalg.norm(v)
        if norm == 0:
            return v
        return v / norm
    
    def translate_window(self, dx, dy, dz):

        vpn_vec = np.array(self._viewport.vpn, dtype=float)
        vup_vec = np.array(self._viewport.vup, dtype=float)

        gaze_direction_world = self._normalize(vpn_vec)
        print("gaze direction", gaze_direction_world)

        right_direction_world = self._normalize(np.cross(vup_vec, gaze_direction_world))
        print("right direction", right_direction_world)

        up_direction_world = self._normalize(np.cross(gaze_direction_world, right_direction_world))
        
        displacement_world = (dx * right_direction_world +
                              dy * up_direction_world +
                              dz * gaze_direction_world)
        
        print("world displacement: ")

        self._cop.x += displacement_world[0]
        self._cop.y += displacement_world[1]
        self._cop.z += displacement_world[2]