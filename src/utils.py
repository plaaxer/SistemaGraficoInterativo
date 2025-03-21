#todo: adaptar isso para mais tipos de entradas

def parse_coordinates(coordinates: str):
    if not coordinates or coordinates == "":
        raise ValueError("Favor inserir coordenadas")
    
    coords = coordinates.split(", ")

    int_coords = []

    for i in range(0, len(coords), 2):
        x, y = coords[i], coords[i + 1]
        if not x.isdigit() or not y.isdigit():
            raise ValueError("Coordenadas inválidas")
        int_coords.append((int(x), int(y)))
        
    return int_coords