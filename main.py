import requests
import urllib3
import os
import base64
import json
import time
from prettytable import PrettyTable

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BLACK = "\033[0;30m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
BROWN = "\033[0;33m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
LIGHT_GRAY = "\033[0;37m"
DARK_GRAY = "\033[1;30m"
LIGHT_RED = "\033[1;31m"
LIGHT_GREEN = "\033[1;32m"
YELLOW = "\033[1;33m"
LIGHT_BLUE = "\033[1;34m"
LIGHT_PURPLE = "\033[1;35m"
LIGHT_CYAN = "\033[1;36m"
LIGHT_WHITE = "\033[1;37m"
BOLD = "\033[1m"
FAINT = "\033[2m"
ITALIC = "\033[3m"
UNDERLINE = "\033[4m"
BLINK = "\033[5m"
NEGATIVE = "\033[7m"
CROSSED = "\033[9m"
end_tag = "\033[0m"


number_to_ranks = {
    0: LIGHT_GRAY + "Unrated" + end_tag,
    1: LIGHT_GRAY + "Unrated" + end_tag,
    2: LIGHT_GRAY + "Unrated" + end_tag,
    3: LIGHT_GRAY + "Iron 1" + end_tag,
    4: LIGHT_GRAY + "Iron 2" + end_tag,
    5: LIGHT_GRAY + "Iron 3" + end_tag,
    6: BROWN + "Bronze 1" + end_tag,
    7: BROWN + "Bronze 2" + end_tag,
    8: BROWN + "Bronze 3" + end_tag,
    9: LIGHT_WHITE + "Silver 1" + end_tag,
    10: LIGHT_WHITE + "Silver 2" + end_tag,
    11: LIGHT_WHITE + "Silver 3" + end_tag,
    12: BOLD + YELLOW + "Gold 1" + end_tag,
    13: BOLD + YELLOW + "Gold 2" + end_tag,
    14: BOLD + YELLOW + "Gold 3" + end_tag,
    15: LIGHT_CYAN + "Platinum 1" + end_tag,
    16: LIGHT_CYAN + "Platinum 2" + end_tag,
    17: LIGHT_CYAN + "Platinum 3" + end_tag,
    18: LIGHT_PURPLE + "Diamond 1" + end_tag,
    19: LIGHT_PURPLE + "Diamond 2" + end_tag,
    20: LIGHT_PURPLE + "Diamond 3" + end_tag,
    21: LIGHT_RED + "Immortal" + end_tag,
    22: LIGHT_RED + "Immortal 2" + end_tag,
    23: LIGHT_RED + "Immortal 3" + end_tag,
    24: BOLD + "Radiant" + end_tag
}



headers = {}

def get_current_version():
    data = requests.get('https://valorant-api.com/v1/version')
    data = data.json()['data']
    version = f"{data['branch']}-shipping-{data['buildVersion']}-{data['version'].split('.')[3]}"
    return version

def fetch(url_type, endpoint, method):
    global response
    try:
        if url_type == "glz":
            response = requests.request(method, glz_url + endpoint, headers=get_headers(), verify=False)
            return response.json()
        elif url_type == "pd":
            response = requests.request(method, pd_url + endpoint, headers=get_headers(), verify=False)
            return response.json()
        elif url_type == "local":
            local_headers = {}
            local_headers['Authorization'] = 'Basic ' + base64.b64encode(
                ('riot:' + lockfile['password']).encode()).decode()
            response = requests.request(method, f"https://127.0.0.1:{lockfile['port']}{endpoint}", headers=local_headers,
                                    verify=False)
            return response.json()
        elif url_type == "custom":
            response = requests.request(method, f"{endpoint}", headers=get_headers(),
                                    verify=False)
            return response.json()
    except json.decoder.JSONDecodeError:
        print(response)
        print(response.text)


def get_lockfile():
    try:
        with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
            data = lockfile.read().split(':')
            keys = ['name', 'PID', 'port', 'password', 'protocol']
            return dict(zip(keys, data))
    except:
        raise Exception("Lockfile not found, you're not in a game!")


