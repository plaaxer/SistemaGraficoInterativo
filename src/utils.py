from typing import List, Tuple
import constants as c
import numpy as np

def parse_coordinates(coordinates: str, type: str = None) -> List[Tuple[float, float]]:
    if not coordinates.strip():
        raise ValueError("Favor inserir coordenadas")
    
    coordinates = coordinates.replace(" ", "")
    print(coordinates.startswith("("))
    if not (coordinates.startswith("(") and coordinates.endswith(")")):
        raise ValueError("Formato inválido de coordenadas")
    
    pairs = coordinates.split("),(")
    pairs[0] = pairs[0].replace("(", "")
    pairs[-1] = pairs[-1].replace(")", "")

    parsed_coords = []
   
    print("Pairs: ", pairs)
    for pair in pairs:
        print("Pair: ", pair)
        values = pair.split(",")
        if len(values) != 2:
            raise ValueError("Formato inválido de coordenadas")
        
        try:
            x, y = float(values[0]), float(values[1])
        except ValueError:            
            raise ValueError("Coordenadas devem ser números válidos")
        
        # por enquanto, vamos arredondar as coordenadas para inteiros
        x, y = map(round, (x, y))
        
        print("Final coordinates: (", x, ", ", y, ")")

        parsed_coords.append((x, y))

    if (type == "Point" and len(parsed_coords) > 1):
        raise ValueError("O objeto Point requer apenas uma coordenada")
    elif (type == "Line" and len(parsed_coords) > 2):
        raise ValueError("O objeto Line requer apenas duas coordenadas")
    elif (type == "Wireframe" and len(parsed_coords) < 3):
        raise ValueError("O objeto Wireframe requer pelo menos três coordenadas")
    elif (type == "Line" and len(parsed_coords) < 2):
        raise ValueError("O objeto Line requer pelo menos duas coordenadas")
        
    return parsed_coords

def homogeneo(vertices: List[Tuple[int, int]]) -> List[Tuple[int, int, int]]:
    return np.array([(*x, 1) for x in vertices])

def translate(vertices: List[Tuple[int, int]], shift: Tuple[int, int]) -> List[Tuple[int, int]]:
    return [(x + shift[0], y + shift[1]) for x, y in vertices]

def escalate(vertices: List[Tuple[int, int]], factor: Tuple[float, float]) -> List[Tuple[int, int]]:
    matrix1 = homogeneo(vertices)
    matrix2 = [[factor[0], 0, 0], [0, factor[1], 0], [0, 0, 1]]
    result = np.dot(matrix1, matrix2)
    return [(x, y) for x, y, _ in result]

def rotate(vertices: List[Tuple[int, int]], angle: float) -> List[Tuple[int, int]]:
    rad = np.radians(angle)
    # implementar o resto
    return 

def get_id_from_info(info: str) -> str:
    return info.split()[0][1:-1]