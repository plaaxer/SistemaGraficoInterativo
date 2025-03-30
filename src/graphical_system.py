# classe para tratar da lógica de geração gráfica
from user_interface import UserInterface
from viewport import Viewport
from graphical_objects.graphical_object_factory import GraphicalObjectFactory

import utils as ut
import constants as c


class GraphicalSystem:
    def __init__(self):
        self._ui = UserInterface(self)
        self._viewport = Viewport(self._ui, width=c.VIEWPORT_WIDTH, height=c.VIEWPORT_HEIGHT, bg=c.VIEWPORT_BG_COLOR)
        self._ui.set_viewport(self._viewport)
        self._unique_id = 0
    
    def run(self):
        self._ui.run()
        
    def create_object(self, obj_type: str, coords: str, name: str, color: str):

        # valida atributos
        if name == "" or name is None:
            name = "Objeto"
        if color == "" or color is None:
            color = c.DEFAULT_OBJECT_COLOR

        #processa coordenadas
        try:
            coords = ut.parse_coordinates(coords, obj_type)
        except ValueError as e:
            self._ui.display_error(str(e))
            return

        #instancia objeto utilizando factory
        obj = GraphicalObjectFactory.create_object(obj_type, name, self._unique_id, coords, color)
        self._unique_id += 1

        #adiciona objeto à display file
        self._viewport.display_file.add_object(obj)

        #atualiza viewport
        self._viewport.update()

        #exibe mensagem de sucesso e adiciona objeto à lista de referências da UI
        self.reference_object(obj)

    def translate_object(self, obj_id: str, shift: str):

        obj = self._viewport.display_file.get_object_by_id(int(obj_id))
        
        if obj is None:
            self._ui.display_error(f"Erro ao obter objeto com id {obj_id} para translação")
            return

        # adicionar exception aqui para caso o shift nao tenha argumentos o suficiente
        new_cords = ut.translate(obj.get_vertices(), shift)
        obj.modify(new_cords)

        self._viewport.update()

        self.reference_object(obj, "translated")
    
    def delete_object(self, obj_id: str):
        obj = self._viewport.display_file.get_object_by_id(int(obj_id))
        
        if obj is None:
            self._ui.display_error(f"Object with id {obj_id} not found")
            return
        
        self._viewport.display_file.remove_object(obj)
        self._viewport.update()

        self.reference_object(obj, "deleted")

    def modify_object(self, obj_id: str, type: str, value: str):

        if type == "translate":
            try:
                shift = ut.parse_coordinates(value)
            except ValueError as e:
                self._ui.display_error(str(e))
                return
            self.translate_object(obj_id, shift.pop(0))
        
        elif type == "escalate":
            pass

        self._viewport.update()
    
    def reference_object(self, obj, message=None):
        if message == "deleted":
            self._ui.display_info(f"Object {obj.get_type()} with id {obj.get_id()} deleted")
        elif message == "translated":
            self._ui.display_info(f"Object {obj.get_type()} with id {obj.get_id()} translated")
        else:
            self._ui.display_info(f"Object {obj.get_type()} created with id {obj.get_id()}")