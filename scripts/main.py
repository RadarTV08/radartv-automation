import requests
import os
import time

token = os.environ["APIFY_TOKEN"]

actor_id = "api-ninja/youtube-search-scraper"

input_data = {
    "query": "estudante de jornalismo",
    "maxResults": 20
}

url = f"https://api.apify.com/v2/acts/{actor_id.replace('/','~')}/runs?token={token}"

response = requests.post(url, json=input_data)

run = response.json()

print(run)

print("Execução iniciada:", run_id)

time.sleep(20)

dataset_id = run["data"]["defaultDatasetId"]

dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"

videos = requests.get(dataset_url).json()

print(videos)
