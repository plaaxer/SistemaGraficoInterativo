from tkinter import Canvas
from display_file import DisplayFile
import constants as c
import numpy as np
from graphical_objects.ponto3d import Ponto3D
from render import Renderer
from typing import cast

class Viewport(Canvas):
    def __init__(self, app, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.display_file = DisplayFile()

        from graphical_system import GraphicalSystem
        self._app = cast(GraphicalSystem, app)

        # coordenadas da janela
        self.window_bounds = c.WINDOW_BOUNDS
        self.vup = c.VIEW_UP_VECTOR
        self.vrp = c.VIEW_REFERENCE_POINT
        self.vpn = c.VIEW_PLANE_NORMAL
        self.margin = 0.05  # margem da janela de clipping

        self.window_angle = 0

        self.renderer = Renderer(self, app)

    def draw(self):
        for obj in self.display_file.get_objects():
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
    
    def translate_window(self, dwx, dwy, dwz=0):

        vpn = np.array([self.vpn[0], self.vpn[1], self.vpn[2]])
        vup = np.array([self.vup[0], self.vup[1], self.vup[2]])
        
        vpn = vpn / np.linalg.norm(vpn)
        vup = vup / np.linalg.norm(vup)
        
        right_vector = np.cross(vpn, vup)
        right_vector = right_vector / np.linalg.norm(right_vector)
        
        vup = np.cross(right_vector, vpn)
        vup = vup / np.linalg.norm(vup)

        world_translation = right_vector * dwx + vup * dwy + vpn * dwz
        
        world_dx, world_dy, world_dz = world_translation
        
        x_min, y_min = self.window_bounds[0]
        x_max, y_max = self.window_bounds[1]
        x_min += world_dx
        y_min += world_dy
        x_max += world_dx
        y_max += world_dy
        self.window_bounds[0] = (x_min, y_min)
        self.window_bounds[1] = (x_max, y_max)
        
        self.vrp[0] += world_dx
        self.vrp[1] += world_dy
        self.vrp[2] += world_dz
        
        self.renderer.translate_cop(world_dx, world_dy, world_dz)
        
        self.update()


    def rotate_window(self, angle_x=0, angle_y=0, angle_z=0):
        """
        Rotaciona a window em torno dos eixos X, Y e Z.
        """
        #print("Requested rotation:", angle_x, angle_y, angle_z)

        def rotation_matrix(axis, angle):
            angle = np.radians(angle)
            c, s = np.cos(angle), np.sin(angle)
            if axis == 'x':
                return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
            elif axis == 'y':
                return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
            elif axis == 'z':
                return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

        # Rotação em torno do eixo X
        if angle_x != 0:
            rot_x = rotation_matrix('x', angle_x)
            self.vpn = np.dot(rot_x, self.vpn)
            self.vup = np.dot(rot_x, self.vup)

        # Rotação em torno do eixo Y
        if angle_y != 0:
            rot_y = rotation_matrix('y', angle_y)
            self.vpn = np.dot(rot_y, self.vpn)
            self.vup = np.dot(rot_y, self.vup)

        # Rotação em torno do eixo Z
        if angle_z != 0:
            rot_z = rotation_matrix('z', angle_z)
            self.vpn = np.dot(rot_z, self.vpn)
            self.vup = np.dot(rot_z, self.vup)

        # Normaliza os vetores
        self.vpn = self.vpn / np.linalg.norm(self.vpn)
        self.vup = self.vup / np.linalg.norm(self.vup)  

        self.update()

    def switch_lens_perspective(self):
        self.renderer.switch_focal_distance()
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

        if obj.get_type() == "3DObject" or obj.get_type() == "3DPoint":
            
            #print("Objeto 3D: ", obj)
            self.renderer.render_3d_object(obj)
            
        else:

            # objetos 2d não precisam de rotação por eixos diferentes do Z

            vertices = obj.get_vertices()

            aligned = self.align_z_axis(vertices)

            obj.set_scn_vertices(self.normalize(aligned))

    def align_z_axis(self, vertices):
            
            x_min, y_min = self.window_bounds[0]
            x_max, y_max = self.window_bounds[1]

            cx = (x_min + x_max) / 2
            cy = (y_min + y_max) / 2

            # faz a translação do mundo (nesse caso, 1 objeto) para o centro da window
            translated = [(x - cx, y - cy) for x, y in vertices]

            # o ângulo de rotação é o ângulo entre a VUP e o eixo Y do mundo
            vx, vy, vz = self.vup
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

    def normalize(self, vertices):
        x_min, y_min = self.window_bounds[0][:2]
        x_max, y_max = self.window_bounds[1][:2]

        window_width, window_height = x_max - x_min, y_max - y_min

        normalized_vertices = [
            ((x-x_min) / window_width, (y-y_min) / window_height)
            for x, y in vertices
        ]

        return normalized_vertices
    
    def update_all_scn(self):
        for obj in self.display_file.get_objects():
            self.update_specific_scn(obj)

    def update(self):
        self.renderer.recompute()
        self.update_all_scn()
        self._app.clip_objects()
        self.clear()
        self.draw()
        self.update_idletasks()
