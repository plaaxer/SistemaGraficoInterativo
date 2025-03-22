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
    
    def get_object_by_id(self, obj_id):

        for obj in self.objects:
            if obj.get_id() == obj_id:
                return obj
        return

    def clear(self):

        self.objects.clear()
