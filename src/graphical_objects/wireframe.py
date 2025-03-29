#todo
from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Wireframe(AbstractGraphicalObject):
    def __init__(self, name, id, coordinates: list[tuple[str, str]], color: str):
        super().__init__(name, id, color)
        self.coordinates = coordinates
        print(f"Wireframe {name} created at {coordinates}")

    def get_object_center(self):
        x = sum([x for x, _ in self.coordinates]) / len(self.coordinates)
        y = sum([y for _, y in self.coordinates]) / len(self.coordinates)
        return (x, y)
    
    def get_vertices(self):
        return [self.coordinates]
    
    def get_type(self):
        return "Wireframe"
    
    def modify(self, new_coords):
        self.coordinates = new_coords
        return self
    
    def draw(self, canvas):
        for i in range(len(self.coordinates) - 1):
            viewport_x0, viewport_y0 = canvas.window_to_viewport(*self.coordinates[i])
            viewport_x1, viewport_y1 = canvas.window_to_viewport(*self.coordinates[i + 1])
            canvas.create_line(
                viewport_x0, viewport_y0,
                viewport_x1, viewport_y1,
                fill=self._color
            )
        viewport_x0, viewport_y0 = canvas.window_to_viewport(*self.coordinates[-1])
        viewport_x1, viewport_y1 = canvas.window_to_viewport(*self.coordinates[0])
        canvas.create_line(
            viewport_x0, viewport_y0,
            viewport_x1, viewport_y1,
            fill=self._color
        )