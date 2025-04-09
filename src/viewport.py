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
        # self.draw_y_direction()
        self.draw_window_axes()
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
    
    def translate_window(self, dwx, dwy):
        """
        Translada a janela no sistema da janela (dwx, dwy).
        Ex: dwx = -10 move 10 unidades 'à esquerda' da viewport.
        """
        
        # # lembrando que é o inverso
        # self.window_bounds[0] = (self.window_bounds[0][0] + dwx, self.window_bounds[0][1] - dwy)
        # self.window_bounds[1] = (self.window_bounds[1][0] + dwx, self.window_bounds[1][1] - dwy)

        # self.update()

        # VUP: eixo Y da janela
        vx, vy = self.vup

        angle = -np.arctan2(vx, vy)

        dmx = dwx * np.cos(angle) - dwy * np.sin(angle)
        dmy = dwx * np.sin(angle) + dwy * np.cos(angle)

        # atualiza as coordenadas da janela
        x_min, y_min = self.window_bounds[0]
        x_max, y_max = self.window_bounds[1]
        x_min += dmx
        y_min += dmy
        x_max += dmx
        y_max += dmy
        self.window_bounds[0] = (x_min, y_min)
        self.window_bounds[1] = (x_max, y_max)

        self.update()


    def rotate_window(self, angle: int):
        print("---Rotating window (VUP)---")

        rad = np.radians(angle)
        cos_a = np.cos(rad)
        sin_a = np.sin(rad)

        # rotaciona VUP
        vx, vy = self.vup
        rotated_vup = np.dot([
            [cos_a, -sin_a],
            [sin_a, cos_a]], 
            [vx, vy])

        # só normaliza por causa do erro de precisão
        norm = np.linalg.norm(rotated_vup)
        if norm != 0:
            self.vup = (rotated_vup[0] / norm, rotated_vup[1] / norm)

        self.update()

    def zoom(self, factor):

        self.window_bounds[0] = (self.window_bounds[0][0] * factor, self.window_bounds[0][1] * factor)
        self.window_bounds[1] = (self.window_bounds[1][0] * factor, self.window_bounds[1][1] * factor)

        self.update()

    def clear(self):
        self.delete("all")

    # apenas para debug
    def draw_y_direction(self, length=50, color="red"):
        # Get current viewport size
        viewport_width = self.winfo_width()
        viewport_height = self.winfo_height()
        cx = viewport_width / 2
        cy = viewport_height / 2

        vx, vy = self.vup
        end_x = cx + vx * length
        end_y = cy - vy * length

        self.create_line(cx, cy, end_x, end_y, fill=color, width=2, arrow="last")

    def draw_window_axes(self, length=50):
        cx = self.winfo_width() / 2
        cy = self.winfo_height() / 2

        # Eixo Y (VUP)
        vx, vy = self.vup
        self.create_line(cx, cy, cx + vx * length, cy - vy * length, fill="red", arrow="last")  # Y

        # Eixo X (perpendicular a VUP)
        ux, uy = vy, -vx
        self.create_line(cx, cy, cx + ux * length, cy - uy * length, fill="blue", arrow="last")  # X

    
    def update_specific_scn(self, obj):
            print("---UPDATING SCN---")

            # localização da window
            x_min, y_min = self.window_bounds[0]
            x_max, y_max = self.window_bounds[1]

            # computa o centro da window
            cx = (x_min + x_max) / 2
            cy = (y_min + y_max) / 2

            # faz a translação do mundo (nesse caso, 1 objeto) para o centro da window
            translated = [(x - cx, y - cy) for x, y in obj.get_vertices()]

            # o ângulo de rotação é o ângulo entre a VUP e o eixo Y do mundo
            vx, vy = self.vup
            angle = -np.arctan2(vx, vy)

            cos_a, sin_a = np.cos(angle), np.sin(angle)

            # tamanho da window
            window_width = x_max - x_min
            window_height = y_max - y_min

            # rotaciona o mundo por -θ para alinhar o VUP com o eixo Y
            rotated = [
                (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
                for x, y in translated
            ]

            # normaliza de volta para scn
            scn = [
                ((x + window_width / 2) / window_width,
                (y + window_height / 2) / window_height)
                for x, y in rotated
            ]

            # faz o update das coordenadas normalizadas do objeto
            obj.set_scn_vertices(scn)
    
    def update_all_scn(self):
        for obj in self.display_file.get_objects():
            self.update_specific_scn(obj)

    def update(self):
        print("display file objects", self.display_file.get_objects())
        self.update_all_scn()
        self.clear()
        self.draw()
        self.update_idletasks()