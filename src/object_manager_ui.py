import tkinter as tk
import utils as ut
import constants as c

class ObjectManagerUI(tk.Frame):
    def __init__(self, parent, display_file, app, user_interface):
        super().__init__(parent, bg="gray")
        self._display_file = display_file
        self._display_file.subscribe(self)

        self._app = app

        self._user_interface = user_interface
        
        self.object_listbox = tk.Listbox(self, height=10, width=50)
        self.object_listbox.pack(pady=10)
        
        self.modify_button = tk.Button(self, text="Modify Selected", command=self.modify_selected_object)
        self.modify_button.pack(pady=5)
        
        self.delete_button = tk.Button(self, text="Delete Selected", command=self.delete_selected_object)
        self.delete_button.pack(pady=5)
    
    def update(self):
        self.object_listbox.delete(0, tk.END)
        #print("objects: ", self._display_file.get_objects_infos())
        for obj in self._display_file.get_objects_infos():
            self.object_listbox.insert(tk.END, obj)
    
    # consertar os dois métodos abaixo
    def delete_selected_object(self):
        id = self.get_object_id()
        if id is not None:
            self._app.delete_object(id)
            self.update()
        else:
            self._app.display_error("No object selected")

    def modify_selected_object(self):
        id = self.get_object_id()
        if id is not None:
            self.object_modifier_popup(id)
        else:
            self._app.display_error("No object selected")

    def get_object_id(self):
        selected_index = self.object_listbox.curselection()
        if selected_index:
            obj_info = self.object_listbox.get(selected_index)
            return ut.get_id_from_info(obj_info)
        return None

    def object_modifier_popup(self, obj_id):
        popup = tk.Toplevel(self)
        popup.title("Modify Object")
        popup.geometry(f"{c.POPUP_WIDTH}x{c.POPUP_HEIGHT}")

        self.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (c.POPUP_WIDTH // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (c.POPUP_HEIGHT // 2)
        popup.geometry(f"+{x}+{y - c.POPUP_Y_OFFSET}")

        tk.Label(popup, text="Select Modification Type:").pack(pady=5)
        
        mode_var = tk.StringVar(value="translate")
        
        translate_radio = tk.Radiobutton(popup, text="Translate", variable=mode_var, value="translate")
        escalate_radio = tk.Radiobutton(popup, text="Escalate", variable=mode_var, value="escalate")
        rotate_radio = tk.Radiobutton(popup, text="Rotate", variable=mode_var, value="rotate")
        translate_radio.pack()
        escalate_radio.pack()
        rotate_radio.pack()

        input_frame = tk.Frame(popup)
        input_frame.pack(pady=10)
        
        def update_input_fields():
            for widget in input_frame.winfo_children():
                widget.destroy()
            
            if mode_var.get() == "translate":
                tk.Label(input_frame, text="Enter Shift:").pack()
                coord_entry = tk.Entry(input_frame, width=50)
                coord_entry.pack()
                input_frame.coord_entry = coord_entry
            elif mode_var.get() == "escalate":
                tk.Label(input_frame, text="Enter Scaling Factor:").pack()
                factor_entry = tk.Entry(input_frame, width=10)
                factor_entry.pack()
                input_frame.factor_entry = factor_entry
            else:
                tk.Label(input_frame, text="Enter Angle:").pack()
                angle_entry = tk.Entry(input_frame, width=10)
                angle_entry.pack()
                input_frame.angle_entry = angle_entry
                tk.Label(input_frame, text="Select Rotation Point:").pack(pady=5)
                rotation_point_var = tk.StringVar(value="center")

                center_radio = tk.Radiobutton(input_frame, text="Object Center", variable=rotation_point_var, value="center")
                custom_radio = tk.Radiobutton(input_frame, text="Custom Point", variable=rotation_point_var, value="custom")
                center_radio.pack()
                custom_radio.pack()

                def update_rotation_point_fields():
                    for widget in input_frame.winfo_children():
                        if isinstance(widget, tk.Entry) and widget != angle_entry:
                            widget.destroy()
                    
                    if rotation_point_var.get() == "custom":
                        tk.Label(input_frame, text="Enter Rotation Point (x, y):").pack()
                        point_entry = tk.Entry(input_frame, width=50)
                        point_entry.pack()
                        input_frame.point_entry = point_entry

                rotation_point_var.trace_add("write", lambda *args: update_rotation_point_fields())
                update_rotation_point_fields()
        
        mode_var.trace_add("write", lambda *args: update_input_fields())
        update_input_fields()
        
        def modify_object():
            if mode_var.get() == "translate":
                coords = getattr(input_frame, "coord_entry", None)
                if coords:
                    self._app.modify_object(obj_id, "translate", coords.get())
            elif mode_var.get() == "escalate":
                factor = getattr(input_frame, "factor_entry", None)
                if factor:
                    self._app.modify_object(obj_id, "escalate", factor.get())
            else:
                angle = getattr(input_frame, "angle_entry", None)
                if angle:
                    point = getattr(input_frame, "point_entry", None)
                    if point:
                        self._app.modify_object(obj_id, "rotate", angle.get(), point.get())
                    else:
                        self._app.modify_object(obj_id, "rotate", angle.get())
            popup.destroy()
        
        tk.Button(popup, text="Apply", command=modify_object).pack(pady=10)