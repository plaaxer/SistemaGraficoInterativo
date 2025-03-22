from tkinter import Canvas
from display_file import DisplayFile
import constants as c

class Viewport(Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.display_file = DisplayFile()

        # coordenadas da janela
        self.window_bounds = c.WINDOW_BOUNDS

    def draw(self):
        for obj in self.display_file.get_objects():
            obj.draw(self)
    
    def window_to_viewport(self, x, y):
        
        # dimensão da viewport
        self.viewport_width = self.winfo_width()
        self.viewport_height = self.winfo_height()

        print(f"Viewport width: {self.viewport_width}, height: {self.viewport_height}")

        window_x_min, window_y_min = self.window_bounds[0]
        window_x_max, window_y_max = self.window_bounds[1]

        viewport_x = ((x - window_x_min) / (window_x_max - window_x_min)) * self.viewport_width
        viewport_y = (1 - (y - window_y_min) / (window_y_max - window_y_min)) * self.viewport_height

        print("viewport_x: ", viewport_x, "viewport_y: ", viewport_y)

        return viewport_x, viewport_y
    
    def translate_window(self, x, y):
        # lembrando que é o inverso
        self.window_bounds[0] = (self.window_bounds[0][0] - x, self.window_bounds[0][1] - y)
        self.window_bounds[1] = (self.window_bounds[1][0] - x, self.window_bounds[1][1] - y)
    
    def zoom(self, factor):

        self.window_bounds[0] = (self.window_bounds[0][0] * factor, self.window_bounds[0][1] * factor)
        self.window_bounds[1] = (self.window_bounds[1][0] * factor, self.window_bounds[1][1] * factor)

    def clear(self):
        self.delete("all")
    
    def update(self):
        self.clear()
        self.draw()
        self.update_idletasks()