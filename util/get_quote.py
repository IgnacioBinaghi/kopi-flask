import requests
 

def get_quote():
    url = 'https://api.quotable.io/random'

    r = requests.get(url)
    quote = r.json()

    return[quote['author'], quote['content']]
