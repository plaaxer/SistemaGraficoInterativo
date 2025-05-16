from graphical_objects.abstract_graphical_object import AbstractGraphicalObject
from graphical_objects.point import Point
from graphical_objects.line import Line
from graphical_objects.wireframe import Wireframe
from graphical_objects.objeto3d import Object3D
from viewport import Viewport
import copy
import numpy as np

class Clipper:
    def __init__(self):
        self.margin = 0.05
        self.selected_algorithm = 1

    def clip(self, display_file, window):
        for obj in display_file:
            if isinstance(obj, Point):
                obj.get_scn_vertices()
                self.clip_point(obj)

            elif isinstance(obj, Object3D):
                self.clip_object3d(obj, window)

            elif isinstance(obj, Line):
                vertices = obj.get_scn_vertices()
                self.clip_line1(obj) if self.selected_algorithm == 1 else self.clip_line_2(obj)

            elif isinstance(obj, Wireframe):
                vertices = obj.get_scn_vertices()
                self.clip_wireframe(obj, window)

        
    def clip_point(self, point):
        if ((point.get_scn_vertices()[0][0] <= 1-self.margin) and (point.get_scn_vertices()[0][0] >= -1+self.margin)) and ((point.get_scn_vertices()[0][1] <= 1-self.margin) and (point.get_scn_vertices()[0][1] >= -1+self.margin)):
            point.in_window = True
        else:
            point.in_window = False
        
    ###################################################################################################
    #COHEN-SUTHERLAND
    def clip_line1(self, line):
        x_min = y_min = -1 + self.margin
        x_max = y_max = 1 - self.margin
        x1, y1 = line.get_scn_vertices()[0]
        x2, y2 = line.get_scn_vertices()[1]
        code1 = self.compute_cohen_sutherland_code(x1, y1, x_min, x_max, y_min, y_max)
        code2 = self.compute_cohen_sutherland_code(x2, y2, x_min, x_max, y_min, y_max)
        ##print(f"Line: {line.get_id()}, Code1: {code1}, Code2: {code2}")

        accept = False
        while True:
            if code1 == 0 and code2 == 0:
                accept = True
                break
            elif code1 & code2 != 0:
                break
            else:
                x, y = 0, 0
                code_out = code1 if code1 != 0 else code2
                if x2 == x1:
                    m = float('inf')
                else:
                    m = (y2 - y1) / (x2 - x1)

                if code_out & 8:
                    x = x1 + (1 / m) * (y_max - y1) if m != float('inf') else x1
                    y = y_max
                elif code_out & 4:
                    x = x1 + (1 / m) * (y_min - y1) if m != float('inf') else x1
                    y = y_min
                elif code_out & 2:
                    y = m * (x_max - x1) + y1 if m != float('inf') else y1
                    x = x_max
                elif code_out & 1:
                    y = m * (x_min - x1) + y1 if m != float('inf') else y1
                    x = x_min

                if code_out == code1:
                    x1, y1 = x, y
                    code1 = self.compute_cohen_sutherland_code(x1, y1, x_min, x_max, y_min, y_max)
                else:
                    x2, y2 = x, y
                    code2 = self.compute_cohen_sutherland_code(x2, y2, x_min, x_max, y_min, y_max)

        if accept:
            ##print(f"Line {line.get_id()} accepted: ({x1}, {y1}) -> ({x2}, {y2})")
            line.set_scn_vertices([(x1, y1), (x2, y2)])
            line.in_window = True
        else:
            ##print(f"Line {line.get_id()} rejected")
            line.in_window = False

    def compute_cohen_sutherland_code(self, x, y, x_min, x_max, y_min, y_max):
        code = 0
        if x < x_min:
            code |= 1
        elif x > x_max:
            code |= 2
        if y < y_min:
            code |= 4
        elif y > y_max:
            code |= 8
        return code

    ###################################################################################################

    #LIANG-BARSKY
    def clip_line_2(self, line):
        line.in_window = False
        x_min = y_min = -1 + self.margin
        x_max = y_max = 1 - self.margin
        x1, y1 = line.get_scn_vertices()[0]
        x2, y2 = line.get_scn_vertices()[1]
        dx, dy = x2 - x1, y2 - y1
        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        u1, u2 = 0, 1

        if x_min < x1 < x_max and y_min < y1 < y_max and x_min < x2 < x_max and y_min < y2 < y_max:
            line.in_window = True
            return

        for i in range(4):
            if p[i] == 0:
                if q[i] < 0:
                    break                    
            else:
                r = q[i] / p[i]
                if p[i] < 0:
                    u1 = max(u1, r)
                else:
                    u2 = min(u2, r)
        
        if u1 > u2:  # Reject the line if u1 > u2
            return
        
        # Apply Liang-Barsky clipping
        x1_clip = x1 + u1 * dx
        y1_clip = y1 + u1 * dy
        x2_clip = x1 + u2 * dx
        y2_clip = y1 + u2 * dy
        
        scn_vertices = [(x1_clip, y1_clip), (x2_clip, y2_clip)]
        line.set_scn_vertices(scn_vertices)
        line.in_window = True
