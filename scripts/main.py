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
    ("faculdade de jornalismo", "Jornalismo"),
    ("recém formado em jornalismo", "Jornalismo"),
    ("TCC jornalismo", "Jornalismo"),
    ("telejornal faculdade", "Jornalismo"),
    ("reportagem faculdade jornalismo", "Jornalismo")
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
        canal = video.get("channelTitle", "")
        handle = video.get("channelHandle", "")
        descricao = video.get("description", "").lower()

        # Views
        views_texto = str(video.get("viewCount", "0"))
        views = int(views_texto.replace(",", "").replace(".", ""))

        link = f"https://youtube.com/watch?v={video.get('videoId', '')}"
        inscritos = 0

        texto = (titulo + " " + descricao + " " + canal + " " + handle).lower()

        # Canal vazio
        if canal == "":
            continue

        # Máximo de 2 mil views
        if views > 2000:
            continue

        # Temas obrigatórios
        palavras_chave = [
            "jornalismo",
            "estudante",
            "faculdade",
            "universidade",
            "telejornal",
            "tcc",
            "reportagem"
        ]

        if not any(p in texto for p in palavras_chave):
            continue

        # Bloqueia canais grandes e emissoras
        bloqueados = [
            "globo",
            "globonews",
            "cnn",
            "record",
            "band",
            "sbt",
            "jovem pan",
            "espn",
            "sportv",
            "cazétv",
            "uol",
            "terra",
            "metrópoles",
            "itatiaia",
            "cbn",
            "rádio",
            "radio",
            "tv",
            "fm",
            "am"
            "Cazé TV"
            'Cortes do Casemiro Oficial"
            "R7"
        ]

        if any(p in texto for p in bloqueados):
            continue

        # Não aceita canais muito profissionais
        palavras_proibidas = [
            "oficial",
            "news",
            "podcast",
            "ao vivo",
            "live",
            "entrevista exclusiva"
        ]

        if any(p in texto for p in palavras_proibidas):
            continue

        # Evita duplicados
        existente = (
            supabase.table("talentos")
            .select("id")
            .eq("canal", canal)
            .execute()
        )

        if len(existente.data) > 0:
            continue


        score = 50



        if inscritos > 100000:
            score += 20

        if views > 10000:
            score += 10

        if views > 100000:
            score += 10

        print(
            "SALVANDO:",
            canal,
            titulo,
            views
        )
            

        
        try:

            resposta = supabase.table("talentos").insert({
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

        except Exception as e:

            print("ERRO NO INSERT:")
            print(e)

print("Fim da execução.")




