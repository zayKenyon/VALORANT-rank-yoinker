import websockets
import websockets.client
import ssl
import base64
import json


class Ws:
    def __init__(self, lockfile, Requests, cfg):

        self.lockfile = lockfile
        self.Requests = Requests
        # websocket.enableTrace(True)
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE
        self.id_seen = []
        self.cfg = cfg

    # async def conntect_to_websocket(self, initial_game_state):


    #     local_headers = {}
    #     local_headers['Authorization'] = 'Basic ' + base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()
    #     url = f"wss://127.0.0.1:{self.lockfile['port']}"
    #     self.websocket_client = websockets.connect(url, ssl=self.ssl_context, extra_headers=local_headers)
    #     async with self.websocket_client as websocket:
    #         await websocket.send('[5, "OnJsonApiEvent_chat_v4_presences"]')
    #         return None
    #         # while True:
    #         #     response = await websocket.recv()
    #         #     h = self.handle(response, initial_game_state)
    #         #     if h is not None:
    #         #         return h


    async def recconect_to_websocket(self, initial_game_state):
        #wont actually recconect :)
        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()
        url = f"wss://127.0.0.1:{self.lockfile['port']}"
        self.websocket_client = websockets.connect(url, ssl=self.ssl_context, extra_headers=local_headers)
        async with self.websocket_client as websocket:
            await websocket.send('[5, "OnJsonApiEvent_chat_v4_presences"]')
            await websocket.send('[5, "OnJsonApiEvent_chat_v6_messages"]')
            while True:
                response = await websocket.recv()
                h = self.handle(response, initial_game_state)
                if h is not None:
                    await websocket.close()
                    return h

    def handle(self, m, initial_game_state):
        if len(m) > 10:
            resp_json = json.loads(m)
            if resp_json[2].get("uri") == "/chat/v4/presences":
                presence = resp_json[2]["data"]["presences"][0]
                if presence['puuid'] == self.Requests.puuid:
                    if presence.get("championId") is not None or presence.get("product") == "league_of_legends":
                        state = None
                    else:
                        state = json.loads(base64.b64decode(presence['private']))["sessionLoopState"]
                    
                    if state is not None:
                        if state != initial_game_state:
                            return state
            if resp_json[2].get("uri") == "/chat/v6/messages":
                message = resp_json[2]["data"]["messages"][0]
                if message["id"] not in self.id_seen:
                    if self.cfg.get_feature_flag("game_chat"):
                        print(f"{message['game_name']}#{message['game_tag']}: {message['body']}")
                    self.id_seen.append(message['id'])

# if __name__ == "__main__":
#     try:
#         with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
#             data = lockfile.read().split(':')
#             keys = ['name', 'PID', 'port', 'password', 'protocol']
#             lockfile = dict(zip(keys, data))
#     except:
#         raise Exception("Lockfile not found")


#     ws = Ws(lockfile, "MENUS")
#     loop = asyncio.new_event_loop()
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(ws.conntect_to_websocket("MENUS"))
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_forever()
