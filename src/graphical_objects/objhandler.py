from graphical_objects.abstract_graphical_object import AbstractGraphicalObject
class ObjHandler:
    # Classe feita com auxílio de IA (Claude), dada a natureza extensiva de parsing
    # Supports both 2D and 3D .obj files

    @staticmethod
    def load_obj(file_path):
        """Loads a .obj file and returns its content as a string."""
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            ##print(f"File not found: {file_path}")
            return None
        except Exception as e:
            ##print(f"Error loading .obj file: {e}")
            return None

    @staticmethod
    def process_obj_data(obj_data, app):
        """Processes the loaded .obj data and creates the objects themselves."""
        vertices = []
        lines = [] 
        wireframes = [] 
        faces = []  # For 3D objects
        current_material = None
        is_3d = False

        # Material color mapping
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
                parts = line.split()
                if len(parts) >= 4:  # 3D vertex (x, y, z)
                    is_3d = True
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append((x, y, z))
                else:  # 2D vertex (x, y)
                    x, y = float(parts[1]), float(parts[2])
                    vertices.append((x, y))
            
            elif line.startswith('usemtl '):
                current_material = line.split()[1]
            
            elif line.startswith('l '):
                indices = list(map(int, line.split()[1:]))
                lines.append((indices, current_material))
            
            elif line.startswith('f '):
                indices = [int(v.split('/')[0]) for v in line.split()[1:]]
                if is_3d:
                    faces.append((indices, current_material))
                else:
                    wireframes.append((indices, current_material))

        # Create 2D lines if not 3D
        if not is_3d:
            for i, (indices, mat_name) in enumerate(lines):
                for j in range(len(indices) - 1):
                    x1, y1 = vertices[indices[j] - 1]
                    x2, y2 = vertices[indices[j + 1] - 1]
                    coords_str = f"({x1}, {y1}), ({x2}, {y2})"
                    color = material_color_map.get(mat_name, "#FFFFFF")
                    app.create_object("Line", coords_str, f"Line_{i+1}_{j+1}", color)

            # Create 2D wireframes
            for i, (indices, mat_name) in enumerate(wireframes):
                coords_str = ", ".join(
                    f"({vertices[idx - 1][0]}, {vertices[idx - 1][1]})" for idx in indices
                )
                color = material_color_map.get(mat_name, "#FFFFFF")
                app.create_object("Wireframe", coords_str, f"Wireframe_{i+1}", color)
        
        else:
            # Create 3D objects
            # For faces (3D objects)
            for i, (indices, mat_name) in enumerate(faces):
                coords = []
                for idx in indices:
                    x, y, z = vertices[idx - 1]
                    coords.append((x, y, z))
                
                # Format coordinates string for 3D object
                coords_str = ", ".join(
                    f"({x}, {y}, {z})" for x, y, z in coords
                )
                color = material_color_map.get(mat_name, "#FFFFFF")
                app.create_object("3DObject", coords_str, f"Object3D_{i+1}", color)

            # For lines in 3D
            for i, (indices, mat_name) in enumerate(lines):
                coords = []
                for idx in indices:
                    x, y, z = vertices[idx - 1]
                    coords.append((x, y, z))
                
                # Create line segments for 3D lines
                coords_str = ", ".join(
                    f"({x}, {y}, {z})" for x, y, z in coords
                )
                color = material_color_map.get(mat_name, "#FFFFFF")
                app.create_object("3DObject", coords_str, f"Line3D_{i+1}", color)

    @staticmethod
    def save_obj(file_path, obj: AbstractGraphicalObject):
        """Saves the object data as a .obj file (2D or 3D)."""
        try:
            obj_type = obj.get_type()
            vertices = obj.get_vertices()
            color = obj.get_color()
            is_3d = obj_type == "3DObject"

            obj_data = ""

            # Optional comment header
            obj_data += f"# Object: {obj.get_name()} ({obj_type})\n"
            if color:
                # Convert hex color to material name if possible
                color_name = next((name for name, hex_value in {
                    "red": "#FF0000",
                    "green": "#00FF00",
                    "blue": "#0000FF",
                    "yellow": "#FFFF00",
                    "cyan": "#00FFFF",
                    "magenta": "#FF00FF",
                    "white": "#FFFFFF",
                    "black": "#000000",
                }.items() if hex_value.lower() == color.lower()), color)
                
                obj_data += f"usemtl {color_name}\n"

            # Helper function to extract x, y, z coordinates from a vertex
            # which could be a tuple or a custom Ponto3D class
            def get_coords(vertex):
                # Handle custom Ponto3D class (assuming it has x, y, z attributes or methods)
                if hasattr(vertex, 'x') and hasattr(vertex, 'y'):
                    # For a Ponto3D type object
                    if hasattr(vertex, 'z'):
                        return vertex.x, vertex.y, vertex.z
                    return vertex.x, vertex.y, 0
                elif isinstance(vertex, (list, tuple)):
                    # For tuple/list type
                    if len(vertex) >= 3:
                        return vertex[0], vertex[1], vertex[2]
                    elif len(vertex) == 2:
                        return vertex[0], vertex[1], 0
                # As a fallback, try string parsing
                try:
                    if isinstance(vertex, str):
                        parts = vertex.strip('()').split(',')
                        if len(parts) >= 3:
                            return float(parts[0]), float(parts[1]), float(parts[2])
                        else:
                            return float(parts[0]), float(parts[1]), 0
                except:
                    pass
                
                # Last resort
                return 0, 0, 0

            # Write vertices
            for vertex in vertices:
                if is_3d:
                    x, y, z = get_coords(vertex)
                    obj_data += f"v {x} {y} {z}\n"
                else:
                    x, y, _ = get_coords(vertex)
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
            elif obj_type == "3DObject":
                # For 3D objects, create faces from vertices
                indices = [str(i + 1) for i in range(len(vertices))]
                obj_data += f"f {' '.join(indices)}\n"
                
                # If there are defined segments, add them as lines too
                if hasattr(obj, 'segments') and obj.segments:
                    # Create a vertex lookup dictionary for more efficient matching
                    vertex_lookup = {}
                    
                    # Function to compare two vertices, accounting for Ponto3D objects
                    def vertices_equal(v1, v2):
                        x1, y1, z1 = get_coords(v1)
                        x2, y2, z2 = get_coords(v2)
                        # Use approximate equality for floating point
                        return (abs(x1 - x2) < 0.001 and 
                                abs(y1 - y2) < 0.001 and 
                                abs(z1 - z2) < 0.001)
                    
                    # Build lookup of existing vertices
                    for i, vertex in enumerate(vertices):
                        # We can't use the vertex as a direct key if it's a custom object
                        # So we'll create a string representation key
                        x, y, z = get_coords(vertex)
                        key = f"{x:.6f},{y:.6f},{z:.6f}"
                        vertex_lookup[key] = i + 1  # Store 1-based index
                    
                    # Track vertices that need to be added
                    additional_vertices = []
                    segment_data = []
                    
                    for segment in obj.segments:
                        start_point, end_point = segment[0], segment[1]
                        
                        # Get coordinates and create keys
                        start_x, start_y, start_z = get_coords(start_point)
                        end_x, end_y, end_z = get_coords(end_point)
                        start_key = f"{start_x:.6f},{start_y:.6f},{start_z:.6f}"
                        end_key = f"{end_x:.6f},{end_y:.6f},{end_z:.6f}"
                        
                        # Try to find indices, if not found, add them to additional vertices
                        if start_key in vertex_lookup:
                            idx1 = vertex_lookup[start_key]
                        else:
                            # Add to additional vertices list and update lookup
                            additional_vertices.append((start_x, start_y, start_z))
                            idx1 = len(vertices) + len(additional_vertices)
                            vertex_lookup[start_key] = idx1
                        
                        if end_key in vertex_lookup:
                            idx2 = vertex_lookup[end_key]
                        else:
                            # Add to additional vertices list and update lookup
                            additional_vertices.append((end_x, end_y, end_z))
                            idx2 = len(vertices) + len(additional_vertices)
                            vertex_lookup[end_key] = idx2
                        
                        segment_data.append((idx1, idx2))
                    
                    # Add any additional vertices needed for segments
                    for x, y, z in additional_vertices:
                        obj_data += f"v {x} {y} {z}\n"
                    
                    # Add the line segments
                    for idx1, idx2 in segment_data:
                        obj_data += f"l {idx1} {idx2}\n"
            else:
                raise ValueError(f"Unsupported object type: {obj_type}")

            # Write to file
            with open(file_path, 'w') as file:
                file.write(obj_data)

        except Exception as e:
            print(f"Error saving .obj file: {e}")