###################################################################################################

    #SUTHERLAND-HODGMAN
    def clip_wireframe(self, wireframe, window):
        # Inicializa o wireframe como fora da janela
        wireframe.in_window = False
        wireframe.clipped_points = []

        # Define os limites da janela de clipping
        x_min = y_min = -1 + self.margin
        x_max = y_max = 1 - self.margin
        clipper_polygon = [(x_min, y_min), (x_min, y_max), (x_max, y_max), (x_max, y_min)]

        # Obtém os vértices normalizados do wireframe
        polygon_points = wireframe.get_scn_vertices()

        # Aplica o algoritmo de Sutherland-Hodgman para cada aresta do clipper
        for i in range(len(clipper_polygon)):
            k = (i + 1) % len(clipper_polygon)
            edge_start = clipper_polygon[i]
            edge_end = clipper_polygon[k]
            polygon_points = self.compute_sutherland_hodgman_polygon_clip(
                polygon_points, edge_start, edge_end
            )

        # Verifica se o wireframe está visível após o clipping
        if polygon_points:
            wireframe.in_window = True
            wireframe.set_scn_vertices(polygon_points)  # Atualiza os vértices clipados

    # Function to return x-value of point of intersection of two lines
    def x_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        num = (x1*y2 - y1*x2) * (x3-x4) - (x1-x2) * (x3*y4 - y3*x4)
        den = (x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)
        return num/den

    # Function to return y-value of point of intersection of two lines
    def y_intersect(self, x1, y1, x2, y2, x3, y3, x4, y4):
        num = (x1*y2 - y1*x2) * (y3-y4) - (y1-y2) * (x3*y4 - y3*x4)
        den = (x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)
        return num/den
    
    def compute_sutherland_hodgman_polygon_clip(self, polygon_points, edge_start, edge_end):
        new_polygon_points = []
        
        # No points to clip
        if not polygon_points:
            return []
            
        for i in range(len(polygon_points)):
            k = (i+1) % len(polygon_points)
            current_point = polygon_points[i]
            next_point = polygon_points[k]
            
            ix, iy = current_point
            kx, ky = next_point
            
            # Calculate if points are inside or outside the clipping edge
            # We use the cross product to determine which side of the line the points are on
            i_pos = (edge_end[0]-edge_start[0]) * (iy-edge_start[1]) - (edge_end[1]-edge_start[1]) * (ix-edge_start[0])
            k_pos = (edge_end[0]-edge_start[0]) * (ky-edge_start[1]) - (edge_end[1]-edge_start[1]) * (kx-edge_start[0])
            
            # Case 1: Both points inside - add the next point
            if i_pos < 0 and k_pos < 0:
                new_polygon_points.append(next_point)
                
            # Case 2: Current point outside, next point inside - add intersection and next point
            elif i_pos >= 0 and k_pos < 0:
                intersection_x = self.x_intersect(edge_start[0], edge_start[1], edge_end[0], edge_end[1], ix, iy, kx, ky)
                intersection_y = self.y_intersect(edge_start[0], edge_start[1], edge_end[0], edge_end[1], ix, iy, kx, ky)
                new_polygon_points.append((intersection_x, intersection_y))
                new_polygon_points.append(next_point)
                
            # Case 3: Current point inside, next point outside - add only intersection
            elif i_pos < 0 and k_pos >= 0:
                intersection_x = self.x_intersect(edge_start[0], edge_start[1], edge_end[0], edge_end[1], ix, iy, kx, ky)
                intersection_y = self.y_intersect(edge_start[0], edge_start[1], edge_end[0], edge_end[1], ix, iy, kx, ky)
                new_polygon_points.append((intersection_x, intersection_y))
                
            # Case 4: Both points outside - add nothing

        lastone = new_polygon_points.pop()
        new_polygon_points.insert(0, lastone)

        return new_polygon_points
    
    def clip_object3d(self, object3d, window):

        segments = object3d.get_normalized_segments()
        for i in range(len(segments)):
            ##print(object3d.in_window)
            object3d.in_window[i] = False
            x_min = y_min = -1 + self.margin
            x_max = y_max = 1 - self.margin
            x1, y1 = segments[i][0]
            x2, y2 = segments[i][1]
            code1 = self.compute_cohen_sutherland_code(x1, y1, x_min, x_max, y_min, y_max)
            code2 = self.compute_cohen_sutherland_code(x2, y2, x_min, x_max, y_min, y_max)

            accept = False
            while True:
                if code1 == 0 and code2 == 0:
                    accept = True
                    break
                elif code1 & code2 != 0:
                    break
                else:
                    x, y = 0, 0
                    code_out = code1 if code1 != 0 else code2
                    if x2 == x1:
                        m = float('inf')
                    else:
                        m = (y2 - y1) / (x2 - x1)

                    if code_out & 8:
                        x = x1 + (1 / m) * (y_max - y1) if m != float('inf') else x1
                        y = y_max
                    elif code_out & 4:
                        x = x1 + (1 / m) * (y_min - y1) if m != float('inf') else x1
                        y = y_min
                    elif code_out & 2:
                        y = m * (x_max - x1) + y1 if m != float('inf') else y1
                        x = x_max
                    elif code_out & 1:
                        y = m * (x_min - x1) + y1 if m != float('inf') else y1
                        x = x_min

                    if code_out == code1:
                        x1, y1 = x, y
                        code1 = self.compute_cohen_sutherland_code(x1, y1, x_min, x_max, y_min, y_max)
                    else:
                        x2, y2 = x, y
                        code2 = self.compute_cohen_sutherland_code(x2, y2, x_min, x_max, y_min, y_max)

            if accept:
                print(f"Line {i} accepted: ({x1:.3f}, {y1:.3f}) -> ({x2:.3f}, {y2:.3f})")
                segments[i] = [(x1, y1), (x2, y2)]
                object3d.in_window[i] = True
            else:
                print(f"Line {i} rejected: ({x1:.3f}, {y1:.3f}) -> ({x2:.3f}, {y2:.3f})")
                object3d.in_window[i] = False