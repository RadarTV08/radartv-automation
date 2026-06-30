import os

from youtube_collector import buscar_videos
from gemini_analyzer import analisar
from supabase_service import salvar_talento

token = os.environ["APIFY_TOKEN"]


from searches import TODAS


for categoria, pesquisas in TODAS:

    print(f"\n========== {categoria.upper()} ==========\n")

    for termo in pesquisas:

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

        salvar_talento(video, analise)



