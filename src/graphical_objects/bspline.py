from graphical_objects.wireframe import Wireframe

class BSplineCurve(Wireframe):
    def __init__(self, name, id, points: list[tuple[str, str]], color: str, fill: bool):

        print(f"BSplineSurface {name} created at {points}")
        self.create_bspline_surface(points)
        super().__init__(name, id, self.curve_coordinates, color, fill)

    def create_bspline_surface(self, points):
        curves = []

        m = len(points)
        for i in range(m - 3):
            n = len(points[i])
            for j in range(n - 3):
                controls = [
                        points[i][j], points[i][j+1], points[i][j+2], points[i][j+3],
                        points[i+1][j], points[i+1][j+1], points[i+1][j+2], points[i+1][j+3],
                        points[i+2][j], points[i+2][j+1], points[i+2][j+2], points[i+2][j+3],
                        points[i+3][j], points[i+3][j+1], points[i+3][j+2], points[i+3][j+3],
                    ]
                lines = bSplineSurface(controls, step)
                curves.extend([Linestring(line) for line in lines])

            self.curve_coordinates = curves
        
        