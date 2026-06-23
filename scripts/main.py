import requests
import os
import time
import google.generativeai as genai
from supabase import create_client

# =====================
# CHAVES
# =====================

token = os.environ["APIFY_TOKEN"]
gemini_key = os.environ["GEMINI_API_KEY"]
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]

# =====================
# SUPABASE
# =====================

supabase = create_client(supabase_url, supabase_key)

# =====================
# GEMINI
# =====================

genai.configure(api_key=gemini_key)
model = genai.GenerativeModel("gemini-2.5-flash")

# =====================
# APIFY
# =====================

actor_id = "api-ninja/youtube-search-scraper"

pesquisas = [
    ("estudante de jornalismo", "Jornalismo"),
    ("jornalista esportivo", "Esportes"),
    ("comentarista esportivo", "Esportes"),
    ("narrador esportivo", "Esportes"),
    ("apresentador de TV", "Entretenimento"),
    ("criador de conteúdo futebol", "Esportes"),
    ("podcast futebol", "Esportes"),
    ("humor brasileiro", "Entretenimento"),
    ("cultura pop", "Entretenimento"),
    ("cinema e séries", "Entretenimento")
]

for termo, categoria in pesquisas:

    print("Pesquisando:", termo)

    input_data = {
        "query": termo,
        "maxResults": 20
    }

    url = f"https://api.apify.com/v2/acts/{actor_id.replace('/','~')}/runs?token={token}"

    response = requests.post(url, json=input_data)
    run = response.json()

    dataset_id = run["data"]["defaultDatasetId"]

    # espera o actor terminar
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

        # evita duplicados
        existente = (
            supabase
            .table("talentos")
            .select("id")
            .eq("canal", canal)
            .execute()
        )

        if len(existente.data) > 0:
            print("Talento já existe:", canal)
            continue

        prompt = f"""
Você é um recrutador do RadarTV.

Analise o perfil abaixo e dê uma nota de 0 a 100.

Canal:
{canal}

Título:
{titulo}

Inscritos:
{inscritos}

Views:
{views}

Descrição:
{descricao}

Responda exatamente assim:

Score: XX
Motivo: texto curto.
"""

        try:
            resposta = model.generate_content(prompt)
            texto = resposta.text

            score = 50

            for linha in texto.split("\n"):
                if "Score:" in linha:
                    try:
                        score = int(
                            linha.replace("Score:", "").strip()
                        )
                    except:
                        pass

        except Exception as e:
            print("Erro Gemini:", e)
            score = 50

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

        # evita limite do Gemini
        time.sleep(5)

print("Fim da execução.")





