from geopy.distance import geodesic

coords = [0, 0]

print(geodesic(kilometers=800).destination(coords, -45).format_decimal())