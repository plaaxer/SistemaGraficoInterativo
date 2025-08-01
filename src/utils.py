from typing import List, Tuple
import constants as c
import numpy as np

def parse_coordinates(coordinates: str, type: str = None) -> List[Tuple[float, float]]:
    if not coordinates.strip():
        raise ValueError("Favor inserir coordenadas")
    
    coordinates = coordinates.replace(" ", "")

    if not (coordinates.startswith("(") and coordinates.endswith(")")):
        raise ValueError("Formato inválido de coordenadas: deve começar e terminar com parênteses")
    
    pairs = coordinates.split("),(")
    pairs[0] = pairs[0].replace("(", "")
    pairs[-1] = pairs[-1].replace(")", "")

    parsed_coords = []
   
    for pair in pairs:
        values = pair.split(",")
        if len(values) not in [2, 3]:
            raise ValueError("Formato inválido de coordenadas: cada tupla deve conter exatamente duas ou três coordenadas (x, y) ou (x, y, z)")
        try:
            # Processa coordenadas com dois ou três valores
            if len(values) == 2:
                x, y = float(values[0]), float(values[1])
                parsed_coords.append((x, y))
            elif len(values) == 3:
                x, y, z = float(values[0]), float(values[1]), float(values[2])
                parsed_coords.append((x, y, z))
        except ValueError:
            raise ValueError("Coordenadas devem ser números válidos")
        
        # por enquanto, vamos arredondar as coordenadas para inteiros
        #x, y = map(round, (x, y))
        

    if (type == "Point" and len(parsed_coords) > 1):
        raise ValueError("O objeto Point requer apenas uma coordenada")
    elif (type == "Line" and len(parsed_coords) > 2):
        raise ValueError("O objeto Line requer apenas duas coordenadas")
    elif (type == "Wireframe" and len(parsed_coords) < 3):
        raise ValueError("O objeto Wireframe requer pelo menos três coordenadas")
    elif (type == "Line" and len(parsed_coords) < 2):
        raise ValueError("O objeto Line requer pelo menos duas coordenadas")
    elif (type == "Curve" and len(parsed_coords) < 4):
        raise ValueError("O objeto Curve requer pelo menos quatro coordenadas")
        
    return parsed_coords

def parse_factor(factor: str) -> str:
    if not factor.strip():
        raise ValueError("Favor inserir fator")
    
    if not factor.isdigit():
        raise ValueError("Fator deve ser um número")
    
    return float(factor)

def parse_angle(angle: str) -> Tuple[float, float, float]:
    if not angle.strip():
        raise ValueError("Favor inserir ângulos")
        
    print("Angles received: ", angle)
        
    angle = angle.replace(" ", "")
    components = angle.split(",")
    angles = {"x": None, "y": None, "z": None}
        
    for component in components:
        if "=" not in component:
            raise ValueError("Formato inválido de ângulo: deve ser no formato 'x=valor, y=valor, z=valor'")
        axis, value = component.split("=")
        if axis not in angles:
            raise ValueError(f"Eixo inválido: {axis}. Apenas 'x', 'y' e 'z' são permitidos")
        try:
            angles[axis] = float(value.strip('"'))
        except ValueError:
            raise ValueError(f"Valor inválido para o eixo {axis}: deve ser um número")
        
    return tuple(angles[axis] if angles[axis] is not None else 0.0 for axis in ["x", "y", "z"])

def homogeneo(vertices: List[Tuple[int, int]]) -> List[Tuple[int, int, int]]:
    ##print(vertices)
    return np.array([(x[0], x[1], 1) for x in vertices]).T

def translate(vertices: List[Tuple[int, int]], shift: Tuple[int, int]) -> List[Tuple[int, int]]:
    matrix1 = homogeneo(vertices)
    translation_mtx = [[1, 0, shift[0]], [0, 1, shift[1]], [0, 0, 1]]
    result = np.dot(translation_mtx, matrix1)
    return [(x, y) for x, y, _ in result.T]

def escalate(vertices: List[Tuple[int, int]], factor: Tuple[float, float]) -> List[Tuple[int, int]]:
    matrix1 = homogeneo(vertices)
    escalation_mtx = [[factor[0], 0, 0], [0, factor[1], 0], [0, 0, 1]]
    result = np.dot(escalation_mtx, matrix1)
    return [(x, y) for x, y, _ in result.T]

def rotate(vertices: List[Tuple[int, int]], angle: float) -> List[Tuple[int, int]]:
    rad = np.radians(angle)
    matrix1 = homogeneo(vertices)
    rotation_mtx = [[np.cos(rad), -np.sin(rad), 0], [np.sin(rad), np.cos(rad), 0], [0, 0, 1]]
    result = np.dot(rotation_mtx, matrix1)
    return [(x, y) for x, y, _ in result.T]

def get_id_from_info(info: str) -> str:
    return info.split()[0][1:-1]