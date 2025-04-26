import os
from geopy.geocoders import Nominatim


def calcBbox():
    source = os.environ.get('SOURCE')
    dest = os.environ.get('DEST')

    geolocator = Nominatim(user_agent = "geoapp")
    start = geolocator.geocode(source)
    end = geolocator.geocode(dest)
    os.environ["START"] = start
    os.environ["END"] = end
    starting_bbox = [start.longitude - 0.05, start.latitude - 0.05, start.longitude + 0.05, start.latitude + 0.05]
    ending_bbox = [end.longitude - 0.05, end.latitude - 0.05, end.longitude + 0.05, end.latitude + 0.05]
    middle_bbox = [min(start.longitude, end.longitude) - 0.09, min(start.latitude, end.latitude) - 0.09, max(start.longitude, end.longitude) - 0.09, max(start.latitude, end.latitude) - 0.09]

    starting_bbox_str = ",".join(starting_bbox)
    ending_bbox_str = ",".join(ending_bbox)
    middle_bbox_str = ",".join(middle_bbox)
    os.environ["SOURCE_BBOX"] = starting_bbox_str
    os.environ["DEST_BBOX"] = ending_bbox_str
    os.environ["MIDDLE_BBOX"] = middle_bbox_str

if __name__ == "__main__":
    calcBbox()