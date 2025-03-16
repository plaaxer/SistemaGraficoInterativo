from graphical_objects.abstract_graphical_object import AbstractGraphicalObject
from graphical_objects.point import Point
from graphical_objects.line import Line
from graphical_objects.wireframe import Wireframe

class GraphicalObjectFactory:
    @staticmethod
    def create_object(object_type: str, name: str, coordinates: tuple):
        object_classes = {
            "Point": Point,
            "Line": Line,
            "Wireframe": Wireframe,
        }
        
        if object_type in object_classes:
            return object_classes[object_type](name, coordinates)
        
        raise ValueError(f"tipo de objeto desconhecido: {object_type}")
