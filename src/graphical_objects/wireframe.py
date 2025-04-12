#todo
from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Wireframe(AbstractGraphicalObject):
    def __init__(self, name, id, coordinates: list[tuple[str, str]], color: str, fill: bool):

        super().__init__(name, id, color)
        self.coordinates = coordinates
        self._fill = fill
        #print(f"Wireframe {name} created at {coordinates}")

    def get_object_center(self):
        x = sum([x for x, _ in self.coordinates]) / len(self.coordinates)
        y = sum([y for _, y in self.coordinates]) / len(self.coordinates)
        return (x, y)
    
    def get_vertices(self):
        return self.coordinates
    
    def get_type(self):
        return "Wireframe"
    
    def modify(self, new_coords):
        self.coordinates = new_coords
        return self
    
    def draw(self, canvas):

        viewport_coords = [
            canvas.window_to_viewport(*vertex)
            for vertex in self._scn_vertices
        ]

        if self._fill:

            flat_coords = [coord for pair in viewport_coords for coord in pair]
            canvas.create_polygon(
                flat_coords,
                fill=self._color,
                outline=self._color
            )
        else:

            for i in range(len(viewport_coords) - 1):
                x0, y0 = viewport_coords[i]
                x1, y1 = viewport_coords[i + 1]
                canvas.create_line(x0, y0, x1, y1, fill=self._color)

            x0, y0 = viewport_coords[-1]
            x1, y1 = viewport_coords[0]
            canvas.create_line(x0, y0, x1, y1, fill=self._color)
