class ObjHandler:
    @staticmethod
    def load_obj(file_path):
        """Loads a .obj file and returns its content as a string (simplified logic)."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error loading .obj file: {e}")
            return None

    def process_obj_data(self, obj_data):
        """Processes the loaded .obj data and creates the objects themselves."""
        
        return obj_data

    @staticmethod
    def save_obj(file_path, obj_data):
        """Saves the object data as a .obj file (assumes obj_data is a string)."""
        try:
            with open(file_path, 'w') as file:
                file.write(obj_data)
            print(f"Successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving .obj file: {e}")
