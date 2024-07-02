from flask import Flask, request, redirect
import requests
import os

app = Flask(__name__)

# Load environment variables
upstox_client_id = os.getenv('UPSTOX_API_KEY', 'e154869b-0ffe-4c95-9103-86b8200cc5ca')
upstox_client_secret = os.getenv('UPSTOX_API_SECRET', 'n2x3go8trh')
redirect_uri = os.getenv('REDIRECT_URI', 'http://127.0.0.1:8000/callback')

# Ensure environment variables are loaded
print(f"Upstox Client ID: {upstox_client_id}")
print(f"Upstox Client Secret: {upstox_client_secret}")
print(f"Redirect URI: {redirect_uri}")

@app.route('/login')
def login():
    params = {
        'client_id': upstox_client_id,
        'response_type': 'code',
        'redirect_uri': "http://127.0.0.1:8000/callback",
        'scope': 'profile',
    }

    authorization_url = f'https://api.upstox.com/v2/login/authorization/dialog?response_type=code&client_id={upstox_client_id}&redirect_uri={redirect_uri}'
    print(f"Redirecting to: {authorization_url}")
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    authorization_code = request.args.get('code')
    if authorization_code:
        print(f"Authorization code received: {authorization_code}")
        token_url = 'https://api.upstox.com/v2/login/authorization/token'
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'code': authorization_code,
            'client_id': upstox_client_id,
            'client_secret': upstox_client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }
        response = requests.post(token_url, headers=headers, data=data)
        print(f"Token URL: {token_url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response JSON: {response.json()}")
        return response.json()
    return 'Authorization code not found'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