lockfile = get_lockfile()




def get_headers():
    global headers
    if headers == {}:
        local_headers = {}
        local_headers['Authorization'] = 'Basic ' + base64.b64encode(
            ('riot:' + lockfile['password']).encode()).decode()
        response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                                verify=False)
        entitlements = response.json()
        headers = {
            'Authorization': f"Bearer {entitlements['accessToken']}",
            'X-Riot-Entitlements-JWT': entitlements['token'],
            'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjogIldpbmRvd3MiLA0KCSJwbGF0Z"
                                     "m9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0I"
                                     "jogIlVua25vd24iDQp9",
            'X-Riot-ClientVersion': get_current_version()
        }
    return headers


def get_puuid():
    local_headers = {}
    local_headers['Authorization'] = 'Basic ' + base64.b64encode(
        ('riot:' + lockfile['password']).encode()).decode()
    response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token", headers=local_headers,
                            verify=False)
    entitlements = response.json()
    puuid = entitlements['subject']
    return puuid




def get_coregame_match_id():
    global response
    try:
        response = fetch(url_type="glz", endpoint=f"/core-game/v1/players/{get_puuid()}", method="get")
        match_id = response['MatchID']
        return match_id
    except KeyError:
        print(f"No match id found. {response}")
        return 0


def get_coregame_stats():
    response = fetch("glz", f"/core-game/v1/matches/{get_coregame_match_id()}", "get")
    return response



def getRank(puuid, seasonID):
    response = fetch('pd', f"/mmr/v1/players/{puuid}", "get")
    try:
        rankTIER = response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["CompetitiveTier"]
        if int(rankTIER) not in (0, 1, 2, 3):
            rank = [rankTIER, response["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"]]
        else:
            rank = [0, 0]
    except TypeError:
        rank = [0, 0]
    except KeyError:
        rank = [0, 0]
    return rank



def get_name_from_puuid(puuid):
    response = requests.put(pd_url + f"/name-service/v2/players", headers=get_headers(), json=[puuid], verify=False)
    return response.json()[0]["GameName"] + "#" + response.json()[0]["TagLine"]

def get_latest_season_id(content=fetch("custom", "https://shared.na.a.pvp.net/content-service/v2/content", "get")):
    for season in content["Seasons"]:
        if season["IsActive"] == True:
            return season["ID"]

def get_content():
    content = fetch("custom", "https://shared.na.a.pvp.net/content-service/v2/content", "get")
    return content

def get_all_agents(content=fetch("custom", "https://shared.na.a.pvp.net/content-service/v2/content", "get")):
    agent_dict = {}
    for agent in content["Characters"]:
        if "NPE" not in agent["AssetName"]:
            agent_dict.update({agent['ID'].lower(): agent['Name']})
    return agent_dict

def get_region():
    path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
    with open(path, "r", encoding="utf8") as file:
        while True:
            line = file.readline()
            if '.a.pvp.net/account-xp/v1/' in line:
                return line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]



region = get_region()
glz_url = f"https://glz-{region}-1.{region}.a.pvp.net"
pd_url = f"https://pd.{region}.a.pvp.net"

content = get_content()
agent_dict = get_all_agents(content)
seasonID = get_latest_season_id(content)

Players = get_coregame_stats()["Players"]
table = PrettyTable()
table.field_names = ["Agent", "Name", "Rank", "RR", "Leaderboard Position"]
for player in Players:
    rank = getRank(player["Subject"], seasonID)
    if player['TeamID'] == 'Red':
        color = LIGHT_RED
    elif player['TeamID'] == 'Blue':
        color = LIGHT_BLUE
    else:
        color = ''
    table.add_rows([[color + agent_dict[player["CharacterID"].lower()] + end_tag,
                    color + get_name_from_puuid(player["Subject"]) + end_tag,
                    number_to_ranks[rank[0]],
                    rank[1],
                    0
                    ]])
    time.sleep(0.5)
print(table)
input("Press enter to exit...")
