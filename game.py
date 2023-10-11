"""

HERE ARE ALL THE SQL COMMANDS TO EDIT THE DATABASE:

alter table game add target varchar(10);
alter table game add attempts int(8);
alter table game add difficulty int(8);
alter table game rename column co2_consumed to co2_limit;

"""

import user
import geopy
import mysql.connector
from geopy.distance import geodesic

connection = mysql.connector.connect(
    host='127.0.0.1',
    port='3306',
    database='flight_game',
    user='dbuser',
    password='1234',
    autocommit=True
)


# This function asks for the screen_name, checks if it already exists
# and asks if the user wants to continue or start a new game
def username():
    while True:
        print('\n' * 100)
        user_name = str(input("Hi, enter your username: "))
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT screen_name FROM game WHERE screen_name = '" + user_name + "'")

        print(f"Are you sure that the username '{user_name}' is correct?\n"
              "1. Yes\n"
              "2. No\n")

        match user.choose_option():
            case 1:
                if cursor.rowcount == 0:
                    cursor.execute("SELECT COUNT(id) from game")
                    last_id = cursor.fetchone()
                    total_id = last_id[0] + 1

                    cursor.execute("INSERT INTO game (id ,co2_limit, co2_budget, location, screen_name, target, attempts, difficulty) "
                                   f"VALUES ({total_id},'999', '10000', NULL, '{user_name}', NULL, NULL, NULL)")

                    print("Username", user_name, "added to the database.\n")
                    return False, user_name
                else:
                    print("Welcome back", user_name + '!\n')
                    cursor.execute(f"SELECT target FROM game WHERE screen_name = '{user_name}'")
                    game_session = cursor.fetchone()

                    if game_session[0] is not None:
                        while True:
                            print("Do you wish to continue your previous game?\n"
                                  "1. Yes\n"
                                  "2. No\n")

                            match user.choose_option():
                                case 1:
                                    input("Press any key to continue")
                                    return True, user_name
                                case 2:
                                    break

                    input("Press any key to continue")
                    return False, user_name
            case 2:
                print("Returning to the menu...\n")
            case _:
                print("Invalid option!\n")


# This function initializes a new game
def init_game(settings, screen_name):
    # settings[0] is difficulty, settings[1] is distance

    value = False
    location, coords = list(range(2)), list(range(2))
    match settings[0]:
        case 0:
            airport_type = "large_airport"
        case 1:
            airport_type = "large_airport, medium_airport"
        case 2:
            airport_type = "large_airport, medium_airport, small_airport"

    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT ident, name, latitude_deg, longitude_deg FROM airport "
                   f"WHERE type IN ('{airport_type}') ORDER BY RAND() LIMIT 1")
    location[0] = cursor.fetchall()
    for row in location[0]:
        coords[0] = [row[2], row[3]]
        cursor.execute(f"UPDATE game SET location = '{row[0]}' WHERE screen_name = '{screen_name}'")

    while True:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT ident, name, latitude_deg, longitude_deg FROM airport "
                       f"WHERE type IN ('{airport_type}') ORDER BY RAND() LIMIT 1")
        location[1] = cursor.fetchall()
        for row in location[1]:
            coords[1] = [row[2], row[3]]

        match settings[1]:
            case 0:
                if 1000 <= geodesic(coords[0], coords[1]).km < 5000:
                    value = True
            case 1:
                if 5000 <= geodesic(coords[0], coords[1]).km < 12000:
                    value = True
            case 2:
                if 12000 <= geodesic(coords[0], coords[1]).km:
                    value = True

        if value:
            for row in location[1]:
                cursor.execute(f"UPDATE game SET target = '{row[0]}' WHERE screen_name = '{screen_name}'")
            print(location, geodesic(coords[0], coords[1]).km)
            break


# This function takes care of the navigation during the game
def navigation_system():
    origin = geopy.Point(lat1, lon1)
    destination = geodesic(kilometers=d).destination(origin, b)

    lat2, lon2 = destination.latitude, destination.longitude


def main():
    user_info = username()
    settings = user.new_game()
    if not user_info[0]:
        init_game(settings, user_info[1])

    navigation_system(settings[0], user_info[1])


main()
