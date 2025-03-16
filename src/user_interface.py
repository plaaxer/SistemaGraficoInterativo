import tkinter as tk
import constants as c

class UserInterface(tk.Tk):
    def __init__(self, app):
        super().__init__()
        self._app = app
        self.title("Interactive Graphics System")
        self.geometry(c.APPLICATION_SIZE)
        
        self.control_panel = tk.Frame(self, width=600, height=600, bg="lightgray")
        self.control_panel.pack(side="left", fill="y")

        self.setup()
    
    def run(self):
        self.mainloop()

    def setup(self):
        self.create_buttons()
        
    def set_viewport(self, viewport):
        self.viewport = viewport
        self.viewport.pack(side="right", fill="both", expand=True)
        self.viewport.draw()

    def create_buttons(self):
        tk.Button(self.control_panel, command=self.create_object_creator_popup, text="Create Object").pack(pady=20)
    
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
