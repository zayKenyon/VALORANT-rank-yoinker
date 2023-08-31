import json
from websocket_server import WebsocketServer


class Server:
    def __init__(self, log, Error):
        self.Error = Error
        self.log = log
        self.lastMessage = ""

    def start_server(self):
        try:
            # print(self.lastMessage)
            with open('config.json', "r") as conf:
                port = json.load(conf)["port"]
            self.server = WebsocketServer(host='127.0.0.1', port=port)
            self.server.set_fn_new_client(self.handle_new_client)
            self.server.run_forever(threaded=True)
        except Exception as e:
            self.Error.PortError(port)

    def handle_new_client(self, client, server):
        if self.lastMessage != "":
            self.send_message(self.lastMessage)


    def send_message(self, message):
        self.lastMessage = message
        self.server.send_message_to_all(message)

