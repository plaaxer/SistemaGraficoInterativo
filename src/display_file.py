class DisplayFile:
    def __init__(self):
        self.objects = []
        self._observers = []

    def add_object(self, obj):

        self.objects.append(obj)

    def remove_object(self, obj):

        if obj in self.objects:
            self.objects.remove(obj)

    def get_objects(self):

        return self.objects
    
    def get_object_by_id(self, obj_id):
        if type(obj_id) == str:
            obj_id = int(obj_id)

        for obj in self.objects:
            if obj.get_id() == obj_id:
                return obj
        return
    
    def get_objects_infos(self):
        return [f"{obj.get_info()}" for obj in self.objects]

    def clear(self):

        self.objects.clear()

    # observer design pattern. Object_manager_ui é notificado de mudancas na lista de display de objetos e atualiza
    def subscribe(self, observer):
        self._observers.append(observer)

    def notify(self):
        for observer in self._observers:
            observer.update()
