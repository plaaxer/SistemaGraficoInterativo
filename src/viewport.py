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
        self.vrp = c.VIEW_REFERENCE_POINT
        self.vpn = c.VIEW_PLANE_NORMAL
        self.margin = 0.05  # margem da janela de clipping

        self.window_angle = 0

    def draw(self):
        for obj in self.display_file.get_objects():
            #if obj.in_window:  # Desenha apenas objetos visíveis
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
    
    def translate_window(self, dwx, dwy, dwz):

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


    def rotate_window(self, angle_x=0, angle_y=0, angle_z=0):
        """
        Rotaciona a window em torno dos eixos X, Y e Z.
        """
        print("Requested rotation:", angle_x, angle_y, angle_z)

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

        if obj._type == "3DObject" or obj._type == "3DPoint" or len(obj.get_vertices()) == 8:
            segments = []
            for segment in obj.segments:
                # 1. Translada VRP para a origem
                vrp = self.vrp
                translated_vertices = [
                    (x - vrp[0], y - vrp[1], z - vrp[2]) for x, y, z in segment
                ]

                # 2. Determina VPN e seus ângulos com X e Y
                vpn = self.vpn / np.linalg.norm(self.vpn)  # Normaliza VPN
                theta_x = np.arctan2(vpn[1], vpn[2])  # Ângulo com o eixo X
                theta_y = np.arctan2(vpn[0], vpn[2])  # Ângulo com o eixo Y

                # 3. Rotaciona o mundo em torno de X e Y para alinhar VPN com o eixo Z
                # Rotação em torno de X
                cos_theta_x, sin_theta_x = np.cos(-theta_x), np.sin(-theta_x)
                rotation_x = np.array([
                    [1, 0, 0],
                    [0, cos_theta_x, -sin_theta_x],
                    [0, sin_theta_x, cos_theta_x]
                ])
                rotated_vertices = [np.dot(rotation_x, v) for v in translated_vertices]

                # Rotação em torno de Y
                cos_theta_y, sin_theta_y = np.cos(-theta_y), np.sin(-theta_y)
                rotation_y = np.array([
                    [cos_theta_y, 0, sin_theta_y],
                    [0, 1, 0],
                    [-sin_theta_y, 0, cos_theta_y]
                ])
                rotated_vertices = [np.dot(rotation_y, v) for v in rotated_vertices]

                # 4. Ignora as coordenadas Z dos objetos
                projected_vertices = [(x, y) for x, y, z in rotated_vertices]
                # 5. Normaliza as coordenadas restantes
                x_min, y_min = self.window_bounds[0][:2]
                x_max, y_max = self.window_bounds[1][:2]
                #cx, cy = (x_min + x_max) / 2, (y_min + y_max) / 2
                window_width, window_height = x_max - x_min, y_max - y_min

                normalized_vertices = [
                    ((x - x_min) / window_width, (y - y_min) / window_height)
                    for x, y in projected_vertices
                ]
                # 6. Aplica o clipping
                '''
                clipped_vertices = []
                for x, y in normalized_vertices:
                    if 0 + self.margin <= x <= 1 - self.margin and 0 + self.margin <= y <= 1 - self.margin:
                        clipped_vertices.append((x, y))
                '''
                clipped_vertices = normalized_vertices
                # 7. Transforma para coordenadas da viewport
                
                segments.append(clipped_vertices)
            obj.set_normalized_segments(segments)
            obj.in_window = True
            
        
        else:
            vertices = obj.get_vertices()
            # localização da window
            x_min, y_min = self.window_bounds[0]
            x_max, y_max = self.window_bounds[1]

            # computa o centro da window
            cx = (x_min + x_max) / 2
            cy = (y_min + y_max) / 2

            # tamanho da window
            window_width = x_max - x_min
            window_height = y_max - y_min

            print("vertices in specific scn size: ", len(vertices))
            print(vertices)    
            # faz a translação do mundo (nesse caso, 1 objeto) para o centro da window
            translated = [(x - cx, y - cy) for x, y in vertices]

            print("translated size: ", len(translated))

            # o ângulo de rotação é o ângulo entre a VUP e o eixo Y do mundo
            vx = self.vup[0]
            vy = self.vup[1]
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

    
    def update_all_scn(self):
        for obj in self.display_file.get_objects():
            self.update_specific_scn(obj)

    def update(self):
        self.update_all_scn()
        self._app.clip_objects()
        self.clear()
        self.draw()
        self.update_idletasks()
