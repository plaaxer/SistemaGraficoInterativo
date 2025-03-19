from abc import ABC, abstractmethod
import copy as cp

class AbstractGraphicalObject(ABC):

    def __init__(self, name):
        self._name = name

    @abstractmethod
    def draw(self, canvas):
        pass
    
    @abstractmethod
    def get_object_center(self):
        pass
    
    @abstractmethod
    def get_vertices(self):
        pass

    @abstractmethod
    def get_type(self):
        pass
    
    @abstractmethod
    def modify(self, new_coords):
        pass

    def update_name(self, new_name):
        self._name = new_name

    def get_name (self):
        return self._name
    
    def clone(self):
        return cp.copy.deepcopy(self)

    def __repr__(self):
        return f"{self.__class__.__name__}({self._name})"