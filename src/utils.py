#todo: adaptar isso para mais tipos de entradas

def parse_coordinates(coordinates: str):
    if not coordinates or coordinates == "":
        raise ValueError("Favor inserir coordenadas")
    
    coords = coordinates.split(", ")

    int_coords = []

    for num in coords:
        if not num.isdigit():
            raise ValueError("Coordenadas inválidas")
        int_coords.append(int(num))
        
    return int_coords