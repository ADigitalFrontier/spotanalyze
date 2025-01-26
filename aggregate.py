import json
import pandas as pd
import os
from datetime import timedelta
from tqdm import tqdm

def aggregate():
    if os.path.exists("mydata.json"):
        print("mydata.json already exists. Skipping aggregation step.")
        return

    csv_directory = "./spotanalyze/csvgoeshere"
    csv_files = [f for f in os.listdir(csv_directory) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in /csvgoeshere. Exiting.")
        return

    csv_path = os.path.join(csv_directory, csv_files[0])
    print(f"Using CSV file: {csv_path}")

    ppdata = pd.read_csv(csv_path)

    with open("./spotanalyze/combined_history.json", "r", encoding="utf-8") as file:
        combined_history = json.load(file)

    aggregated_data = {}

    print("Aggregating data...")
    for item in tqdm(combined_history, desc="Processing items", unit="item"):
        spotify_track_uri = item.get("spotify_track_uri")
        ts = pd.to_datetime(item.get("ts"))
        ms_played = item.get("ms_played", 0)

        end_ts = ts + timedelta(milliseconds=ms_played)

        if spotify_track_uri:
            match = ppdata[ppdata["Spotify Track Id"] == spotify_track_uri.split(":")[2]]

            if not match.empty:
                track_id = spotify_track_uri

                timelength = match.iloc[0]["Time"]
                genres = match.iloc[0]["Genres"]
                song = match.iloc[0]["Song"]
                artist = match.iloc[0]["Artist"]

                genres = genres if pd.notna(genres) else "_Unknown_Genres"
                song = song if pd.notna(song) else "_Unknown_Song"
                artist = artist if pd.notna(artist) else "_Unknown_Artist"

                if track_id not in aggregated_data:
                    aggregated_data[track_id] = {
                        "song": song,
                        "artist": artist,
                        "total_ms_played": 0,
                        "play_instances": [],
                        "genres": genres,
                        "timelength": timelength
                    }

                aggregated_data[track_id]["total_ms_played"] += ms_played
                aggregated_data[track_id]["play_instances"].append({
                    "start": ts.isoformat(),
                    "end": end_ts.isoformat()
                })

    with open("mydata.json", "w", encoding="utf-8") as outfile:
        json.dump(aggregated_data, outfile, ensure_ascii=False, indent=4)

    print("Aggregation completed. Data saved to mydata.json.")
