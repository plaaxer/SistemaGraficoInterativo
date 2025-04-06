#arrumar o viewport
from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Line(AbstractGraphicalObject):
    def __init__(self, name, id, coordinates: list[tuple[int, int]], color: str):
        super().__init__(name, id, color)
        self.coordinates = coordinates
        print(f"Line {name} created at {coordinates}")

    def get_object_center(self):
        x_delta = self.coordinates[1][0] - self.coordinates[0][0]
        y_delta = self.coordinates[1][1] - self.coordinates[0][1]
        return (round(self.coordinates[0][0] + x_delta / 2), round(self.coordinates[0][1] + y_delta / 2))
    
    def get_vertices(self):
        return self.coordinates
    
    def get_type(self):
        return "Line"
    
    def modify(self, new_coords):
        self.coordinates = new_coords
        # todo: update scn vertices
        return self
    
    # scn refers to the normalized coordinates of the scene
    def draw(self, canvas):
        print("coordinates", self.coordinates)
        print("scn vertices", self._scn_vertices)
        viewport_x0, viewport_y0 = canvas.window_to_viewport(*self._scn_vertices[0])
        viewport_x1, viewport_y1 = canvas.window_to_viewport(*self._scn_vertices[1])
        Cviewport_x0, Cviewport_y0 = canvas.window_to_viewport(*self.coordinates[0])
        Cviewport_x1, Cviewport_y1 = canvas.window_to_viewport(*self.coordinates[1])
        print("Scn x0 y0", viewport_x0, viewport_y0)
        print("Scn x1 y1", viewport_x1, viewport_y1)
        print("C x0 y0", Cviewport_x0, Cviewport_y0)
        print("C x1 y1", Cviewport_x1, Cviewport_y1)
        canvas.create_line(
            viewport_x0, viewport_y0,
            viewport_x1, viewport_y1,
            fill=self._color
        )