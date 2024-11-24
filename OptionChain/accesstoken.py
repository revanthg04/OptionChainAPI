import requests
token_url = "https://api.upstox.com/v2/login/authorization/token"
payload = {
    'code': "zfwx5U",
    'client_id': "a4e8730f-7a32-4ab3-8211-8714c97daeb6",
    'client_secret': "lchagwgll6",
    'redirect_uri': "https://breakoutai.tech",
    'grant_type': 'authorization_code'
}

response = requests.post(token_url, data=payload)
access_token = response.json().get("access_token")
print("Access Token:", access_token)
