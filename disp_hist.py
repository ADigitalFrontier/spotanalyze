import json
import pandas as pd
import plotly.express as px

def create_histogram_by_genres():
    with open("mydata.json", "r", encoding="utf-8") as file:
        aggregated_data = json.load(file)

    flat_data = []

    for _track_id, details in aggregated_data.items():
        genres = details["genres"].split(",")
        total_playtime_minutes = details["total_ms_played"] / (1000 * 60)

        for genre in genres:
            flat_data.append({
                "Genre": genre.strip(),
                "Total Playtime (minutes)": total_playtime_minutes,
                "Song": details["song"],
                "Artist": details["artist"]
            })

    df = pd.DataFrame(flat_data)

    fig = px.histogram(
        df,
        x="Genre",
        y="Total Playtime (minutes)",
        histfunc="sum",
        title="Total Playtime by Genre",
        labels={"Total Playtime (minutes)": "Playtime (minutes)", "Genre": "Genres"},
        color="Genre"
    )

    fig.update_layout(
        xaxis_title="Genres",
        yaxis_title="Total Playtime (minutes)",
        showlegend=False,
    )

    fig.show()
