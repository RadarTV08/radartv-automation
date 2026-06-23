import requests
import os
import time
from supabase import create_client

# Chaves
token = os.environ["APIFY_TOKEN"]
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]

# Supabase
supabase = create_client(supabase_url, supabase_key)

# Pesquisas
pesquisas = [
    ("estudante de jornalismo", "Jornalismo"),
    ("jornalista esportivo", "Esportes"),
    ("comentarista esportivo", "Esportes"),
    ("narrador esportivo", "Esportes"),
    ("apresentador de TV", "Entretenimento")
]

actor_id = "api-ninja/youtube-search-scraper"

for termo, categoria in pesquisas:

    print("Pesquisando:", termo)

    input_data = {
        "query": termo,
        "maxResults": 20
    }

    url = f"https://api.apify.com/v2/acts/{actor_id.replace('/','~')}/runs?token={token}"

    response = requests.post(url, json=input_data)
    run = response.json()

    if "data" not in run:
        print("Erro no Apify:", run)
        continue

    run_id = run["data"]["id"]

    # Espera o actor terminar
    status = "RUNNING"

    while status not in ["SUCCEEDED", "FAILED", "ABORTED"]:
        time.sleep(15)

        status_response = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}?token={token}"
        ).json()

        status = status_response["data"]["status"]

        print("Status:", status)

    if status != "SUCCEEDED":
        print("Actor falhou.")
        continue

    dataset_id = run["data"]["defaultDatasetId"]

    dataset_url = (
        f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"
    )

    videos = requests.get(dataset_url).json()

    print("Vídeos encontrados:", len(videos))

    for video in videos:

        titulo = video.get("title", "")
        canal = video.get("channelName", "")
        inscritos = video.get("channelSubscribers", 0) or 0
        views = video.get("viewCount", 0) or 0
        link = video.get("url", "")

        if canal == "":
            continue

        existente = (
            supabase
            .table("talentos")
            .select("id")
            .eq("canal", canal)
            .execute()
        )

        if len(existente.data) > 0:
            print("Já existe:", canal)
            continue

        score = 50

        if inscritos > 100000:
            score += 20

        if views > 10000:
            score += 10

        if views > 100000:
            score += 10

        supabase.table("talentos").insert({
            "nome": canal,
            "canal": canal,
            "titulo_video": titulo,
            "categoria": categoria,
            "plataforma": "YouTube",
            "inscritos": inscritos,
            "views": views,
            "link_video": link,
            "score": score
        }).execute()

        print("Talento salvo:", canal)

print("Fim da execução.")





