import os

from youtube_collector import buscar_videos
from gemini_analyzer import analisar
from supabase_service import salvar_talento

token = os.environ["APIFY_TOKEN"]


PESQUISAS = [

    # Jornalismo
    ("estudante de jornalismo", "Jornalismo"),
    ("faculdade de jornalismo", "Jornalismo"),
    ("telejornal faculdade", "Jornalismo"),
    ("reportagem faculdade", "Jornalismo"),
    ("recém formado jornalismo", "Jornalismo"),

]


for termo, categoria in PESQUISAS:

    videos = buscar_videos(
        token,
        termo,
        max_results=20
    )

    for video in videos:

        print("--------------------------------")
        print(video["titulo"])

        analise = analisar(video)

        if not analise["salvar"]:
            print("Descartado pelo Gemini.")
            continue

        analise["categoria"] = categoria

        salvar_talento(video, analise)



