import webbrowser

client_id = "a4e8730f-7a32-4ab3-8211-8714c97daeb6"
redirect_uri = "https://breakoutai.tech"

login_url = f"https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}"
webbrowser.open(login_url)
