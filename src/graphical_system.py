# classe para tratar da lógica de geração gráfica
from user_interface import UserInterface
from viewport import Viewport
from graphical_objects.graphical_object_factory import GraphicalObjectFactory
from file_loader import FileLoader
from graphical_objects.objhandler import ObjHandler
from clipper import Clipper

import utils as ut
import constants as c


class GraphicalSystem:
    def __init__(self):
        self._ui = UserInterface(self)
        self._file_loader = FileLoader(self)
        self._viewport = Viewport(self, self._ui, width=c.VIEWPORT_WIDTH, height=c.VIEWPORT_HEIGHT, bg=c.VIEWPORT_BG_COLOR)
        self._ui.set_viewport(self._viewport)
        self._unique_id = 0
        self._clipper = Clipper()
        self._3dperspective = c.PARALLEL_PROJECTION
    
    def run(self):
        self._ui.run()
        
    def create_object(self, obj_type: str, coords: str, name: str, color: str, **options):

        # valida atributos
        if name == "" or name is None:
            name = "Objeto"
        if color == "" or color is None:
            color = c.DEFAULT_OBJECT_COLOR

        print("FKING OPTIONS", options)

        # argumentos adicionais
        fill = options.get("fill", False)
        curve_type = options.get("curve_type", None)
        surface_type = options.get("surface_type", None)

        if curve_type is None and obj_type == "Curve":
            self._ui.display_error("Tipo de curva não especificado")
            return
        
        if surface_type is None and obj_type == "Surface":
            self._ui.display_error("Tipo de superfície não especificado")
            return

        #processa coordenadas
        try:
            coords = ut.parse_coordinates(coords, obj_type)
        except ValueError as e:
            self._ui.display_error(str(e))
            return

        # instancia objeto utilizando factory com parâmetros em um dicionário
        params = {
            "object_type": obj_type,
            "name": name,
            "object_id": self._unique_id,
            "coordinates": coords,
            "color": color,
            "fill": fill,
            "curve_type": curve_type,
            "surface_type": surface_type
        }

        obj = GraphicalObjectFactory.create_object(**params)
        self._unique_id += 1


        #adiciona objeto à display file
        self._viewport.display_file.add_object(obj)

        #atualiza viewport
        self._viewport.update()

        #exibe mensagem de sucesso e adiciona objeto à lista de referências da UI
        self.reference_object(obj)

    def translate_object(self, obj_id: str, shift: list[tuple[float, float]]):

        obj = self._viewport.display_file.get_object_by_id(int(obj_id))
        
        if obj is None:
            self._ui.display_error(f"Erro ao obter objeto com id {obj_id} para translação")
            return

        # adicionar exception aqui para caso o shift nao tenha argumentos o suficiente
        new_cords = ut.translate(obj.get_vertices(), shift[0])
        obj.modify(new_cords)

        self._viewport.update()

        self.reference_object(obj, "translated")

    def escalate_object(self, obj_id: str, factor: list[tuple[float, float]]):
        obj = self._viewport.display_file.get_object_by_id(int(obj_id))
        
        if obj is None:
            self._ui.display_error(f"Erro ao obter objeto com id {obj_id} para escalonamento")
            return

        # adicionar exception aqui para caso o factor nao tenha argumentos o suficiente
        center = obj.get_object_center()
        new_cords = ut.translate(obj.get_vertices(), (center[0] * -1, center[1] * -1))
        new_cords = ut.escalate(new_cords, factor[0])
        new_cords = ut.translate(new_cords, center)
        obj.modify(new_cords)

        self._viewport.update()

        self.reference_object(obj, "escalated")
    
    def rotate_object(self, obj_id: str, angle, point = None):
        obj = self._viewport.display_file.get_object_by_id(int(obj_id))

        if obj is None:
            self._ui.display_error(f"Erro ao obter objeto com id {obj_id} para rotação")
            return
        print(obj.get_type())
        if obj.get_type() == "3DObject":
            print("Rotating 3D object")
            angles = ut.parse_angle(angle)
            if point is None:
                obj.rotate(angles[0], angles[1], angles[2])
            else:
                obj.rotate(angles[0], angles[1], angles[2], point)

        else:
            if point is None:
                point = obj.get_object_center()
            else:
                point = point[0]
            
            new_cords = ut.translate(obj.get_vertices(), (point[0] * -1, point[1] * -1))
            new_cords = ut.rotate(new_cords, angle)
            new_cords = ut.translate(new_cords, point)
            obj.modify(new_cords)

        self._viewport.update()

        self.reference_object(obj, "rotated")


    def delete_object(self, obj_id: str):
        obj = self._viewport.display_file.get_object_by_id(int(obj_id))
        
        if obj is None:
            self._ui.display_error(f"Object with id {obj_id} not found")
            return
        
        self._viewport.display_file.remove_object(obj)
        self._viewport.update()

        self.reference_object(obj, "deleted")

    def modify_object(self, obj_id: str, type: str, value: str, other=None):

        if type == "translate":
            try:
                shift = ut.parse_coordinates(value)
            except ValueError as e:
                self._ui.display_error(str(e))
                return
            self.translate_object(obj_id, shift)
        
        elif type == "escalate":
            try:
                factor = ut.parse_coordinates(value)
            except ValueError as e:
                self._ui.display_error(str(e))
                return
            self.escalate_object(obj_id, factor)

        elif type == "rotate":
            if other is not None:
                try:
                    point = ut.parse_coordinates(other)
                except ValueError as e:
                    self._ui.display_error("Ponto inválido")
                    return
            if other is not None:
                self.rotate_object(obj_id, value, point)
            else:
                self.rotate_object(obj_id, value)

        self._viewport.update()
    
    def reference_object(self, obj, message=None):
        if message != None:
            self._ui.display_info(f"Object {obj.get_type()} with id {obj.get_id()} {message}")
        else:
            self._ui.display_info(f"Object {obj.get_type()} created with id {obj.get_id()}")
    
    def import_object(self):
        file_path = self._file_loader.open_file_dialog()
        if file_path:
            try:
                # carrega string
                obj_as_string = ObjHandler.load_obj(file_path)
                if obj_as_string is None:
                    self._ui.display_error("Error loading object: File not found or empty")
                    return
                # processa string e cria objetos
                ObjHandler.process_obj_data(obj_as_string, self)
            except Exception as e:
                self._ui.display_error(f"Error loading object: {str(e)}")

    def export_object(self, obj_id: str):
        file_path = self._file_loader.save_file_dialog()
        if file_path:
            try:
                if self._viewport.display_file.get_object_by_id(int(obj_id)) is None:
                    self._ui.display_error(f"Object with id {obj_id} not found")
                    return
                # salva o objeto em um arquivo .obj
                ObjHandler.save_obj(file_path, self._viewport.display_file.get_object_by_id(int(obj_id)))
                self._ui.display_info(f"Object saved to {file_path}")
            except Exception as e:
                self._ui.display_error(f"Error saving object: {str(e)}")

    def clip_objects(self):
        self._clipper.clip(self._viewport.display_file.get_objects(), self._viewport)

    def switch_clipping_algorithm(self):
        self._clipper.selected_algorithm = 2 if self._clipper.selected_algorithm == 1 else 1