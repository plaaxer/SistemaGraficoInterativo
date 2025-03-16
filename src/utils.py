def parse_coordinates(coordinates: str):
    if not coordinates:
        return None
    
    coords = coordinates.split(", ")

    for num in coords:
        if not num.isdigit():
            raise ValueError("Coordenadas inválidas")
    return coords