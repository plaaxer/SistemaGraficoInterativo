class DisplayFile:
    def __init__(self):
        self.objects = []

    def add_object(self, obj):

        self.objects.append(obj)

    def remove_object(self, obj):

        if obj in self.objects:
            self.objects.remove(obj)

    def get_objects(self):

        return self.objects

    def clear(self):

        self.objects.clear()
