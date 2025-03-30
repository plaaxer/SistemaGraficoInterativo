from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Point(AbstractGraphicalObject):
    def __init__(self, name, id, coordinates: list[tuple[int, int]], color: str):
        super().__init__(name, id, color)
        self.coordinates = coordinates
        print(f"Point {name} created at {coordinates}")
        print(f"point color: {color}")

    def get_object_center(self):
        return self.coordinates
    
    def get_vertices(self):
        return self.coordinates
    
    def get_type(self):
        return "Point"
    
    def modify(self, new_coords):
        self.coordinates = new_coords
        return self
    
    def draw(self, canvas):
        viewport_x, viewport_y = canvas.window_to_viewport(*self.coordinates[0])
        radius = 2
        canvas.create_oval(
            viewport_x - radius, viewport_y - radius,
            viewport_x + radius, viewport_y + radius,
            fill=self._color, outline=""
        )