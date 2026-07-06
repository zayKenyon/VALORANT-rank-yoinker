import json
import logging
from websocket_server import WebsocketServer, WebSocketHandler

def safe_read_http_headers(self):
    headers = {"upgrade": "invalid"}
    try:
        http_get = self.rfile.readline().decode().strip()
        if not http_get.upper().startswith('GET'):
            return headers
    except Exception:
        return headers
        
    while True:
        try:
            header = self.rfile.readline().decode().strip()
            if not header:
                break
            head, value = header.split(':', 1)
            headers[head.lower().strip()] = value.strip()
        except Exception:
            break
    return headers

WebSocketHandler.read_http_headers = safe_read_http_headers

from src.constants import version

logging.getLogger('websocket_server.websocket_server').disabled = True

# websocket.enableTrace(True)

class Server:
    def __init__(self, log, Error):
        self.Error = Error
        self.log = log
        self.lastMessages = {}

    def start_server(self):
        try:
            # print(self.lastMessage)
            with open("config.json", "r") as conf:
                port = json.load(conf)["port"]
            self.server = WebsocketServer(host="0.0.0.0", port=port)
            # server = websocket.WebSocketApp("wss://localhost:1100", on_open=on_open, on_message=on_message, on_close=on_close)
            self.server.set_fn_new_client(self.handle_new_client)
            self.server.run_forever(threaded=True)
        except Exception as e:
            self.Error.PortError(port)

    def handle_new_client(self, client, server):
        self.send_payload("version",{
            "core": version
        })
        for key in self.lastMessages:
            if key not in ["chat","version"]:
                self.send_message(self.lastMessages[key])

    def send_message(self, message):
        self.server.send_message_to_all(message)

    def send_payload(self, type, payload):
        payload["type"] = type
        msg_str = json.dumps(payload)
        self.lastMessages[type] = msg_str
        self.server.send_message_to_all(msg_str)
