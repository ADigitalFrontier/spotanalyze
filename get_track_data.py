import os
import json
import requests

def get_track_data(track_id, bearer_token, market="ES"):
    """
    Retrieves data for a track from the Spotify Web API, saving it locally as [track_id].json.
    If the file already exists, returns the local data.
    
    :param track_id: The Spotify track ID.
    :param market:   The market parameter for the track request, default is "ES".
    :param bearer_token: A valid OAuth bearer token for accessing the Spotify Web API.
    :return:         A Python dictionary containing the track's data.
    """
    
    filename = f"{track_id}.json"

    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as file:
            track_data = json.load(file)
        return track_data

    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = {
        "Authorization": f"Bearer {bearer_token}"
    }
    params = {
        "market": market
    }

    response = requests.get(url, headers=headers, params=params)

    if not response.ok:
        raise RuntimeError(
            f"Error fetching track data from Spotify API (status {response.status_code}): {response.text}"
        )

    track_data = response.json()
    return track_data