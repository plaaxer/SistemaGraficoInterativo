#arrumar o viewport
from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Line(AbstractGraphicalObject):
    def __init__(self, name, coordinates: list[tuple[str, str]]):
        super().__init__(name)
        self.coordinates = coordinates
        print(f"Line {name} created at {coordinates}")

    def get_object_center(self):
        return self.coordinates
    
    def get_vertices(self):
        return [self.coordinates]
    
    def get_type(self):
        return "Line"
    
    def modify(self, new_coords):
        self.coordinates = new_coords
        return self
    
    def draw(self, canvas):
        viewport_x0, viewport_y0 = canvas.world_to_viewport(*self.coordinates[0])
        viewport_x1, viewport_y1 = canvas.world_to_viewport(*self.coordinates[1])
        canvas.create_line(
            viewport_x0, viewport_y0,
            viewport_x1, viewport_y1,
            fill="black"
        )