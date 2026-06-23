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

# Executa o actor do Apify
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

# Espera terminar
time.sleep(30)

# Obtém resultados
dataset_url = f"https://api.apify.com/v2/datasets/{dataset_id}/items?token={token}"

videos = requests.get(dataset_url).json()

for video in videos:

    titulo = video.get("title", "")
    canal = video.get("channelName", "")
    inscritos = video.get("channelSubscribers", 0)
    views = video.get("viewCount", 0)
    descricao = video.get("description", "")
    link = video.get("url", "")

    prompt = f"""
Você é um recrutador do RadarTV.

Estamos procurando talentos para um projeto de TV no YouTube nas áreas de jornalismo, esportes e entretenimento.

Analise o perfil abaixo e atribua uma nota de 0 a 100.

Título do vídeo:
{titulo}

Canal:
{canal}

Inscritos:
{inscritos}

Views:
{views}

Descrição:
{descricao}

Responda neste formato:

Score: XX

Motivo: texto curto.
"""
   
    response = model.generate_content(prompt)
    resultado = response.text

    score = 0

    for linha in resultado.split("\n"):
        if "Score:" in linha:
            try:
                score = int(linha.replace("Score:", "").strip())
            except:
                score = 0

    existente = (
        supabase.table("talentos")
        .select("id")
        .eq("canal", canal)
        .execute()
    )

    if len(existente.data) == 0:

        supabase.table("talentos").insert({
            "nome": canal,
            "canal": canal,
            "titulo_video": titulo,
            "categoria": "Jornalismo",
            "plataforma": "YouTube",
            "inscritos": inscritos,
            "views": views,
            "link_video": link,
            "score": score
        }).execute()

        print("Talento salvo:", canal)

    else:
        print("Talento já existe:", canal)





