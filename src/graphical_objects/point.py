from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Point(AbstractGraphicalObject):
    def __init__(self, name, coordinates: tuple[str, str]):
        super().__init__(name)
        self.coordinates = coordinates
        print(f"Point {name} created at {coordinates}")

    def get_object_center(self):
        return self.coordinates
    
    def get_vertices(self):
        return [self.coordinates]
    
    def get_type(self):
        return "Point"
    
    def modify(self, new_coords):
        self.coordinates = new_coords
        return self
    
    def draw(self, canvas):
        viewport_x, viewport_y = canvas.world_to_viewport(*self.coordinates)
        radius = 2
        canvas.create_oval(
            viewport_x - radius, viewport_y - radius,
            viewport_x + radius, viewport_y + radius,
            fill="black", outline=""
        )