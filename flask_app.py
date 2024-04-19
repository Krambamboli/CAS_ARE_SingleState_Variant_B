import os
from flask import Flask, jsonify, render_template, request, send_file

from chatbot.chatbot import Chatbot

PYTHONANYWHERE_USERNAME = "carvice"
PYTHONANYWHERE_WEBAPPNAME = "mysite"

app = Flask(__name__)

my_type_role = """
    Dein Auftrag ist es, den Benutzer dabei zu unterstützen, sich an ein spezifisches Wort oder einen bestimmten Begriff zu erinnern, der ihm auf der Zunge liegt. Verwende in dieser Sitzung geschlossene Fragen, die auf Ja- oder Nein-Antworten oder kurze, spezifische Informationen abzielen. Beginne das Gespräch mit einer präzisen Frage. Fortlaufend solltest du weitere geschlossene Fragen stellen, die auf den bisherigen Antworten aufbauen, um den Benutzer eng zu führen und den Erinnerungsprozess zu beschleunigen. Ziel ist es, durch diese enge Führung und präzisen Fragen den Benutzer schnell zum gesuchten Begriff zu navigieren.
"""

my_instance_context = """
    Dieses Modul unterstützt Nutzer dabei, sich an schwer fassbare Wörter oder Begriffe zu erinnern, indem es geschlossene Fragen verwendet. Die Fragen sind darauf ausgelegt, schnelle und spezifische Informationen zu gewinnen, um den Erinnerungsprozess zu beschleunigen. Durch direkte Ja- oder Nein-Antworten oder eine Auswahl aus wenigen Optionen soll der Benutzer schnell zum gesuchten Begriff navigiert werden. Das System reagiert effizient auf die Antworten der Benutzer und passt die Fragen entsprechend an, um eine zielgerichtete Unterstützung zu bieten.

"""

my_instance_starter = """
Versuchen wir, das gesuchte Wort einzugrenzen. Ist der Begriff, der dir auf der Zunge liegt, ein Gegenstand? 
"""

bot = Chatbot(
    database_file="database/chatbot.db", 
    type_id="coach",
    user_id="daniel",
    type_name="Health Coach",
    type_role=my_type_role,
    instance_context=my_instance_context,
    instance_starter=my_instance_starter
)

bot.start()

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/mockups.pdf', methods=['GET'])
def get_first_pdf():
    script_directory = os.path.dirname(os.path.realpath(__file__))
    files = [f for f in os.listdir(script_directory) if os.path.isfile(os.path.join(script_directory, f))]
    pdf_files = [f for f in files if f.lower().endswith('.pdf')]
    if pdf_files:
        # Get the path to the first PDF file
        pdf_path = os.path.join(script_directory, pdf_files[0])

        # Send the PDF file as a response
        return send_file(pdf_path, as_attachment=True)

    return "No PDF file found in the root folder."

@app.route("/<type_id>/<user_id>/chat")
def chatbot(type_id: str, user_id: str):
    return render_template("chat.html")


@app.route("/<type_id>/<user_id>/info")
def info_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: dict[str, str] = bot.info_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/conversation")
def conversation_retrieve(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    response: list[dict[str, str]] = bot.conversation_retrieve()
    return jsonify(response)


@app.route("/<type_id>/<user_id>/response_for", methods=["POST"])
def response_for(type_id: str, user_id: str):
    user_says = None
    # content_type = request.headers.get('Content-Type')
    # if (content_type == 'application/json; charset=utf-8'):
    user_says = request.json
    # else:
    #    return jsonify('/response_for request must have content_type == application/json')

    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    assistant_says_list: list[str] = bot.respond(user_says)
    response: dict[str, str] = {
        "user_says": user_says,
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)


@app.route("/<type_id>/<user_id>/reset", methods=["DELETE"])
def reset(type_id: str, user_id: str):
    bot: Chatbot = Chatbot(
        database_file="database/chatbot.db",
        type_id=type_id,
        user_id=user_id,
    )
    bot.reset()
    assistant_says_list: list[str] = bot.start()
    response: dict[str, str] = {
        "assistant_says": assistant_says_list,
    }
    return jsonify(response)
