"""

HERE ARE ALL THE SQL COMMANDS TO EDIT THE DATABASE:

alter table game add target varchar(10);
alter table game add attempts int(8);
alter table game add difficulty int(8);
alter table game add distance int(8);
alter table game rename column co2_consumed to co2_limit;

"""

import info
import user
import math
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


# This function asks for the screen_name and links it to its data
def check_username():
    while True:
        print('\n' * 100)
        user_name = str(input("Hi, enter your username: "))

        print(f"Are you sure that the username '{user_name}' is correct?\n"
              "1. Yes\n"
              "2. No\n")

        match user.choose_option():
            case 1:
                return username_data(user_name)
            case 2:
                print("Returning to the menu...\n")
            case _:
                print("Invalid option!\n")
                input("Press any key to continue")


# This functions checks the data from the username
def username_data(user_name):
    cursor = connection.cursor(buffered=True)
    cursor.execute("SELECT screen_name FROM game WHERE screen_name = '" + user_name + "'")

    if cursor.rowcount == 0:
        cursor.execute("SELECT COUNT(id) from game")
        last_id = cursor.fetchone()
        total_id = last_id[0] + 1

        cursor.execute(
            "INSERT INTO game (id ,co2_limit, co2_budget, location, screen_name, target, attempts, difficulty) "
            f"VALUES ({total_id},'999', '10000', NULL, '{user_name}', NULL, NULL, NULL)")

        print("Username", user_name, "added to the database.\n")

        while True:
            print("Do you want information about the game?\n"
                  "1. Yes\n"
                  "2. No\n")
            match user.choose_option():
                case 1:
                    info.tutorial()
                    break
                case 2:
                    print("Continuing to the settings...")
                    break
                case _:
                    print("Invalid option!\n")

        input("Press any key to continue")
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
                        cursor.execute(
                            f"UPDATE game SET location = NULL, target = NULL WHERE screen_name = '{user_name}'")
                        break

        input("Press any key to continue")
        return False, user_name


# This function initializes a new game
def init_game(settings, user_name):
    value = False
    location, coords = list(range(2)), list(range(2))

    cursor = connection.cursor(buffered=True)
    cursor.execute(f"UPDATE game SET difficulty = {settings[0]}, attempts = 0, distance = 0 "
                   f"WHERE screen_name = '{user_name}'")

    match settings[0]:
        case 0:
            airport_type = "'large_airport'"
        case 1:
            airport_type = "'large_airport' OR TYPE = 'medium_airport'"
        case 2:
            airport_type = "'large_airport' OR TYPE = 'medium_airport' OR TYPE = 'small_airport'"

    cursor.execute("SELECT ident, name, latitude_deg, longitude_deg FROM airport "
                   f"WHERE type = {airport_type} ORDER BY RAND() LIMIT 1")
    location[0] = cursor.fetchall()
    for row in location[0]:
        coords[0] = [row[2], row[3]]
        cursor.execute(f"UPDATE game SET location = '{row[0]}' WHERE screen_name = '{user_name}'")

    while True:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT ident, name, latitude_deg, longitude_deg FROM airport "
                       f"WHERE type = {airport_type} ORDER BY RAND() LIMIT 1")
        location[1] = cursor.fetchall()
        for row in location[1]:
            coords[1] = [row[2], row[3]]

        match settings[1]:
            case 0:
                if 1000 <= geodesic(coords[0], coords[1]).km < 5000:
                    value = True
            case 1:
                if 5000 <= geodesic(coords[0], coords[1]).km < 11000:
                    value = True
            case 2:
                if 11000 <= geodesic(coords[0], coords[1]).km:
                    value = True

        if value:
            for row in location[1]:
                cursor.execute(f"UPDATE game SET target = '{row[0]}' WHERE screen_name = '{user_name}'")
            print(location, geodesic(coords[0], coords[1]).km)
            break


