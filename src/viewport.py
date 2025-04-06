from tkinter import Canvas
from display_file import DisplayFile
import constants as c
import numpy as np

class Viewport(Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.display_file = DisplayFile()

        # coordenadas da janela
        self.window_bounds = c.WINDOW_BOUNDS
        self.vup = c.VIEW_UP_VECTOR

    def draw(self):
        for obj in self.display_file.get_objects():
            obj.draw(self)
        self.display_file.notify()
    
    def window_to_viewport(self, x, y):
        
        # dimensão da viewport
        self.viewport_width = self.winfo_width()
        self.viewport_height = self.winfo_height()

        # utilizando scn
        window_x_min, window_y_min = (0, 0)
        window_x_max, window_y_max = (1, 1)

        viewport_x = ((x - window_x_min) / (window_x_max - window_x_min)) * self.viewport_width
        viewport_y = (1 - (y - window_y_min) / (window_y_max - window_y_min)) * self.viewport_height

        return viewport_x, viewport_y
    
    def translate_window(self, x, y):
        # lembrando que é o inverso
        self.window_bounds[0] = (self.window_bounds[0][0] + x, self.window_bounds[0][1] - y)
        self.window_bounds[1] = (self.window_bounds[1][0] + x, self.window_bounds[1][1] - y)

        self.update()
    
    def rotate_window(self, angle: int):
        # Step 1: Update the Viewport's SCN for all objects
        print("---Rotating window---")
        
        # 2. Rotate window bounds
        # Compute the center of the window
        x_min, y_min = self.window_bounds[0]
        x_max, y_max = self.window_bounds[1]

        # Compute center
        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2

        # Convert the rotation angle from degrees to radians
        rad = np.radians(angle)
        cos_a, sin_a = np.cos(rad), np.sin(rad)

        # Create rotation matrix (2D)
        rotation_matrix = np.array([
            [cos_a, -sin_a],
            [sin_a, cos_a]
        ])

        # Rotate the window bounds
        window_centered = [
            (x - cx, y - cy) for x, y in [self.window_bounds[0], self.window_bounds[1]]
        ]

        rotated = [
            np.dot(rotation_matrix, [x, y]) for x, y in window_centered
        ]

        # Update window bounds after rotation
        rotated_x_min, rotated_y_min = rotated[0]
        rotated_x_max, rotated_y_max = rotated[1]

        self.window_bounds[0] = (rotated_x_min + cx, rotated_y_min + cy)
        self.window_bounds[1] = (rotated_x_max + cx, rotated_y_max + cy)

        # Step 3: Update all objects' SCN vertices after rotation
        self.update()

    
    def zoom(self, factor):

        self.window_bounds[0] = (self.window_bounds[0][0] * factor, self.window_bounds[0][1] * factor)
        self.window_bounds[1] = (self.window_bounds[1][0] * factor, self.window_bounds[1][1] * factor)

        self.update()

    def clear(self):
        self.delete("all")
    
    def update_specific_scn(self, obj):
            print("---UPDATING SCN---")
            # Extract window bounds from the viewport
            x_min, y_min = self.window_bounds[0]
            x_max, y_max = self.window_bounds[1]

            # 1. Compute the center of the window
            cx = (x_min + x_max) / 2
            cy = (y_min + y_max) / 2

            # 2. View Up Vector angle with Y-axis
            vx, vy = self.vup
            angle = -np.arctan2(vx, vy)  # angle to rotate world so vup aligns with Y

            cos_a, sin_a = np.cos(angle), np.sin(angle)

            # 3. Window dimensions for normalization
            window_width = x_max - x_min
            window_height = y_max - y_min

            # 4. Translate world so window center is at the origin
            translated = [(x - cx, y - cy) for x, y in obj.get_vertices()]

            # 5. Rotate world by -θ to align VUP with Y axis
            rotated = [
                (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
                for x, y in translated
            ]

            # 6. Normalize into SCN (0 to 1)
            scn = [
                ((x + window_width / 2) / window_width,
                (y + window_height / 2) / window_height)
                for x, y in rotated
            ]

            # 7. Update normalized coordinates in the viewport (instead of object)
            # Now updating the viewport's internal object list or the object itself
            obj.set_scn_vertices(scn)
    
    def update_all_scn(self):
        # todo: otimizar pra n recalcular todos os objetos
        for obj in self.display_file.get_objects():
            self.update_specific_scn(obj)

    def update(self):
        print("display file objects", self.display_file.get_objects())
        self.update_all_scn()
        self.clear()
        self.draw()
        self.update_idletasks()