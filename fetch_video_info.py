from dotenv import load_dotenv
import argparse
import requests
from pprint import pprint
import os

parser = argparse.ArgumentParser()
parser.add_argument("video_id")

args = parser.parse_args()

load_dotenv()


params = {
    "key": os.getenv("YOUTUBE_API_KEY"),
    "part": "snippet",
    "id": args.video_id,
}

data = requests.get(
    "https://youtube.googleapis.com/youtube/v3/videos",
    params=params,
).json()

pprint(data)
