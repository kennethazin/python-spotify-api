from flask import Flask, render_template, request
from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json

app = Flask(__name__)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + (auth_base64),
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"  # Add a "?" here before the query parameters

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)

    # Check if "artists" and "items" exist in the JSON response
    if "artists" in json_result and "items" in json_result["artists"]:
        artists = json_result["artists"]["items"]

        if len(artists) == 0:
            print("No artist with this name exists...")
            return None

        return artists[0]
    else:
        print("Invalid response from Spotify API")
        return None


def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?=country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result


@app.route("/", methods=["GET", "POST"])
def index():
    result = None  # Initialize result with a default value
    error_message = None

    if request.method == "POST":
        artist_name = request.form["artist_name"]
        token = get_token()
        result = search_for_artist(token, artist_name)

        if result:
            artist_id = result["id"]
            tracks = get_songs_by_artist(token, artist_id)

            # Create a list of dictionaries with track names and URLs
            songs = [{'index': idx + 1, 'name': track['name'], 'url': track['external_urls']['spotify']} for idx, track in enumerate(tracks)]

            return render_template("results.html", artist_name=artist_name, songs=songs)
        else:
            error_message = "No artist with this name exists."

    return render_template("index.html", error_message=error_message)

if __name__ == "__main__":
    app.run(debug=True)