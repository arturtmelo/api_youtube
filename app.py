from flask import Flask, render_template, request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

app = Flask(__name__)

API_KEY = "AIzaSyDaVaIIPqUrAcLCHNf0x881HIy7wD96n6Q"

# API YT
youtube = build("youtube", "v3", developerKey=API_KEY)

# Dicionário de tópicos/IDs correspondentes
topics = {
    "História": "/m/05qt0",
    "História Antiga": "/m/04jpl",
    "História Medieval": "/m/02vxn",
    "História Moderna": "/m/02vxnc",
    "Guerras Mundiais": "/m/04swyr",
    "Civilizações Antigas": "/m/01b_06",
    "Arqueologia": "/m/0p83c",
    "História da Arte": "/m/09kqc",
    "Biografias Históricas": "/m/03b4p3",
}


@app.route('/')
def index():
    return render_template('index.html', topics=topics)


@app.route('/search_videos')
def search_videos():
    topic = request.args.get('topic')
    min_views = 1000000  # MIN DE VIEWS

    try:
        topic_id = topics.get(topic)  # Obtem ID do tópico

        additional_keywords = ""
        if topic == "História":
            # palavra-chave adicional para história
            additional_keywords = "documentário"

        search_response = youtube.search().list(
            type="video",
            part="id,snippet",
            maxResults=10,  # NUM RESULTADOS
            order="viewCount",  # ORDENA POR VIEWS
            topicId=topic_id,  # ID TÓPICO
            q=f"{topic} {additional_keywords}",
            relevanceLanguage="pt",
        ).execute()

        videos = []
        for search_result in search_response.get("items", []):
            video_id = search_result["id"]["videoId"]
            video_title = search_result["snippet"]["title"]
            video_views = get_video_views(video_id)

            videos.append({"title": video_title, "views": video_views, "video_id": video_id})

        return render_template('search_videos.html', topics=topics, videos=videos, selected_topic=topic)

    except HttpError as e:
        print("Erro ao fazer a solicitação HTTP:", e)
        return "Erro ao fazer a solicitação HTTP: " + str(e)


def get_video_views(video_id):
    try:
        # SOLICITA DETALHES DO VIDEO
        video_response = youtube.videos().list(
            id=video_id,
            part="statistics"
        ).execute()

        # EXTRAI VIEWS
        view_count = video_response["items"][0]["statistics"]["viewCount"]
        formatted_view_count = "{:,}".format(int(view_count))

        return formatted_view_count

    except HttpError as e:
        print("Erro ao obter estatísticas do vídeo:", e)


if __name__ == "__main__":
    app.run(debug=True)
