import requests
import random

API_KEY = 'ghsh_zLqfT86QRFc2mogqzoSZAZIJUPK8JEjhQ6LPXgGnnaN-2Y0-h1VzakNWk889cu1Kl3WXDgjhd6LPVjGaW9OwK3vuQ72DsnPiKaWuh2Ns-4iKa0tKRkEDL3TZHYx'
ENDPOINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': f'Bearer {API_KEY}'}


def get_cafes(location):
    try:
        cafes = []
        PARAMETERS = {'term': 'cafe', 'location': location, 'limit': 50}

        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
        businesses = response.json()['businesses']
        for business in businesses:
            name = business['name']
            address = ' '.join(business['location']['display_address'])
            image_url = business['image_url']
            url = business['url']
            attending = random.randint(0, 10)
            cafes.append([name, address, image_url, url, attending])
        random.shuffle(cafes)
    except:
        cafes = []
        PARAMETERS = {'term': 'cafe', 'location':'New York','limit': 50}

        response = requests.get(url=ENDPOINT, params=PARAMETERS, headers=HEADERS)
        businesses = response.json()['businesses']
        for business in businesses:
            name = business['name']
            address = ' '.join(business['location']['display_address'])
            image_url = business['image_url']
            url = business['url']
            attending = random.randint(0, 10)
            cafes.append([name, address, image_url, url, attending])
        random.shuffle(cafes)
    return cafes