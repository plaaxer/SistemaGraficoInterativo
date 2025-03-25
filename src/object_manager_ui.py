import tkinter as tk
import utils as ut

# TODO (para a outra entrega)

class ObjectManagerUI(tk.Frame):
    def __init__(self, parent, display_file, app):
        super().__init__(parent, bg="gray")
        self._display_file = display_file
        self._display_file.subscribe(self)

        self._app = app
        
        self.object_listbox = tk.Listbox(self, height=10, width=50)
        self.object_listbox.pack(pady=10)
        
        self.modify_button = tk.Button(self, text="Modify Selected", command=self.modify_selected_object)
        self.modify_button.pack(pady=5)
        
        self.delete_button = tk.Button(self, text="Delete Selected", command=self.delete_selected_object)
        self.delete_button.pack(pady=5)
    
    def update(self):
        self.object_listbox.delete(0, tk.END)
        print("objects: ", self._display_file.get_objects_infos())
        for obj in self._display_file.get_objects_infos():
            self.object_listbox.insert(tk.END, obj)
    
    # consertar os dois métodos abaixo
    def delete_selected_object(self):
        selected_index = self.object_listbox.curselection()
        if selected_index:
            obj_info = self.object_listbox.get(selected_index)
            obj_id = ut.get_id_from_info(obj_info)
            self._app.delete_object(obj_id)
    
    def modify_selected_object(self):
        # nao implementado, entrega futura
        pass