from flask import Flask, request
import application
import json

app = Flask(__name__)

@app.route("/msg")
def msg():
    message = request.get_json()
    message = json.loads(message)
    application.mp.Chat.append(message["text"])

async def Run():
    await app.run(port=8888)