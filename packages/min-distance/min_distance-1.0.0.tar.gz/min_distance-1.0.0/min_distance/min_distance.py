import math

def deg_to_rad(degree: float) -> float:
    """Convert degree to radians."""
    return degree * math.pi / 180

def calculate_min_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the minimum distance between two points on the Earth specified by latitude and longitude.

    Parameters:
        lat1, lon1: Latitude and Longitude of point 1 in decimal degrees.
        lat2, lon2: Latitude and Longitude of point 2 in decimal degrees.

    Returns:
        Distance in kilometers between the two points.
    """
    earth_radius = 6371  # Radius of the Earth in km

    dlat = deg_to_rad(lat2 - lat1)
    dlon = deg_to_rad(lon2 - lon1)

    a = (math.sin(dlat / 2) ** 2 +
         math.cos(deg_to_rad(lat1)) *
         math.cos(deg_to_rad(lat2)) *
         math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius * c
