import websockets
import ssl
import os
import asyncio
import base64
import json

class Ws:
    def __init__(self, lockfile, Requests):

        self.lockfile = lockfile
        self.Requests = Requests
        # websocket.enableTrace(True)
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def conntect_to_websocket(self, initial_game_state):


        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()
        url = f"wss://127.0.0.1:{self.lockfile['port']}"
        self.websocket_client = websockets.connect(url, ssl=self.ssl_context, extra_headers=local_headers)
        async with self.websocket_client as websocket:
            await websocket.send('[5, "OnJsonApiEvent_chat_v4_presences"]')
            return None
            # while True:
            #     response = await websocket.recv()
            #     h = self.handle(response, initial_game_state)
            #     if h is not None:
            #         return h


    async def recconect_to_websocket(self, initial_game_state):
        #wont actually recconect :)
        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()
        url = f"wss://127.0.0.1:{self.lockfile['port']}"
        self.websocket_client = websockets.connect(url, ssl=self.ssl_context, extra_headers=local_headers)
        async with self.websocket_client as websocket:
            await websocket.send('[5, "OnJsonApiEvent_chat_v4_presences"]')
            while True:
                response = await websocket.recv()
                h = self.handle(response, initial_game_state)
                if h is not None:
                    await websocket.close()
                    return h

    def handle(self, m, initial_game_state):
        if len(m) > 10:
            presence = json.loads(m[38:-1])
            n_presence = presence["data"]["presences"][0]
            # print(n_presence)
            # print(type(n_presence))
            if n_presence['puuid'] == self.Requests.puuid:
            # if n_presence['puuid'] == "963ad672-61e1-537e-8449-06ece1a5ceb7":
            # #preventing vry from crashing when lol is open
            # print(presence)
            # print(presence.get("championId"))
                if n_presence.get("championId") is not None or n_presence.get("product") == "league_of_legends":
                    state = None
                else:
                    state = json.loads(base64.b64decode(n_presence['private']))["sessionLoopState"]
                
                if state is not None:
                    if state != initial_game_state:
                        return state

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
    