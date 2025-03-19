from tkinter import Canvas
from display_file import DisplayFile

class Viewport(Canvas):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.display_file = DisplayFile()

        # coordenadas da janela de visualização
        self.window_x = 0
        self.window_y = 0

        # coordenadas do mundo
        self.world_bounds = (0, 0), (1920, 1080)

        # estabeleci o tamanho do mundo como 1920x1080. A window tem o mesmo tamanho que o canvas/viewport

    def draw(self):
        for obj in self.display_file.get_objects():
            obj.draw(self)
    
    def world_to_viewport(self, x, y):

        viewport_width = self.winfo_width()
        viewport_height = self.winfo_height()
        
        print(f"Viewport width: {viewport_width}, height: {viewport_height}")

        world_x_min, world_y_min = self.world_bounds[0]
        world_x_max, world_y_max = self.world_bounds[1]

        viewport_x = ((x - world_x_min) / (world_x_max - world_x_min)) * viewport_width
        viewport_y = (1 - (y - world_y_min) / (world_y_max - world_y_min)) * viewport_height

        print("viewport_x: ", viewport_x, "viewport_y: ", viewport_y)

        return viewport_x, viewport_y


    def clear(self):
        self.delete("all")
    
    def update(self):
        self.clear()
        self.draw()
        self.update_idletasks()