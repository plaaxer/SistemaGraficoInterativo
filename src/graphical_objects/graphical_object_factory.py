from graphical_objects.abstract_graphical_object import AbstractGraphicalObject
from graphical_objects.point import Point
from graphical_objects.line import Line
from graphical_objects.wireframe import Wireframe
from graphical_objects.objeto3d import Object3D
from graphical_objects.ponto3d import Ponto3D
import constants as c

class GraphicalObjectFactory:

    object_classes = {
                "Point": Point,
                "Line": Line,
                "Wireframe": Wireframe,
                "3DObject": Object3D,
                "3DPoint": Ponto3D,
            }

    @staticmethod
    def create_object(object_type: str, name: str, object_id: int, coordinates: tuple, color: str, fill: bool, curve_type: str):

        if (isinstance(object_type, AbstractGraphicalObject)):
            GraphicalObjectFactory.duplicate_object(object_type, name, object_id)

        if (object_type == "Curve"):
            if curve_type == c.CURVE_TYPE_BEZIER:
                from graphical_objects.bezier import BezierCurve
                return BezierCurve(name, object_id, coordinates, color, fill)
            elif curve_type == c.CURVE_TYPE_BSPLINE:
                from graphical_objects.bspline import BSplineCurve
                return BSplineCurve(name, object_id, coordinates, color, fill)
            else:
                raise ValueError(f"tipo de curva desconhecido: {curve_type}")
    
        if object_type in GraphicalObjectFactory.object_classes:
            obj_class = GraphicalObjectFactory.object_classes[object_type]
            return obj_class(name, object_id, coordinates, color, fill)
        
        raise ValueError(f"tipo de objeto desconhecido: {object_type}")
    
    @staticmethod
    def duplicate_object(obj: AbstractGraphicalObject, name: str, id: int):
        new_obj = obj.clone()
        new_obj.update_name(name)
        return new_obj
