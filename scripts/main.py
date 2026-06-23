import requests
import os
import time
import google.generativeai as genai
from supabase import create_client

# Chaves
token = os.environ["APIFY_TOKEN"]
gemini_key = os.environ["GEMINI_API_KEY"]
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]

# Supabase
supabase = create_client(supabase_url, supabase_key)

# Gemini
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-2.5-flash")

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

    try:
        run = response.json()
    except:
        print("Erro ao ler resposta do Apify")
        continue

    if "data" not in run:
        print("Erro do Apify:")
        print(run)
        continue

    dataset_id = run["data"]["defaultDatasetId"]

    time.sleep(30)

    dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"

    videos = requests.get(dataset_url).json()

    for video in videos:

        titulo = video.get("title", "")
        canal = video.get("channelName", "")
        inscritos = video.get("channelSubscribers", 0)
        views = video.get("viewCount", 0)
        descricao = video.get("description", "")
        link = video.get("url", "")

        if canal == "":
            continue

        # evita duplicados
        existente = (
            supabase.table("talentos")
            .select("id")
            .eq("canal", canal)
            .execute()
        )

        if len(existente.data) > 0:
            print("Talento já existe:", canal)
            continue

        # Score simples para não gastar Gemini
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





