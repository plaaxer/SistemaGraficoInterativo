from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

class Point(AbstractGraphicalObject):
    def __init__(self, name, coordinates):
        super().__init__(name)
        self.coordinates = coordinates

#todo: implementar os métodos abstratos (nao precisa de todos)