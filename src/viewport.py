from tkinter import Canvas
from display_file import DisplayFile
import constants as c
import numpy as np

class Viewport(Canvas):
    def __init__(self, app, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.display_file = DisplayFile()
        self._app = app

        # coordenadas da janela
        self.window_bounds = c.WINDOW_BOUNDS
        self.vup = c.VIEW_UP_VECTOR
        self.margin = 0.05  # margem da janela de clipping

        self.window_angle = 0

    def draw(self):
        for obj in self.display_file.get_objects():
            if obj.in_window:  # Desenha apenas objetos visíveis
                obj.draw(self)
        self.draw_clipping_window()
        self.display_file.notify()
    
    def window_to_viewport(self, x, y):
        
        # dimensão da viewport - atualmente o mesmo tamanho do canvas
        self.viewport_width = self.winfo_width()
        self.viewport_height = self.winfo_height()

        # utilizando scn
        window_x_min, window_y_min = (0, 0)
        window_x_max, window_y_max = (1, 1)

        viewport_x = ((x - window_x_min) / (window_x_max - window_x_min)) * self.viewport_width
        viewport_y = (1 - (y - window_y_min) / (window_y_max - window_y_min)) * self.viewport_height

        return viewport_x, viewport_y
    
    def translate_window(self, dwx, dwy):

            print("Requested translation:", dwx, dwy)

            # VUP: eixo Y da janela
            vx, vy = self.vup

            angle = -np.arctan2(vx, vy)

            print("Current angle:", np.degrees(angle))

            print("Sin(angle):", np.sin(angle), "Cos(angle):", np.cos(angle))

            world_dx = dwx * np.cos(angle) + dwy * np.sin(angle)

            world_dy = -dwx * np.sin(angle) + dwy * np.cos(angle)

            print("World dx:", world_dx, "World dy:", world_dy)

            # atualiza as coordenadas da janela
            x_min, y_min = self.window_bounds[0]
            x_max, y_max = self.window_bounds[1]
            x_min += world_dx
            y_min += world_dy
            x_max += world_dx
            y_max += world_dy
            self.window_bounds[0] = (x_min, y_min)
            self.window_bounds[1] = (x_max, y_max)

            print("New window bounds:", self.window_bounds)

            self.update()


    def rotate_window(self, angle: int):

        # apenas para referência no futuro
        self.window_angle = (self.window_angle + angle) % 360

        # rotaciona o vup
        rad = np.radians(angle)
        cos_a = np.cos(rad)
        sin_a = np.sin(rad)
        vx, vy = self.vup
        rotated_vup = (vx * cos_a - vy * sin_a, vx * sin_a + vy * cos_a)
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


    def draw_y_direction(self, length=50, color="red"):

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

    def draw_clipping_window(self):
        # Define os limites da janela de clipping
        x_min, y_min = self.window_to_viewport(-1 + self.margin, -1 + self.margin)
        x_max, y_max = self.window_to_viewport(1 - self.margin, 1 - self.margin)

        # Desenha um retângulo representando a área visível
        self.create_rectangle(
            x_min, y_min, x_max, y_max,
            outline="red", width=2, dash=(5, 5)  # Linha tracejada para indicar os limites
        )
    
    def update_specific_scn(self, obj):
            #print("---UPDATING SCN---")

            # localização da window
            x_min, y_min = self.window_bounds[0]
            x_max, y_max = self.window_bounds[1]

            # computa o centro da window
            cx = (x_min + x_max) / 2
            cy = (y_min + y_max) / 2

            # tamanho da window
            window_width = x_max - x_min
            window_height = y_max - y_min

            vertices = obj.get_vertices()

            print("vertices in specific scn size: ", len(vertices))
                
            # faz a translação do mundo (nesse caso, 1 objeto) para o centro da window
            translated = [(x - cx, y - cy) for x, y in vertices]

            print("translated size: ", len(translated))

            # o ângulo de rotação é o ângulo entre a VUP e o eixo Y do mundo
            vx, vy = self.vup
            angle = -np.arctan2(vx, vy)

            cos_a, sin_a = np.cos(angle), np.sin(angle)

            # rotaciona o mundo por -θ para alinhar o VUP com o eixo Y
            rotated = [
                (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
                for x, y in translated
            ]

            print("rotated size: ", len(rotated))

            # normaliza de volta para scn
            scn = [
                ((x + window_width / 2) / window_width,
                (y + window_height / 2) / window_height)
                for x, y in rotated
            ]

            print("scn in update size: ", len(scn))

            obj.set_scn_vertices(scn)
    
    def desnormalizar_vertices(self, scn_vertices, window_bounds, vup):

        # localização da window
        x_min, y_min = window_bounds[0]
        x_max, y_max = window_bounds[1]

        # computa o centro da window
        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2

        # ângulo entre a VUP e o eixo Y do mundo (mesmo cálculo que antes)
        vx, vy = vup
        angle = -np.arctan2(vx, vy)

        cos_a, sin_a = np.cos(-angle), np.sin(-angle)  # desfazendo a rotação

        # tamanho da window
        window_width = x_max - x_min
        window_height = y_max - y_min

        # desfaz a normalização
        rotated = [
            (x * window_width - window_width / 2,
            y * window_height - window_height / 2)
            for x, y in scn_vertices
        ]

        # desfaz a rotação (rotaciona por +θ)
        translated = [
            (x * cos_a - y * sin_a, x * sin_a + y * cos_a)
            for x, y in rotated
        ]

        # desfaz a translação (move o centro de volta)
        original = [
            (x + cx, y + cy)
            for x, y in translated
        ]

        return original

    
    def update_all_scn(self):
        for obj in self.display_file.get_objects():
            self.update_specific_scn(obj)

    def update(self):
        self.update_all_scn()
        self._app.clip_objects()
        self.clear()
        self.draw()
        self.update_idletasks()