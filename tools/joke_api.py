import requests

def get_joke():
    url = "https://official-joke-api.appspot.com/random_joke"
    response = requests.get(url, timeout=10)
    data = response.json()
    return data.get("setup", ""), data.get("punchline", "")
