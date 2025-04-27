import os
from geopy.geocoders import Nominatim


def calcBbox():
    source = os.environ.get('SOURCE')
    dest = os.environ.get('DEST')
    print(f"SOURCE: {os.environ.get('SOURCE')}")
    print(f"DEST: {os.environ.get('DEST')}")

    geolocator = Nominatim(user_agent = "geoapp")
    print("SOURCE: " + source)
    print("DEST: "+ dest)

    start = geolocator.geocode(source)
    end = geolocator.geocode(dest)
    print(start)
    print(end)
    os.environ["START_LAT"] = str(start.latitude)
    os.environ["START_LON"] = str(start.longitude)
    os.environ["END_LAT"] = str(end.latitude)
    os.environ["END_LON"] = str(end.longitude)

    starting_bbox = [start.longitude - 0.05, start.latitude - 0.05, start.longitude + 0.05, start.latitude + 0.05]
    ending_bbox = [end.longitude - 0.05, end.latitude - 0.05, end.longitude + 0.05, end.latitude + 0.05]
    middle_bbox = [min(start.longitude, end.longitude) - 0.09, min(start.latitude, end.latitude) - 0.09, max(start.longitude, end.longitude) - 0.09, max(start.latitude, end.latitude) - 0.09]
    # Assicurati che le coordinate siano sempre nel range valido
    # Calcolo del middle_bbox, mantenendo la latitudine e longitudine valide
    # middle_bbox = [
    # max(min(start.longitude, end.longitude) - 0.09, -180),  # Assicurati che la longitudine non sia minore di -180
    # max(min(start.latitude, end.latitude) - 0.09, -90),  # Assicurati che la latitudine non sia minore di -90
    # min(max(start.longitude, end.longitude) + 0.09, 180),  # Assicurati che la longitudine non superi 180
    # min(max(start.latitude, end.latitude) + 0.09, 90)  # Assicurati che la latitudine non superi 90
    # ]

    #due to the fact that evironment variables can only contains string, it is necessary
    #to save the corrd of the bbox in string format separated by a comma
    starting_bbox_str = ",".join(str(coord) for coord in starting_bbox)
    ending_bbox_str = ",".join(str(coord) for coord in ending_bbox)
    middle_bbox_str = ",".join(str(coord) for coord in middle_bbox)
    
    print(starting_bbox_str)
    print(ending_bbox_str)
    print(middle_bbox_str)

    
    # Salva le variabili in un file temporaneo
    with open("env_variables.txt", "w") as f:
        f.write(f"SOURCE_BBOX={','.join(map(str, starting_bbox))}\n")
        f.write(f"DEST_BBOX={','.join(map(str, ending_bbox))}\n")
        f.write(f"MIDDLE_BBOX={','.join(map(str, middle_bbox))}\n")
        f.write(f"START_LAT={start.latitude}\n")
        f.write(f"START_LON={start.longitude}\n")
        f.write(f"END_LAT={end.latitude}\n")
        f.write(f"END_LON={end.longitude}\n")

    # os.environ["SOURCE_BBOX"] = starting_bbox_str
    # os.environ["DEST_BBOX"] = ending_bbox_str
    # os.environ["MIDDLE_BBOX"] = middle_bbox_str

if __name__ == "__main__":
    calcBbox()