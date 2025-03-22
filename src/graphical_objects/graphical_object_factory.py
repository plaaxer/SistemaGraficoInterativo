from graphical_objects.abstract_graphical_object import AbstractGraphicalObject
from graphical_objects.point import Point
from graphical_objects.line import Line
from graphical_objects.wireframe import Wireframe

class GraphicalObjectFactory:

    object_classes = {
                "Point": Point,
                "Line": Line,
                "Wireframe": Wireframe,
            }

    @staticmethod
    def create_object(object_type: str, name: str, object_id: int, coordinates: tuple):

        if (isinstance(object_type, AbstractGraphicalObject)):
            GraphicalObjectFactory.duplicate_object(object_type, name, object_id)
    
        if object_type in GraphicalObjectFactory.object_classes:
            obj_class = GraphicalObjectFactory.object_classes[object_type]
            return obj_class(name, object_id, coordinates)
        
        raise ValueError(f"tipo de objeto desconhecido: {object_type}")
    
    @staticmethod
    def duplicate_object(obj: AbstractGraphicalObject, name: str, id: int):
        new_obj = obj.clone()
        new_obj.update_name(name)
        return new_obj
