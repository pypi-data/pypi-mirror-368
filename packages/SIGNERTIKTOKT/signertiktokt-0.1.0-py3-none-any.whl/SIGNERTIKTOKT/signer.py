import requests

def make_headers(url, payload):
    api_url = "https://fghgghgfhgfth.pythonanywhere.com/make_headers"
    data = {
        "params": url,
        "payload": payload
    }
    response = requests.post(api_url, json=data)
    return response.json()
