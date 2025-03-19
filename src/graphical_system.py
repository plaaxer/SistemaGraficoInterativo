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
        
    def create_object(self, obj_type: str, coords: str):

        #processa coordenadas
        try:
            coords = ut.parse_coordinates(coords)
        except ValueError as e:
            self._ui.display_error(str(e))
            return

        #instancia objeto utilizando factory
        obj = GraphicalObjectFactory.create_object(obj_type, str(self._unique_id), coords)
        self._unique_id += 1

        #adiciona objeto à display file
        self._viewport.display_file.add_object(obj)

        #atualiza viewport
        self._viewport.update()