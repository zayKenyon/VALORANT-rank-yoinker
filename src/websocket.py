import websockets
import ssl
import os
import asyncio
import base64
import json

class Ws:
    def __init__(self, lockfile):

        self.lockfile = lockfile

        # websocket.enableTrace(True)
        self.ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        self.ssl_context.check_hostname = False
        self.ssl_context.verify_mode = ssl.CERT_NONE

    async def conntect_to_websocket(self):


        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(('riot:' + self.lockfile['password']).encode()).decode()
        url = f"wss://127.0.0.1:{self.lockfile['port']}"
        async with websockets.connect(url, ssl=self.ssl_context, extra_headers=local_headers) as websocket:
            await websocket.send('[5, "OnJsonApiEvent_chat_v4_presences"]')
            while True:
                response = await websocket.recv()
                if len(response) > 10:
                    presence = json.loads(response[38:-1])
                    print(presence["data"]["presences"])





if __name__ == "__main__":
    try:
        with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
            data = lockfile.read().split(':')
            keys = ['name', 'PID', 'port', 'password', 'protocol']
            lockfile = dict(zip(keys, data))
    except:
        raise Exception("Lockfile not found")


    ws = Ws(lockfile)
    # loop = asyncio.get_event_loop()
    # loop.run_until_complete(ws.conntect_to_websocket())
    asyncio.run(ws.conntect_to_websocket())