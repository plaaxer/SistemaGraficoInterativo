import tkinter as tk
import constants as c
from object_manager_ui import ObjectManagerUI
from file_loader import FileLoader
from PIL import Image, ImageTk

class UserInterface(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.title("Interactive Graphics System")
        self.geometry(c.APPLICATION_SIZE)
        
        self.configure(bg=c.UI_BACKGROUND_COLOR)
        
        self.command_panel = tk.Frame(self, width=c.APPLICATION_WIDTH-c.VIEWPORT_WIDTH, height=c.APPLICATION_HEIGHT, bg="gray")
        self.command_panel.pack(side=tk.LEFT)
        self.command_panel.pack_propagate(False)

        self.setup()
    
    def run(self):
        self.mainloop()

    def setup(self):

        self.logger_box = tk.Text(self.command_panel, height=15, width=60, state=tk.DISABLED)
        self.logger_box.pack(pady=10)

        self.create_buttons()
        
    def set_viewport(self, viewport):
        self.viewport = viewport
        self.display_file = viewport.display_file
        self.viewport.place(relx=1.0, rely=0.0, anchor="ne")
        self.viewport.draw()

        self.object_manager = ObjectManagerUI(self.command_panel, self.viewport.display_file, self._app, self)
        self.object_manager.pack(pady=10)

    def create_buttons(self):

        tk.Button(self.command_panel, command=self.create_object_creator_popup, text="Create Object").pack(pady=20)

        rotate_button = tk.Button(self.command_panel, command=self.rotate_window, text="Rotate")
        # rotate_photo = FileLoader.load_image(c.ROTATE_ICON_PATH)
        # rotate_button.config(image=rotate_photo)
        # rotate_button.image = rotate_photo
        # rotate_button.config(text="Rotate window")
        rotate_button.pack(pady=10)

        move_frame = tk.Frame(self.command_panel, bg="gray")
        move_frame.pack(pady=10)
        
        tk.Button(move_frame, command=self.move_up, text="Move up").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(move_frame, command=self.move_left, text="Move left").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(move_frame, command=self.move_right, text="Move right").grid(row=1, column=2, padx=5, pady=5)
        tk.Button(move_frame, command=self.move_down, text="Move down").grid(row=2, column=1, padx=5, pady=5)
        
        zoom_frame = tk.Frame(self.command_panel, bg="gray")
        zoom_frame.pack(pady=10)
        
        tk.Button(zoom_frame, command=self.zoom_in, text="Zoom in").pack(side=tk.LEFT, padx=5)
        tk.Button(zoom_frame, command=self.zoom_out, text="Zoom out").pack(side=tk.LEFT, padx=5)

        import_button = tk.Button(self, text="Import OBJ", command=self._app.import_object)
        export_button = tk.Button(self, text="Export OBJ", command=self._app.export_object)

        import_button.place(relx=1.0, rely=1.0, anchor="se", x=-140, y=-10)
        export_button.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-10)

    
    def create_object_creator_popup(self):

        popup = tk.Toplevel(self)
        popup.title("Create Object")
        popup.geometry(f"{c.POPUP_WIDTH}x{c.POPUP_HEIGHT}")

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (c.POPUP_WIDTH // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (c.POPUP_HEIGHT// 2)
        popup.geometry(f"+{x}+{y-c.POPUP_Y_OFFSET}")

        tk.Label(popup, text="Select Object Type:").pack(pady=5)
        obj_type_var = tk.StringVar(popup)
        obj_type_var.set(c.DEFAULT_SELECTED_OBJECT)
        obj_types = c.POSSIBLE_OBJECTS
        obj_menu = tk.OptionMenu(popup, obj_type_var, *obj_types)
        obj_menu.pack(pady=5)

        tk.Label(popup, text="Enter Coordinates:").pack(pady=5)
        coord_entry = tk.Entry(popup, width=50)
        coord_entry.pack(pady=5)

        color_name_frame = tk.Frame(popup)
        color_name_frame.pack(pady=5, anchor="center", padx=10)

        tk.Label(color_name_frame, text="Color (optional):").grid(row=0, column=0, padx=5)
        color_entry = tk.Entry(color_name_frame, width=15)
        color_entry.grid(row=0, column=1, padx=5)

        tk.Label(color_name_frame, text="Name (optional):").grid(row=0, column=2, padx=5)
        name_entry = tk.Entry(color_name_frame, width=15)
        name_entry.grid(row=0, column=3, padx=5)



        def create_object():
            obj_type = obj_type_var.get()
            coords = coord_entry.get()
            color = color_entry.get()
            name = name_entry.get()
            self._app.create_object(obj_type, coords, name, color)
            popup.destroy()

        tk.Button(popup, text="Create", command=create_object).pack(pady=10)
    
    def log_message(self, message):
        self.logger_box.config(state=tk.NORMAL)
        self.logger_box.insert(tk.END, message + "\n")
        self.logger_box.config(state=tk.DISABLED)
        self.logger_box.yview(tk.END)

    def display_error(self, message):

        error_popup = tk.Toplevel(self)
        error_popup.title("Error")
        error_popup.geometry(f"{c.POPUP_WIDTH}x{c.POPUP_HEIGHT}")

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (c.POPUP_WIDTH // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (c.POPUP_HEIGHT // 2)
        error_popup.geometry(f"+{x}+{y-c.POPUP_Y_OFFSET}")

        tk.Label(error_popup, text="Error!", font=("Arial", 14, "bold"), fg="red").pack(pady=5)
        tk.Label(error_popup, text=message, wraplength=250, justify="center").pack(pady=5)

        tk.Button(error_popup, text="OK", command=error_popup.destroy).pack(pady=10)
    
    def display_info(self, message):

        info_popup = tk.Toplevel(self)
        info_popup.title("Info")
        info_popup.geometry(f"{c.POPUP_WIDTH}x{c.POPUP_HEIGHT}")

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (c.POPUP_WIDTH // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (c.POPUP_HEIGHT // 2)
        info_popup.geometry(f"+{x}+{y-c.POPUP_Y_OFFSET}")

        tk.Label(info_popup, text="Information", font=("Arial", 14, "bold"), fg="blue").pack(pady=5)
        tk.Label(info_popup, text=message, wraplength=250, justify="center").pack(pady=5)

        tk.Button(info_popup, text="OK", command=info_popup.destroy).pack(pady=10)
        self.log_message(f"Info: {message}")

    def move_up(self):
        self._app.create_object("Line", "((0, 0), (1920, 0))", "debugWorldAxisX", "red")
        self._app.create_object("Line", "((0, 0), (0, 1080))", "debugWorldAxisY", "blue")
        self._app.create_object("Line", "(480, 270), (480, 810)", "debugWorldCenterX", "red")
        self._app.create_object("Line", "(480, 270), (1440, 270)", "debugWorldCenterY", "blue")
        self._app.create_object("Wireframe", "(50, 50), (1500, 50), (1500, 800)", "debugWireframe", "green")
        step = 20
        self.viewport.translate_window(0, -step)
        self.viewport.update()
        self.log_message(f"Moved up by {step} pixels")
    
    def move_down(self):
        step = 20
        self.viewport.translate_window(0, step)
        self.viewport.update()
        self.log_message(f"Moved down by {step} pixels")
    
    def move_left(self):
        step = 20
        self.viewport.translate_window(-step, 0)
        self.viewport.update()
        self.log_message(f"Moved left by {step} pixels")
    
    def move_right(self):
        step = 20
        self.viewport.translate_window(step, 0)
        self.viewport.update()
        self.log_message(f"Moved right by {step} pixels")
    
    def zoom_in(self):
        factor = 0.85
        self.viewport.zoom(factor)
        self.viewport.update()
        self.log_message("Zoomed in (factor: 0.85)")
    
    def zoom_out(self):
        factor = 1.15
        self.viewport.zoom(factor)
        self.viewport.update()
        self.log_message("Zoomed out (factor: 1.15)")
    
    def rotate_window(self):
        self.viewport.rotate_window(-30)
        self.log_message("Rotated window 30 degrees counterclockwise")