import requests

url = 'https://api.upstox.com/v2/login/authorization/token'
headers = {
    'accept': 'application/json',
    'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
    'code': '{your_code}',
    'client_id': '{your_client_id}',
    'client_secret': '{your_client_secret}',
    'redirect_uri': '{your_redirect_url}',
    'grant_type': 'authorization_code',
}

response = requests.post(url, headers=headers, data=data)

print(response.status_code)
print(response.json())


url = 'https://api.upstox.com/v2/historical-candle/intraday/NSE_EQ%7CINE848E01016/30minute'
headers = {
    'Accept': 'application/json'
}


response = requests.get(url, headers=headers)

# Check the response status
if response.status_code == 200:
    # Do something with the response data (e.g., print it)
    print(response.json())
else:
    # Print an error message if the request was not successful
    print(f"Error: {response.status_code} - {response.text}")
