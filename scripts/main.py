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

run_id = run["data"]["id"]

print("Execução iniciada:", run_id)

import requests
import os
import time
import google.generativeai as genai

token = os.environ["APIFY_TOKEN"]
gemini_key = os.environ["GEMINI_API_KEY"]
genai.configure(api_key=gemini_key)

model = genai.GenerativeModel("gemini-2.5-flash")

response = model.generate_content(
    "Diga apenas: Gemini funcionando"
)

print(response.text)

print("Gemini carregado com sucesso!")

actor_id = "api-ninja/youtube-search-scraper"

input_data = {
    "query": "estudante de jornalismo",
    "maxResults": 20
}

url = f"https://api.apify.com/v2/acts/{actor_id.replace('/','~')}/runs?token={token}"

response = requests.post(url, json=input_data)

run = response.json()

run_id = run["data"]["id"]
dataset_id = run["data"]["defaultDatasetId"]

print("Execução iniciada:", run_id)

# Espera o actor terminar
time.sleep(30)

dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"

videos = requests.get(dataset_url).json()

print(videos)
