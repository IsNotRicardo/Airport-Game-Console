"""

HERE ARE ALL THE SQL COMMANDS TO EDIT THE DATABASE:

alter table game add target varchar(10);
alter table game add attempts int(8);
alter table game add difficulty int(8);
alter table game rename column co2_consumed to co2_limit;

"""

import geopy
import mysql
from geopy.distance import geodesic


# This function asks for the screen_name and checks if it already exists
def username():
    return False


# This function initializes a new game
def init_game(settings):
    # settings[0] is difficulty, settings[1] is distance
    print(settings[0], settings[1])


# This function takes care of the navigation during the game
def navigation_system():
    origin = geopy.Point(lat1, lon1)
    destination = geodesic(kilometers=d).destination(origin, b)

    lat2, lon2 = destination.latitude, destination.longitude
