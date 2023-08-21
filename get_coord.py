from geopy.geocoders import Photon
geolocator = Photon(user_agent="measurements")

def get_location(place):
    location = geolocator.geocode(place)
    if location:
        return str(location)
    else:
        return None