# This function takes care of the navigation during the game
def navigation_system(user_name):
    airport_type = str()
    attempts = score = travel_distance = int()
    direction = distance = float()
    text, temp_coords = list(range(2)), list(range(2))
    coords, location = list(range(3)), list(range(3))
    # Index 0 = current airport, Index 1 = target airport, Index 2 = next airport
    cursor = connection.cursor(buffered=True)

    cursor.execute(f"SELECT attempts FROM game WHERE screen_name = '{user_name}'")
    for data in cursor.fetchall():
        attempts = data[0]

    cursor.execute(f"SELECT distance FROM game WHERE screen_name = '{user_name}'")
    for data in cursor.fetchall():
        travel_distance = data[0]

    for i in range(2):
        if i == 0:
            value = 'location'
        else:
            value = 'target'
        cursor.execute(f"SELECT ident, name, latitude_deg, longitude_deg FROM airport "
                       f"LEFT JOIN game ON game.{value} = ident WHERE game.screen_name = '{user_name}'")
        result = cursor.fetchall()
        for row in result:
            location[i] = [row[0], row[1], row[2], row[3]]
            coords[i] = [row[2], row[3]]

    cursor.execute(f"SELECT difficulty FROM game WHERE screen_name = '{user_name}'")
    value = cursor.fetchone()
    difficulty = value[0]

    match difficulty:
        case 0:
            airport_type = "'large_airport'"
        case 1:
            airport_type = "'large_airport' OR TYPE = 'medium_airport'"
        case 2:
            airport_type = "'large_airport' OR TYPE = 'medium_airport' OR TYPE = 'small_airport'"

    print('\n' * 100)
    print("You will be given directions as you move.\n")
    while True:
        for i in range(2):
            if i == 0:
                text[0] = "In order to travel you must select a direction (degrees).\n"
                text[1] = ("The direction can be any float number and is measured in degrees.\n"
                           "However, we recommend sticking to integers from 0º to 360º.\n"
                           "The angle of the direction increments in a clockwise motion.\n"
                           "\n0º is North, 90º is East, 180º is South and 270º is West.\n")
            else:
                text[0] = "In addition, you must also select a distance (kilometers).\n"
                text[1] = ("The distance can be any float number and is measured in kilometers.\n"
                           "However, we recommend sticking to positive integers.\n")

            while True:
                print(f"You are now in: {location[0][1]}\n"
                      f"You must reach: {location[1][1]}\n")
                print(text[0])
                print("Write 'help' for additional information.\n"
                      "Write 'quit' to quit the program.\n")
                option = input("Insert a value: ")

                if option.lower() == 'help':
                    print('\n' * 100)
                    print(text[1])
                elif option.lower() == 'quit':
                    quit()
                else:
                    try:
                        float(option)
                        break
                    except ValueError:
                        print("Invalid option!\n")

            if i == 0:
                direction = float(option)
            else:
                distance = float(option)

        destination = geodesic(kilometers=distance).destination(coords[0], direction)
        temp_coords[0] = [destination.latitude, destination.longitude]

        cursor.execute("SELECT ident, name, latitude_deg, longitude_deg FROM airport "
                       f"WHERE type = {airport_type}")
        airports = cursor.fetchall()

        length = 1000
        # Placeholder value for now
        for row in airports:
            temp_coords[1] = [row[2], row[3]]

            if math.dist(temp_coords[0], temp_coords[1]) < length and math.dist(temp_coords[0], temp_coords[1]) != 0:
                length = math.dist(temp_coords[0], temp_coords[1])
                coords[2] = [row[2], row[3]]
                location[2] = [row[0], row[1], row[2], row[3]]

        attempts += 1
        travel_distance += int(geodesic(coords[0], coords[2]).km)

        print('\n' * 100)
        if location[2] == location[1]:
            # Finish the game
            match difficulty:
                case 0:
                    score = int(2000 / travel_distance * 10000)
                case 1:
                    score = int(3000 / travel_distance * 10000)
                case 2:
                    score = int(4500 / travel_distance * 10000)

            cursor.execute("UPDATE game SET co2_limit = NULL, location = NULL, target = NULL, attempts = NULL, "
                           f"difficulty = NULL, distance = NULL WHERE screen_name = '{user_name}'")
            print(f"You landed at {location[2][1]}")
            return difficulty, attempts, score

        if location[2] == location[0]:
            print("You didn't find any airport in that direction!\n"
                  f"Therefore, you have returned to {location[0][1]}.\n"
                  "\nYou are at the same distance from your target.\n")
        else:
            print(f"You landed at {location[2][1]}")
            location[0] = location[2]
            cursor.execute(f"UPDATE game SET location = '{location[0][0]}', attempts = {attempts}, "
                           f"distance = {travel_distance} WHERE screen_name = '{user_name}'")

            if geodesic(coords[2], coords[1]).km < geodesic(coords[0], coords[1]):
                print("\nYou are getting closer to your target.\n")
            else:
                print("\nYou are getting farther from your target.\n")

            coords[0] = coords[2]


# This function is responsible for the end-game information
def end_game(settings, user_name):
    # settings[0] is difficulty, settings[1] is attempts, settings[2] is score
    print("Congratulations", user_name +
          "! You have reached your destination!\n"
          "It took you", settings[1], "attempts!\n"
          "\nYou score was:", settings[2], '\n')

    match settings[0]:
        case 0:
            print("Difficulty: Easy\n")
        case 1:
            print("Difficulty: Normal\n")
        case 2:
            print("Difficulty: Hard\n")

    while True:
        print("Do you want to continue playing?\n"
              "1. Yes\n"
              "2. No\n")

        match (user.choose_option()):
            case 1:
                return True
            case 2:
                info.game_credits()
                print("Exiting game...")
                break
            case _:
                print("Invalid option!\n")


def main():
    continue_game = False
    user_info = check_username()
    # user.new_game[0] is difficulty, user.new_game[1] is distance
    while True:
        if not user_info[0] or continue_game is True:
            init_game(user.new_game(), user_info[1])

        if end_game(navigation_system(user_info[1]), user_info[1]):
            continue_game = True
        else:
            break


main()
