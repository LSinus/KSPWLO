import os
from geopy.geocoders import Nominatim

def get_long_margin(lat):
        import math
        return (360*10)/(2*math.pi*math.cos(lat*math.pi/180)*6371)

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
    
    lat_margin = 0.09
    long_margin = 0.09
    min_lat = min(start.latitude, end.latitude) - lat_margin
    max_lat = max(start.latitude, end.latitude) + lat_margin
    min_lon = min(start.longitude, end.longitude) - long_margin
    max_lon = max(start.longitude, end.longitude) + long_margin
    middle_bbox = [min_lon, min_lat, max_lon, max_lat] 
    
    lat_margin = 0.09
    long_margin = 0.09
    min_lat = start.latitude - lat_margin
    max_lat = start.latitude + lat_margin
    min_lon = start.longitude - long_margin
    max_lon = start.longitude + long_margin

    starting_bbox = [min_lon, min_lat, max_lon, max_lat]
    long_margin = get_long_margin(end.latitude)
    min_lat = end.latitude - lat_margin
    max_lat = end.latitude + lat_margin
    min_lon = end.longitude - long_margin
    max_lon = end.longitude + long_margin
    ending_bbox = [min_lon, min_lat, max_lon, max_lat]
    
    

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