import requests

def solve_captcha(did, iid):
    url = "https://fghgghgfhgfth.pythonanywhere.com/solve"
    data = {
        "did": did,
        "iid": iid
    }
    response = requests.post(url, json=data)
    return response.json()
