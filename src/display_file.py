class DisplayFile:
    def __init__(self):
        """Initialize an empty display file to store graphical objects."""
        self.objects = []

    def add_object(self, obj):
        """Adds a graphical object to the display file."""
        self.objects.append(obj)

    def remove_object(self, obj):
        """Removes a graphical object from the display file."""
        if obj in self.objects:
            self.objects.remove(obj)

    def get_objects(self):
        """Returns a list of all stored graphical objects."""
        return self.objects

    def clear(self):
        """Removes all objects from the display file."""
        self.objects.clear()
