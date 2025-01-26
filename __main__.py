import os
import json
import time
import dotenv
import requests
from tqdm import tqdm
from aggregate import aggregate
from genre_analyzer import analyze_genre
from get_track_data import get_track_data
from get_bearer_token import get_bearer_token
from disp_hist import create_histogram_by_genres

dotenv.load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

DOWNLOAD_TRACKS = False # Don't change this unless you know what you're doing

def combine_json_files(input_dir, output_file):
    """
    Combine all .json files in `input_dir` (each containing a list) into a single list 
    and save them into `output_file`.
    """
    if os.path.exists(output_file):
        print(f"{output_file} already exists. Skipping combination step.")
        return

    combined_data = []

    for filename in os.listdir(input_dir):
        if filename.endswith(".json"):
            file_path = os.path.join(input_dir, filename)
            with open(file_path, "r", encoding="utf-8") as file:
                try:
                    data = json.load(file)
                    if isinstance(data, list):
                        combined_data.extend(data)
                    else:
                        print(f"Skipping {filename}: Not a list")
                except json.JSONDecodeError as e:
                    print(f"Skipping {filename}: Invalid JSON - {e}")

    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(combined_data, output, indent=4)

    print(f"Combined history saved to {output_file}")


def download_track_data(combined_history_file, trackdata_dir, bearer_token):
    """
    Go through the combined history JSON and download track data 
    for each unique track_id if it doesn't already exist in `trackdata_dir`.
    Includes a basic backoff-retry strategy for 429 errors.
    """
    if not os.path.exists(combined_history_file):
        print(f"{combined_history_file} not found. Nothing to download.")
        return

    with open(combined_history_file, "r", encoding="utf-8") as ext_history:
        json_history = json.load(ext_history)

        total_tracks = len(json_history)
        print(f"Starting track data download for {total_tracks} tracks...")
        
        for _, json_item in enumerate(tqdm(json_history, desc="Progress", unit="track")):
            if json_item['spotify_track_uri']:
                track_id = json_item['spotify_track_uri'].split(":")[2]

                track_file = os.path.join(trackdata_dir, f"{track_id}.json")
                if os.path.exists(track_file):
                    continue

                backoff_seconds = 1
                max_retries = 5

                for attempt in range(1, max_retries + 1):
                    try:
                        trackdata = get_track_data(track_id=track_id, bearer_token=bearer_token)

                        with open(track_file, "w", encoding="utf-8") as f:
                            json.dump(trackdata, f, indent=4)
                        
                        break

                    except requests.exceptions.HTTPError as err:
                        if err.response is not None and err.response.status_code == 429:
                            retry_after = err.response.headers.get("Retry-After", backoff_seconds)
                            retry_after = float(retry_after)
                            tqdm.write(f"Rate-limited. Retrying after {retry_after} seconds...")
                            time.sleep(retry_after)
                        else:
                            tqdm.write(f"HTTP error on attempt {attempt}: {err}")
                            time.sleep(backoff_seconds)
                    except Exception as e:
                        tqdm.write(f"Error on attempt {attempt}: {e}")
                        time.sleep(backoff_seconds)

                    backoff_seconds *= 2
                
                time.sleep(0.1)

        print("Track data download complete!")


if __name__ == "__main__":
    directory = "./spotanalyze/history"
    output_file = "./spotanalyze/combined_history.json"
    trackdata_dir = "./spotanalyze/trackdata"

    combine_json_files(directory, output_file)

    if DOWNLOAD_TRACKS:
        bearer_token = get_bearer_token(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        download_track_data(output_file, trackdata_dir, bearer_token)

    aggregate()
    create_histogram_by_genres()
    
    while True:
        genre = input("Enter the genre to analyze: ")
        window_size = int(input("Enter the sliding window size in days: "))
        mode = input("Relative mode? (y/N): ").strip().lower()
        if mode == 'y':
            analyze_genre(genre, window_size, relative=True)
        else:
            analyze_genre(genre, window_size, relative=False)
