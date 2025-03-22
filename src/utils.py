from typing import List, Tuple
import constants as c

def parse_coordinates(coordinates: str) -> List[Tuple[float, float]]:
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
        
        if not (c.WINDOW_BOUNDS[0][0] <= x <= c.WINDOW_BOUNDS[1][0] and c.WINDOW_BOUNDS[0][1] <= y <= c.WINDOW_BOUNDS[1][1]):
            raise ValueError(f"Coordenadas ({x}, {y}) fora dos limites permitidos: {c.WINDOW_BOUNDS}")
        
        print("Final coordinates: (", x, ", ", y, ")")

        parsed_coords.append((x, y))
    
    return parsed_coords

def translate(vertices: List[Tuple[int, int]], shift: Tuple[int, int]) -> List[Tuple[int, int]]:
    return [(x + shift[0], y + shift[1]) for x, y in vertices]