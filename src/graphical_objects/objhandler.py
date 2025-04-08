from graphical_objects.abstract_graphical_object import AbstractGraphicalObject
class ObjHandler:
    
    # por enquanto suporta apenas arquivos 2d e sem .mtl

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

    @staticmethod
    def process_obj_data(obj_data, app):
        """Processes the loaded .obj data and creates the objects themselves."""
        vertices = []
        lines = [] 
        wireframes = [] 
        current_material = None

        # todo: adicionar suporte a .mtl
        material_color_map = {
            "red": "#FF0000",
            "green": "#00FF00",
            "blue": "#0000FF",
            "yellow": "#FFFF00",
            "cyan": "#00FFFF",
            "magenta": "#FF00FF",
            "white": "#FFFFFF",
            "black": "#000000",
        }

        for line in obj_data.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if line.startswith('v '):
                _, x, y = line.split()
                vertices.append((float(x), float(y)))
            elif line.startswith('usemtl '):
                current_material = line.split()[1]
            elif line.startswith('l '):
                indices = list(map(int, line.split()[1:]))
                lines.append((indices, current_material))
            elif line.startswith('f '):
                indices = list(map(int, line.split()[1:]))
                wireframes.append((indices, current_material))

        # criar linhas
        for i, (indices, mat_name) in enumerate(lines):
            for j in range(len(indices) - 1):
                x1, y1 = vertices[indices[j] - 1]
                x2, y2 = vertices[indices[j + 1] - 1]
                coords_str = f"({x1}, {y1}), ({x2}, {y2})"
                color = material_color_map.get(mat_name, None)
                app.create_object("Line", coords_str, f"Line_{i+1}_{j+1}", color)

        # criar wireframes
        for i, (indices, mat_name) in enumerate(wireframes):
            coords_str = ", ".join(
                f"({vertices[idx - 1][0]}, {vertices[idx - 1][1]})" for idx in indices
            )
            color = material_color_map.get(mat_name, None)
            app.create_object("Wireframe", coords_str, f"Wireframe_{i+1}", color)



    @staticmethod
    def save_obj(file_path, obj: AbstractGraphicalObject):
        """Saves the object data as a .obj file."""
        try:
            obj_type = obj.get_type()
            vertices = obj.get_vertices()
            color = obj._color  # Accessing directly; can also use a getter if preferred

            lines = []
            obj_data = ""

            # Optional comment header
            obj_data += f"# Object: {obj.get_name()} ({obj_type})\n"
            if color:
                obj_data += f"usemtl {color}\n"

            # Write vertices
            for x, y in vertices:
                obj_data += f"v {x} {y}\n"

            # Create lines or face depending on the type
            if obj_type == "Line":
                obj_data += "l 1 2\n"
            elif obj_type == "Wireframe":
                indices = [str(i + 1) for i in range(len(vertices))]
                obj_data += f"f {' '.join(indices)}\n"
            elif obj_type == "Point":
                # Points don't have a specific representation in .obj other than vertices
                pass
            else:
                raise ValueError(f"Unsupported object type: {obj_type}")

            # Write to file
            with open(file_path, 'w') as file:
                file.write(obj_data)

            print(f"Successfully saved to {file_path}")
        except Exception as e:
            print(f"Error saving .obj file: {e}")

