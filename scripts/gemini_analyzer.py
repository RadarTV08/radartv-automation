import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])


PROMPT = """
Você é o headhunter oficial do RadarTV.

Sua missão é encontrar talentos para uma emissora digital.

Você deve avaliar se esse criador de conteúdo tem potencial para trabalhar conosco.

Critérios:

- Deve ser uma PESSOA e não uma empresa.
- Não pode ser uma emissora.
- Não pode ser um grande influenciador.
- Não pode ser um canal famoso.
- Dê preferência para:
    • estudantes
    • recém-formados
    • pequenos criadores
    • streamers pequenos
    • jornalistas independentes
    • produtores independentes

Classifique em apenas UMA categoria:

- Jornalismo
- Esportes
- Política
- Entretenimento
- Produção

Também escolha uma subcategoria.

Exemplos:

Telejornal

Reportagem

Streamer

Cinema

Humor

Narrador

Comentarista

Editor de vídeo

Videomaker

Podcast

Cultura Pop

Retorne APENAS um JSON válido.

Formato:

{
    "salvar": true,
    "categoria": "",
    "subcategoria": "",
    "tipo": "Pessoa",
    "score": 0,
    "motivo": ""
}
"""


def analisar(video):

    texto = f"""
Título:
{video["titulo"]}

Canal:
{video["canal"]}

Descrição:
{video["descricao"]}

Views:
{video["views"]}
"""

    try:

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=PROMPT + "\n\n" + texto
        )

        resposta = response.text.strip()

        if resposta.startswith("```json"):
            resposta = resposta.replace("```json", "")
            resposta = resposta.replace("```", "").strip()

        elif resposta.startswith("```"):
            resposta = resposta.replace("```", "").strip()

        dados = json.loads(resposta)

        return dados

    except Exception as e:

        print("Erro Gemini:")
        print(e)

        return {
            "salvar": False,
            "categoria": "",
            "subcategoria": "",
            "tipo": "",
            "score": 0,
            "motivo": "Erro no Gemini"
        }
