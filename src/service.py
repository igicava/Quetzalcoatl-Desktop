import json
import websocket
import plyer
import mdl

class ChatService():
    def __init__(self, username):
        with open("token.txt", "r") as file:
            tokenF = file.read()

        self.ws = websocket.WebSocketApp(f"{mdl.WS_SERVER}/ws?id={username}&token={tokenF}")
        self.ws.on_open = self.on_open
        self.ws.on_message = self.on_message
        self.ws.on_error = self.on_error
        self.ws.on_close = self.on_close

    def on_open(self, ws):
        print("WebSocket connection opened")

    def on_message(self, ws, message):
        print("Getting message", message)
        msg = json.loads(message)
        mdl.mp.AppendMessage(msg)
        with open("config.json", "r") as file:
            data = json.loads(file.read())
            username = data["username"]
        if msg["sender"] != username and mdl.mp.cnt != msg["sender"]:
            plyer.notification.notify( 
                message=f'{msg["text"]}',
                app_name='Quetzalcoatl',
                title=f'Новое сообщение от {msg["sender"]}', )

    def on_error(self, ws, error):
        print("WebSocket error:", error)

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket connection closed")

    def send_message(self, q):
        message = q
        if message:
            self.ws.send(json.dumps(message))
            mdl.mp.TextMsg.clear()
