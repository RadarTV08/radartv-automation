import os
from supabase import create_client


supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)


def talento_existe(canal):

    resposta = (
        supabase.table("talentos")
        .select("id")
        .eq("canal", canal)
        .execute()
    )

    return len(resposta.data) > 0


def salvar_talento(video, analise):

    if talento_existe(video["canal"]):
        print("Talento já existe:", video["canal"])
        return

    resposta = (
        supabase.table("talentos")
        .insert({

            "nome": video["canal"],
            "canal": video["canal"],
            "titulo_video": video["titulo"],
            "categoria": analise["categoria"],
            "plataforma": "YouTube",
            "inscritos": 0,
            "views": video["views"],
            "link_video": video["link"],
            "score": analise["score"],
            "motivo": analise["motivo"]

        })
        .execute()
    )

    print("Talento salvo:", video["canal"])

    return resposta
