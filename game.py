import geopy
import mysql
from geopy.distance import geodesic


# This function asks for the screen_name and checks if it already exists
def username():
    return False


def init_game():



def navigation_system():
    origin = geopy.Point(lat1, lon1)
    destination = geodesic(kilometers=d).destination(origin, b)

    lat2, lon2 = destination.latitude, destination.longitude
