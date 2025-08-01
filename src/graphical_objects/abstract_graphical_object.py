from abc import ABC, abstractmethod
import copy as cp
import numpy as np

class AbstractGraphicalObject(ABC):

    def __init__(self, name, id, color):
        self._name = name
        self._id = id
        self._color = color
        #self.in_window = True
        self._clipped_vertices = None

    @abstractmethod
    def draw(self, canvas):
        pass
    
    @abstractmethod
    def get_object_center(self):
        pass
    
    @abstractmethod
    def get_vertices(self):
        pass

    def get_color(self):
        return self._color

    def get_type(self):
        return self.__class__.__name__

    
    @abstractmethod
    def modify(self, new_coords):
        pass

    def update_name(self, new_name):
        self._name = new_name

    def get_name (self):
        return self._name
    
    def update_id(self, new_id):
        self._id = new_id

    def get_id(self):
        return self._id
    
    def clone(self):
        return cp.copy.deepcopy(self)
    
    def get_info(self):
        return f"[{self._id}] {self._name} ({self.get_type()})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self._name})"
    
    def set_scn_vertices(self, scn_vertices):
        self._scn_vertices = [(float(x), float(y)) for x, y in scn_vertices]

    def get_scn_vertices(self):
        if not hasattr(self, '_scn_vertices'):
            return None
        return self._scn_vertices
    
    def set_clipped_vertices(self, clipped_vertices):
        self._clipped_vertices = clipped_vertices

    def get_clipped_vertices(self):
        return self._clipped_vertices
