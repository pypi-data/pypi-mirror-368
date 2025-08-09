import requests

is_gh = True
url = "https://stainlesteel.github.io/squid-game-api"

def set_hostname(string):
    global url
    global is_gh
    if validators.hostname(string.lower()):
        if not string.lower() == "github.io":
            is_gh = True
            string.lower() == url
        else:
            is_gh = False
            string.lower() == url
        if url.endswith("/"):
            url.removesuffix("/")
    else:
        return("sg-api.py: Not a valid hostname")

def characters(season, number, field=None):
    global is_gh
    global url
    if is_gh == True:
        no_s3 = True
    else:
        no_s3 = False
    mustard = f"{number:03}"
    ketchup = f"{season}"
    if season == 3 and is_gh == True:
        actual_url = f"{url}/s2/characters/{mustard}.json"
    else:
        actual_url = f"{url}/s{ketchup}/characters/{mustard}.json"
    resp = requests.get(actual_url)
    data = resp.json()
    if field is not None:
        return(f"{data[field]}")
    else:
        items = [f"{key}:{value}" for key, value in data.items()]
        return "\n".join(items)
 

def episodes(season, number, field=None):
    global is_gh
    global url
    if is_gh == True:
        no_s3 = True
    else:
        no_s3 = False
    mustard = f"{number:03}"
    ketchup = f"{season}" 
    if season == 3 and is_gh == True:
        actual_url = f"{url}/s2/episodes-s3/{mustard}.json"
    else:
        actual_url = f"{url}/s{ketchup}/episodes/{mustard}.json"
    resp = requests.get(actual_url)
    data = resp.json()
    if field is not None:
        return(f"{data[field]}")    
    else:    
        items = [f"{key}:{value}" for key, value in data.items()]
        return "\n".join(items)

