import requests
import time


ACTOR_ID = "api-ninja/youtube-search-scraper"


def buscar_videos(apify_token, termo, max_results=20):

    print(f"\nPesquisando: {termo}")

    input_data = {
        "query": termo,
        "maxResults": max_results
    }

    url = (
        f"https://api.apify.com/v2/acts/"
        f"{ACTOR_ID.replace('/','~')}/runs"
        f"?token={apify_token}"
    )

    response = requests.post(url, json=input_data)

    try:
        run = response.json()
    except Exception:
        print("Erro ao interpretar resposta do Apify.")
        return []

    if "data" not in run:
        print("Erro retornado pelo Apify:")
        print(run)
        return []

    run_id = run["data"]["id"]

    status = "RUNNING"

    while status not in ["SUCCEEDED", "FAILED", "ABORTED"]:

        time.sleep(10)

        status_response = requests.get(
            f"https://api.apify.com/v2/actor-runs/{run_id}?token={apify_token}"
        ).json()

        status = status_response["data"]["status"]

        print("Status:", status)

    if status != "SUCCEEDED":
        print("Actor falhou.")
        return []

    dataset_id = run["data"]["defaultDatasetId"]

    dataset_url = (
        f"https://api.apify.com/v2/datasets/"
        f"{dataset_id}/items?token={apify_token}"
    )

    videos = requests.get(dataset_url).json()

    print(f"{len(videos)} vídeos encontrados.")

    lista = []

    for video in videos:

        try:

            titulo = video.get("title", "")

            canal = (
                video.get("channelTitle")
                or video.get("channelName")
                or ""
            )

            handle = video.get("channelHandle", "")

            descricao = video.get("description", "")

            views = int(
                str(video.get("viewCount", "0"))
                .replace(",", "")
                .replace(".", "")
            )

            video_id = video.get("videoId", "")

            link = f"https://youtube.com/watch?v={video_id}"

            lista.append({
                "titulo": titulo,
                "canal": canal,
                "handle": handle,
                "descricao": descricao,
                "views": views,
                "link": link
            })

        except Exception as erro:

            print("Erro lendo vídeo:")
            print(erro)

    return lista
