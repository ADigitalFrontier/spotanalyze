import json
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

def analyze_genre(genre_filter, window_size_days=7, relative=False):
    with open("mydata.json", "r", encoding="utf-8") as file:
        aggregated_data = json.load(file)

    track_rows = []
    for track_id, details in aggregated_data.items():
        genre_list = [g.strip() for g in details["genres"].split(",")]
        for play_instance in details["play_instances"]:
            start = datetime.fromisoformat(play_instance["start"])
            end = datetime.fromisoformat(play_instance["end"])
            duration_minutes = (end - start).total_seconds() / 60

            track_rows.append({
                "track_id": track_id,
                "start": start,
                "duration_minutes": duration_minutes,
                "genres": genre_list
            })

    df_tracks = pd.DataFrame(track_rows)

    flat_data = []
    for track_id, details in aggregated_data.items():
        genre_list = [g.strip() for g in details["genres"].split(",")]
        for play_instance in details["play_instances"]:
            start = datetime.fromisoformat(play_instance["start"])
            end = datetime.fromisoformat(play_instance["end"])
            duration_minutes = (end - start).total_seconds() / 60

            for genre in genre_list:
                flat_data.append({
                    "Genre": genre,
                    "Start": start,
                    "Duration (minutes)": duration_minutes
                })

    df_flat = pd.DataFrame(flat_data)

    genre_lower = genre_filter.lower()

    all_starts = pd.concat([df_tracks['start'], df_flat['Start']])
    if all_starts.empty:
        print("No data available at all.")
        return

    start_time = all_starts.min()
    end_time = all_starts.max()

    window_size = timedelta(days=window_size_days)
    current_time = start_time
    time_bins = []
    while current_time <= end_time:
        time_bins.append(current_time)
        current_time += window_size

    time_labels = []
    plot_values = []

    for start_bin in time_bins:
        end_bin = start_bin + window_size
        time_labels.append(start_bin.strftime("%Y-%m-%d"))

        if not relative:
            window_data = df_flat[
                (df_flat["Genre"].str.lower() == genre_lower) &
                (df_flat["Start"] >= start_bin) &
                (df_flat["Start"] < end_bin)
            ]
            total_playtime_minutes = window_data["Duration (minutes)"].sum()
            plot_values.append(total_playtime_minutes)

        else:
            window_df = df_tracks[
                (df_tracks["start"] >= start_bin) &
                (df_tracks["start"] < end_bin)
            ]

            total_window_minutes = window_df["duration_minutes"].sum()

            if total_window_minutes == 0:
                plot_values.append(0)
                continue

            genre_mask = window_df["genres"].apply(
                lambda g_list: any(g.lower() == genre_lower for g in g_list)
            )
            genre_window_minutes = window_df.loc[genre_mask, "duration_minutes"].sum()

            fraction = genre_window_minutes / total_window_minutes
            percentage = fraction * 100
            plot_values.append(percentage)

    if not relative:
        y_axis_title = "Total Playtime (minutes)"
        title_text = f"Nominal Playtime for Genre '{genre_filter}' Over Time ({window_size_days}-Day Windows)"
    else:
        y_axis_title = "Percentage of Listening (%)"
        title_text = f"Relative Playtime (Fraction) for Genre '{genre_filter}' Over Time ({window_size_days}-Day Windows)"

    fig = px.bar(
        x=time_labels,
        y=plot_values,
        labels={"x": "Time Window", "y": y_axis_title},
        title=title_text,
    )

    fig.update_layout(
        xaxis_title="Time Window",
        yaxis_title=y_axis_title
    )

    fig.show()
