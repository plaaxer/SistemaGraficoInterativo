import tkinter as tk
import constants as c

class UserInterface(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.title("Interactive Graphics System")
        self.geometry(c.APPLICATION_SIZE)
        
        self.configure(bg=c.UI_BACKGROUND_COLOR)
        
        self.control_panel = tk.Frame(self, width=c.APPLICATION_WIDTH-c.VIEWPORT_WIDTH, height=c.APPLICATION_HEIGHT, bg="gray")
        self.control_panel.pack(side=tk.LEFT)
        self.control_panel.pack_propagate(False)

        self.logger_box = tk.Text(self.control_panel, height=15, width=60, state=tk.DISABLED)
        self.logger_box.pack(pady=10)

        self.setup()
    
    def run(self):
        self.mainloop()

    def setup(self):
        self.create_buttons()
        
    def set_viewport(self, viewport):
        self.viewport = viewport
        self.display_file = viewport.display_file
        self.viewport.place(relx=1.0, rely=0.0, anchor="ne")
        self.viewport.draw()

    def create_buttons(self):
        tk.Button(self.control_panel, command=self.create_object_creator_popup, text="Create Object").pack(pady=20)
        tk.Button(self.control_panel, command=self.move_up, text="Move up").pack(pady=10)
        tk.Button(self.control_panel, command=self.move_down, text="Move down").pack(pady=10)
        tk.Button(self.control_panel, command=self.move_left, text="Move left").pack(pady=10)
        tk.Button(self.control_panel, command=self.move_right, text="Move right").pack(pady=10)
        tk.Button(self.control_panel, command=self.zoom_in, text="Zoom in").pack(pady=10)
        tk.Button(self.control_panel, command=self.zoom_out, text="Zoom out").pack(pady=10)
    
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

        def create_object():
            obj_type = obj_type_var.get()
            coords = coord_entry.get()
            self._app.create_object(obj_type, coords)
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
        self.viewport.translate_window(0, 10)
        self.viewport.update()
        self.log_message("Viewport translated 10 units up")
    
    def move_down(self):
        self.viewport.translate_window(0, -10)
        self.viewport.update()
        self.log_message("Viewport translated 10 units down")
    
    def move_left(self):
        self.viewport.translate_window(-10, 0)
        self.viewport.update()
        self.log_message("Viewport translated 10 units left")
    
    def move_right(self):
        self.viewport.translate_window(10, 0)
        self.viewport.update()
        self.log_message("Viewport translated 10 units right")
    
    def zoom_in(self):
        self.viewport.zoom(1.1)
        self.viewport.update()
        self.log_message("Viewport zoomed in")
    
    def zoom_out(self):
        self.viewport.zoom(0.9)
        self.viewport.update()
        self.log_message("Viewport zoomed out")