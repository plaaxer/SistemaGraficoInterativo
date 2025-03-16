from abc import ABC, abstractmethod

class AbstractGraphicalObject(ABC):

    def __init__(self, name):
        self._name = name
        #todo
    
    @abstractmethod
    def draw(self, canvas):
        pass

    @abstractmethod
    def move(self, dx, dy):
        pass

    @abstractmethod
    def resize(self, scale):
        pass

    @abstractmethod
    def get_position(self):
        pass

    @abstractmethod
    def get_size(self):
        pass