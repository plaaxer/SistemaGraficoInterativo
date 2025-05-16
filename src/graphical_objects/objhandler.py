from graphical_objects.abstract_graphical_object import AbstractGraphicalObject

import typing

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
    def process_obj_data(obj_data: str, app):
        """
        Processes the loaded .obj data (string) and creates a 3D wireframe
        object using the application's create_object method.

        It extracts vertices ('v') and defines segments based on face ('f') definitions.
        Handles comments ('#') in the OBJ data.

        Args:
            obj_data: A string containing the content of an .obj file.
            app: The application object with a create_object method.
        """
        vertices: typing.List[typing.Tuple[float, float, float]] = []
        segments_set: typing.Set[typing.Tuple[typing.Tuple[float, float, float], typing.Tuple[float, float, float]]] = set()

        lines = obj_data.strip().split('\n')

        print("Processing OBJ data...")

        # Primeiro, leia todos os vértices
        # Processa todas as linhas, mas só age nas que começam com 'v'
        for line in lines:
            # Ignora ou remove a parte do comentário (#...)
            comment_index = line.find('#')
            if comment_index != -1:
                line = line[:comment_index].strip()
            else:
                line = line.strip()

            parts = line.split()
            if not parts: # Ignora linhas vazias após remover comentário
                continue

            prefix = parts[0]

            if prefix == 'v':
                # Processa linha de vértice: v x y z
                try:
                    x, y, z = float(parts[1]), float(parts[2]), float(parts[3])
                    vertices.append((x, y, z))
                except (ValueError, IndexError):
                    print(f"Warning: Skipping malformed vertex line: {line}")
                    continue

        print(f"Found {len(vertices)} vertices.")
        if not vertices:
            print("Error: No vertices found in OBJ data.")
            return # Não podemos processar sem vértices

        # Agora, processe as faces para extrair as arestas
        # Percorre as linhas novamente, agindo nas que começam com 'f'
        for line in lines:
            # Ignora ou remove a parte do comentário (#...)
            comment_index = line.find('#')
            if comment_index != -1:
                line = line[:comment_index].strip()
            else:
                line = line.strip()

            parts = line.split()
            if not parts: # Ignora linhas vazias após remover comentário
                continue

            prefix = parts[0]

            if prefix == 'f':
                # Processa linha de face: f v1 v2 v3 ...
                # Índices são baseados em 1. Podem ter o formato v/vt/vn
                try:
                    # Obtém apenas o índice do vértice (ignora /vt e /vn)
                    face_indices_str = parts[1:]
                    
                    # Verifica se há índices válidos na linha 'f'
                    if not face_indices_str:
                        print(f"Warning: Skipping face line with no vertex indices: {line}")
                        continue

                    # Converte strings de índice para inteiros
                    face_indices = [int(p.split('/')[0]) for p in face_indices_str if p.split('/')[0].isdigit()]

                    # Uma face precisa de pelo menos 2 vértices para definir um segmento
                    if len(face_indices) < 2:
                         print(f"Warning: Skipping face with less than 2 valid vertex indices: {line}")
                         continue

                    # Cria segmentos entre vértices consecutivos na face, incluindo fechar o loop
                    num_indices = len(face_indices)
                    for i in range(num_indices):
                        # Índices do vértice atual e do próximo (com wrap-around para fechar)
                        idx1_obj = face_indices[i]
                        idx2_obj = face_indices[(i + 1) % num_indices] # % num_indices para fechar o ciclo

                        # Converte índices .obj (base 1) para índices da lista Python (base 0)
                        idx1_list = idx1_obj - 1
                        idx2_list = idx2_obj - 1

                        # Verifica se os índices são válidos na lista de vértices
                        if idx1_list < 0 or idx1_list >= len(vertices) or idx2_list < 0 or idx2_list >= len(vertices):
                             print(f"Warning: Skipping segment due to out-of-bounds vertex index: {idx1_obj} or {idx2_obj} (Total vertices: {len(vertices)}) from line: {line}")
                             continue

                        # Obtém as coordenadas dos vértices
                        v1_coords = vertices[idx1_list]
                        v2_coords = vertices[idx2_list]

                        # Cria uma representação canônica da aresta (tupla de coordenadas, ordenada)
                        canonical_segment = tuple(sorted((v1_coords, v2_coords)))

                        segments_set.add(canonical_segment)

                except (ValueError, IndexError):
                     # Esta exceção agora deve ser mais rara, pois tratamos comentários e falta de índices
                     print(f"Warning: Skipping face line due to unexpected format error: {line}")
                     continue


            # Ignora outros tipos de linhas (vn, vt, usemtl, s, etc.)

        # Agora, formatar os segmentos encontrados no formato string requerido
        segments_string_parts = []
        for seg_point1, seg_point2 in segments_set:
             # Formata as coordenadas com precisão para floating point
             segments_string_parts.append(f"({seg_point1[0]:.6f}, {seg_point1[1]:.6f}, {seg_point1[2]:.6f}), ({seg_point2[0]:.6f}, {seg_point2[1]:.6f}, {seg_point2[2]:.6f}), ")

        # Junta as partes da string e remove a vírgula e espaço finais ", "
        segments_string = "".join(segments_string_parts).rstrip(", ")

        print(f"Extracted {len(segments_set)} unique segments.")

        if not segments_string:
            print("Warning: No valid segments found for creating the object.")
            return # Não cria um objeto vazio

        # Cria o objeto usando o método da aplicação
        object_name = "LoadedObjModel" # Nome padrão
        object_color = "blue"      # Cor padrão

        print(f"Creating object '{object_name}' with {len(segments_set)} segments.")

        if hasattr(app, 'create_object') and callable(app.create_object):
             try:
                 app.create_object(
                     "3DObject",          # Tipo de objeto
                     segments_string,     # A string de pares de coordenadas
                     object_name,         # Nome
                     object_color         # Cor
                 )
                 print("OBJ object processing complete. Object created successfully.")
             except Exception as e:
                 print(f"Error calling app.create_object: {e}")
        else:
             print("Error: Provided 'app' object does not have a callable 'create_object' method.")

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