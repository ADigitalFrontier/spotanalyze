import base64
import requests

def get_bearer_token(client_id, client_secret):
    """
    Gets a Spotify Bearer Token using the Client Credentials Flow.
    :param client_id: Your Spotify App's Client ID.
    :param client_secret: Your Spotify App's Client Secret.
    :return: A Bearer Token string.
    """
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{client_id}:{client_secret}'.encode()).decode()}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        raise RuntimeError(f"Failed to get token: {response.status_code}, {response.text}")