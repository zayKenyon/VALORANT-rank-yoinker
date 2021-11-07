import traceback
import requests
import urllib3
import os
import base64
import json
import time
import glob
from json.decoder import JSONDecodeError
from prettytable import PrettyTable
from alive_progress import alive_bar
from io import TextIOWrapper

from src.constants import *
from src.requests import Requests
from src.logs import Logging
from src.config import Config


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

version = "1.23"

os.system('cls')
os.system(f"title VALORANT rank yoinker v{version}")
enablePrivateLogging = False

hideNames = False

server = ""


def program_exit(status: int):  # so we don't need to import the entire sys module
    log(f"exited program with error code {status}")
    raise SystemExit(status)


try:
    Requests = Requests(version)
    Requests.check_version()
    Requests.check_status()

    Logging = Logging()
    log = Logging.log

    cfg = Config()
    log(f"VALORANT rank yoinker v{version}")




    headers = {}


    def get_region():
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if '.a.pvp.net/account-xp/v1/' in line:
                    pd_url = line.split('.a.pvp.net/account-xp/v1/')[0].split('.')[-1]
                elif 'https://glz' in line:
                    glz_url = [(line.split('https://glz-')[1].split(".")[0]),
                               (line.split('https://glz-')[1].split(".")[1])]
                if "pd_url" in locals().keys() and "glz_url" in locals().keys():
                    return [pd_url, glz_url]


    region = get_region()
    pd_url = f"https://pd.{region[0]}.a.pvp.net"
    glz_url = f"https://glz-{region[1][0]}.{region[1][1]}.a.pvp.net"
    log(f"Api urls: pd_url: '{pd_url}', glz_url: '{glz_url}'")
    region = region[0]


    def get_current_version():
        path = os.path.join(os.getenv('LOCALAPPDATA'), R'VALORANT\Saved\Logs\ShooterGame.log')
        with open(path, "r", encoding="utf8") as file:
            while True:
                line = file.readline()
                if 'CI server version:' in line:
                    version_without_shipping = line.split('CI server version: ')[1].strip()
                    version = version_without_shipping.split("-")
                    version.insert(2, "shipping")
                    version = "-".join(version)
                    log(f"got version from logs '{version}'")
                    return version


    def fetch(url_type: str, endpoint: str, method: str):
        global response
        global headers
        try:
            if url_type == "glz":
                response = requests.request(method, glz_url + endpoint, headers=get_headers(), verify=False)
                log(f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                if not response.ok:
                    time.sleep(5)
                    headers = {}
                    fetch(url_type, endpoint, method)
                return response.json()
            elif url_type == "pd":
                response = requests.request(method, pd_url + endpoint, headers=get_headers(), verify=False)
                log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                if not response.ok:
                    time.sleep(5)
                    headers = {}
                    fetch(url_type, endpoint, method)
                return response
            elif url_type == "local":
                local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                    ('riot:' + lockfile['password']).encode()).decode()}
                response = requests.request(method, f"https://127.0.0.1:{lockfile['port']}{endpoint}",
                                            headers=local_headers,
                                            verify=False)
                log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                return response.json()
            elif url_type == "custom":
                response = requests.request(method, f"{endpoint}", headers=get_headers(), verify=False)
                log(
                    f"fetch: url: '{url_type}', endpoint: {endpoint}, method: {method},"
                    f" response code: {response.status_code}")
                if not response.ok: headers = {}
                return response.json()
        except json.decoder.JSONDecodeError:
            log(f"JSONDecodeError in fetch function, resp.code: {response.status_code}, resp_text: '{response.text}")
            print(response)
            print(response.text)


    def get_lockfile():
        try:
            with open(os.path.join(os.getenv('LOCALAPPDATA'), R'Riot Games\Riot Client\Config\lockfile')) as lockfile:
                log("opened log file")
                data = lockfile.read().split(':')
                keys = ['name', 'PID', 'port', 'password', 'protocol']
                return dict(zip(keys, data))
        except FileNotFoundError:
            log("lockfile not found")
            raise Exception("Lockfile not found, you're not in a game!")


    lockfile = get_lockfile()

    puuid = ''


    def get_headers():
        global headers
        if headers == {}:
            global puuid
            local_headers = {'Authorization': 'Basic ' + base64.b64encode(
                ('riot:' + lockfile['password']).encode()).decode()}
            response = requests.get(f"https://127.0.0.1:{lockfile['port']}/entitlements/v1/token",
                                    headers=local_headers, verify=False)
            entitlements = response.json()
            puuid = entitlements['subject']
            headers = {
                'Authorization': f"Bearer {entitlements['accessToken']}",
                'X-Riot-Entitlements-JWT': entitlements['token'],
                'X-Riot-ClientPlatform': "ew0KCSJwbGF0Zm9ybVR5cGUiOiAiUEMiLA0KCSJwbGF0Zm9ybU9TIjog"
                                         "IldpbmRvd3MiLA0KCSJwbGF0Zm9ybU9TVmVyc2lvbiI6ICIxMC4wLjE5"
                                         "MDQyLjEuMjU2LjY0Yml0IiwNCgkicGxhdGZvcm1DaGlwc2V0IjogIlVua25vd24iDQp9",
                'X-Riot-ClientVersion': get_current_version(),
                "User-Agent": "ShooterGame/13 Windows/10.0.19043.1.256.64bit"
            }
        return headers


    def get_coregame_match_id():
        global response
        try:
            response = fetch(url_type="glz", endpoint=f"/core-game/v1/players/{puuid}", method="get")
            match_id = response['MatchID']
            log(f"retrieved coregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            log(f"cannot find coregame match id: ")
            print(f"No match id found. {response}")
            return 0


    def get_pregame_match_id():
        global response
        try:
            response = fetch(url_type="glz", endpoint=f"/pregame/v1/players/{puuid}", method="get")
            match_id = response['MatchID']
            log(f"retrieved pregame match id: '{match_id}'")
            return match_id
        except (KeyError, TypeError):
            log(f"cannot find pregame match id: ")
            print(f"No match id found. {response}")
            return 0


    def get_coregame_stats():
        response = fetch("glz", f"/core-game/v1/matches/{get_coregame_match_id()}", "get")
        return response


    def get_pregame_stats():
        response = fetch("glz", f"/pregame/v1/matches/{get_pregame_match_id()}", "get")
        return response


    def get_rank(puuid, seasonID):
        response = fetch('pd', f"/mmr/v1/players/{puuid}", "get")
        try:
            if response.ok:
                log("retrieved rank successfully")
                r = response.json()
                rankTIER = r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["CompetitiveTier"]
                if int(rankTIER) >= 21:
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["LeaderboardRank"], ]
                elif int(rankTIER) not in (0, 1, 2, 3):
                    rank = [rankTIER,
                            r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][seasonID]["RankedRating"],
                            0,
                            ]
                else:
                    rank = [0, 0, 0]

            else:
                log("failed getting rank")
                log(response.text)
                rank = [0, 0, 0]
        except TypeError:
            rank = [0, 0, 0]
        except KeyError:
            rank = [0, 0, 0]
        max_rank = 0
        seasons = r["QueueSkills"]["competitive"].get("SeasonalInfoBySeasonID")
        if seasons is not None:
            for season in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"]:
                if r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"] is not None:
                    for winByTier in r["QueueSkills"]["competitive"]["SeasonalInfoBySeasonID"][season]["WinsByTier"]:
                        if int(winByTier) > max_rank:
                            max_rank = int(winByTier)
            rank.append(max_rank)
        else:
            rank.append(max_rank)
        return [rank, response.ok]


    def get_name_from_puuid(puuid):
        response = requests.put(pd_url + "/name-service/v2/players", headers=get_headers(), json=[puuid], verify=False)
        return response.json()[0]["GameName"] + "#" + response.json()[0]["TagLine"]


    def get_multiple_names_from_puuid(puuids):
        response = requests.put(pd_url + "/name-service/v2/players", headers=get_headers(), json=puuids, verify=False)
        name_dict = {player["Subject"]: f"{player['GameName']}#{player['TagLine']}"
                     for player in response.json()}
        return name_dict


    def get_content():
        content = fetch("custom", f"https://shared.{region}.a.pvp.net/content-service/v3/content", "get")
        return content


    def get_latest_season_id(content):
        for season in content["Seasons"]:
            if season["IsActive"]:
                return season["ID"]


    def get_all_agents():
        rAgents = requests.get("https://valorant-api.com/v1/agents?isPlayableCharacter=true").json()
        agent_dict = {}
        agent_dict.update({None: None})
        for agent in rAgents["data"]:
            agent_dict.update({agent['uuid'].lower(): agent['displayName']})
        return agent_dict


    def get_presence():
        presences = fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
        log(f"fethced presences:")
        return presences['presences']


    def get_game_state(presences):
        for presence in presences:
            if presence['puuid'] == puuid:
                return json.loads(base64.b64decode(presence['private']))["sessionLoopState"]


    def decode_presence(private):
        # try:
        if "{" not in str(private) and private is not None and str(private) != "":
            dict = json.loads(base64.b64decode(str(private)).decode("utf-8"))
            if dict.get("isValid"):
                return dict
        return {
            "isValid": False,
            "partyId": 0,
            "partySize": 0,
            "partyVersion": 0,
        }


    def get_party_json(GamePlayersPuuid, presences):
        party_json = {}
        for presence in presences:
            if presence["puuid"] in GamePlayersPuuid:
                decodedPresence = decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    if decodedPresence["partySize"] > 1:
                        try:
                            party_json[decodedPresence["partyId"]].append(presence["puuid"])
                        except KeyError:
                            party_json.update({decodedPresence["partyId"]: [presence["puuid"]]})
        log(f"retrieved party json: {party_json}")
        return party_json


    def get_party_members(self_puuid, presences):
        res = []
        for presence in presences:
            # print(presence)
            if presence["puuid"] == self_puuid:
                decodedPresence = decode_presence(presence["private"])
                if decodedPresence["isValid"]:
                    party_id = decodedPresence["partyId"]
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel":
                                decodedPresence["accountLevel"]}})
        for presence in presences:
            decodedPresence = decode_presence(presence["private"])
            if decodedPresence["isValid"]:
                if decodedPresence["partyId"] == party_id and presence["puuid"] != self_puuid:
                    res.append({"Subject": presence["puuid"], "PlayerIdentity": {"AccountLevel":
                                decodedPresence["accountLevel"]}})
        log(f"retrieved party members: {res}")
        return res


    def level_to_color(level):
        if level >= 400:
            return color(level, fore=(0, 255, 255))
        elif level >= 300:
            return color(level, fore=(255, 255, 0))
        elif level >= 200:
            return color(level, fore=(0, 0, 255))
        elif level >= 100:
            return color(level, fore=(241, 144, 54))
        elif level < 100:
            return color(level, fore=(211, 211, 211))


    def get_names_from_puuids(players):
        players_puuid = []
        for player in players:
            players_puuid.append(player["Subject"])
        return get_multiple_names_from_puuid(players_puuid)


    def get_color_from_team(team, name, playerPuuid, selfPuuid, agent=None):
        if agent is not None:
            if hideNames:
                if agent != "":
                    name = agent_dict[agent]
                else:
                    name = "Player"
        if team == 'Red':
            Teamcolor = color(name, fore=(238, 77, 77))
        elif team == 'Blue':
            Teamcolor = color(name, fore=(76, 151, 237))
        else:
            Teamcolor = ''
        if playerPuuid == selfPuuid:
            Teamcolor = color(name, fore=(221, 224, 41))
        return Teamcolor


    def get_rgb_color_from_skin(skin_id, valoApiSkins):
        for skin in valoApiSkins.json()["data"]:
            if skin_id == skin["uuid"]:
                return tierDict[skin["contentTierUuid"]]


    def get_match_loadouts(match_id, players, weaponChoose, valoApiSkins, state="game"):
        weaponLists = {}
        valApiWeapons = requests.get("https://valorant-api.com/v1/weapons").json()
        if state == "game":
            team_id = "Blue"
            PlayerInventorys = fetch("glz", f"/core-game/v1/matches/{match_id}/loadouts", "get")
        elif state == "pregame":
            pregame_stats = players
            players = players["AllyTeam"]["Players"]
            team_id = pregame_stats['Teams'][0]['team_id']
            PlayerInventorys = fetch("glz", f"/pregame/v1/matches/{match_id}/loadouts", "get")
        for player in range(len(players)):
            if team_id == "Red":
                invindex = player + len(players) - len(PlayerInventorys["Loadouts"])
            else:
                invindex = player
            inv = PlayerInventorys["Loadouts"][invindex]
            if state == "game":
                inv = inv["Loadout"]
            for weapon in valApiWeapons["data"]:
                if weapon["displayName"].lower() == weaponChoose.lower():
                    skin_id = \
                        inv["Items"][weapon["uuid"].lower()]["Sockets"]["bcef87d6-209b-46c6-8b19-fbe40bd95abc"]["Item"][
                            "ID"]
                    for skin in valoApiSkins.json()["data"]:
                        if skin_id.lower() == skin["uuid"].lower():
                            rgb_color = get_rgb_color_from_skin(skin["uuid"].lower(), valoApiSkins)
                            # if rgb_color is not None:
                            weaponLists.update({players[player]["Subject"]: color(skin["displayName"], fore=rgb_color)})
                            # else:
                            #     weaponLists.update({player["Subject"]: color(skin["Name"], fore=rgb_color)})
        return weaponLists


    def get_players_puuid(Players):
        return [player["Subject"] for player in Players]


    def add_row_table(table: PrettyTable, args: list):
        # for arg in args:
        table.add_rows([args])


    def get_views(name: str):
        responseViews = requests.get(
            f"https://tracker.gg/valorant/profile/riot/{name.split('#')[0]}%23{name.split('#')[1]}/overview").text
        try:
            result = responseViews.split("views")[1].split(">")[-1]
            int(result)
            log(f"retrieved views {result}, {name}")
            return int(result)
        except ValueError:
            log(f"retrieved None views , {name}")
            return None


    def wait_for_presence(PlayersPuuids):
        while True:
            presence = get_presence()
            for puuid in PlayersPuuids:
                if puuid not in str(presence):
                    time.sleep(1)
                    continue
            break


    def get_agent_from_uuid(agentUUID):
        agent = str(agent_dict.get(agentUUID))
        return color(agent, fore=AGENTCOLOURLIST[agent.lower()])


    valoApiSkins = requests.get("https://valorant-api.com/v1/weapons/skins")
    content = get_content()
    agent_dict = get_all_agents()
    log(f"retrieved agent dict: {agent_dict}")
    seasonID = get_latest_season_id(content)
    log(f"retrieved season id: {seasonID}")
    lastGameState = ""

    while True:
        table = PrettyTable()
        # current in-game status
        try:
            presence = get_presence()
            game_state = get_game_state(presence)
        except TypeError:
            raise Exception("Game has not started yet!")
        if cfg.cooldown == 0 or game_state != lastGameState:
            log(f"getting new {game_state} scoreboard")
            lastGameState = game_state
            game_state_dict = {
                "INGAME": color('In-Game', fore=(241, 39, 39)),
                "PREGAME": color('Agent Select', fore=(103, 237, 76)),
                "MENUS": color('In-Menus', fore=(238, 241, 54)),
            }
            if game_state == "INGAME":
                coregame_stats = get_coregame_stats()
                Players = coregame_stats["Players"]
                server = GAMEPODS[coregame_stats["GamePodID"]]
                wait_for_presence(get_players_puuid(Players))
                loadouts = get_match_loadouts(get_coregame_match_id(), Players, "vandal", valoApiSkins, state="game")
                names = get_names_from_puuids(Players)
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = get_presence()
                    partyOBJ = get_party_json(get_players_puuid(Players), presence)
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    Players.sort(key=lambda Players: Players["TeamID"], reverse=True)
                    partyCount = 0
                    partyIcons = {}
                    lastTeamBoolean = False
                    lastTeam = "Red"
                    for player in Players:
                        party_icon = ''

                        # set party premade icon
                        for party in partyOBJ:
                            if player["Subject"] in partyOBJ[party]:
                                if party not in partyIcons:
                                    partyIcons.update({party: PARTYICONLIST[partyCount]})
                                    # PARTY_ICON
                                    party_icon = PARTYICONLIST[partyCount]
                                    partyCount += 1
                                else:
                                    # PARTY_ICON
                                    party_icon = partyIcons[party]
                        rank = get_rank(player["Subject"], seasonID)
                        rankStatus = rank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            rank = get_rank(player["Subject"], seasonID)
                            rankStatus = rank[1]
                        rank = rank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        Namecolor = get_color_from_team(player["TeamID"], names[player["Subject"]], player["Subject"],
                                                        puuid)
                        if lastTeam != player["TeamID"]:
                            if lastTeamBoolean:
                                add_row_table(table, ["", "", "", "", "", "", "", "", ""])
                        lastTeam = player['TeamID']
                        lastTeamBoolean = True
                        PLcolor = level_to_color(player_level)

                        # AGENT
                        # agent = str(agent_dict.get(player["CharacterID"].lower()))
                        agent = get_agent_from_uuid(player["CharacterID"].lower())

                        # NAME
                        name = Namecolor

                        # VIEWS
                        # views = get_views(names[player["Subject"]])

                        # skin
                        skin = loadouts[player["Subject"]]

                        # RANK
                        rankName = NUMBERTORANKS[rank[0]]

                        # RANK RATING
                        rr = rank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[rank[3]]

                        # LEADERBOARD
                        leaderboard = rank[2]

                        # LEVEL
                        level = PLcolor
                        add_row_table(table, [party_icon,
                                              agent,
                                              name,
                                              # views,
                                              skin,
                                              rankName,
                                              rr,
                                              peakRank,
                                              leaderboard,
                                              level
                                              ])
                        bar()
            elif game_state == "PREGAME":
                pregame_stats = get_pregame_stats()
                server = GAMEPODS[pregame_stats["GamePodID"]]
                Players = pregame_stats["AllyTeam"]["Players"]
                wait_for_presence(get_players_puuid(Players))
                loadouts = get_match_loadouts(get_pregame_match_id(), pregame_stats, "vandal", valoApiSkins,
                                              state="pregame")
                names = get_names_from_puuids(Players)
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = get_presence()
                    partyOBJ = get_party_json(get_players_puuid(Players), presence)
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    partyCount = 0
                    partyIcons = {}
                    for player in Players:
                        party_icon = ''

                        # set party premade icon
                        for party in partyOBJ:
                            if player["Subject"] in partyOBJ[party]:
                                if party not in partyIcons:
                                    partyIcons.update({party: PARTYICONLIST[partyCount]})
                                    # PARTY_ICON
                                    party_icon = PARTYICONLIST[partyCount]
                                else:
                                    # PARTY_ICON
                                    party_icon = partyIcons[party]
                                partyCount += 1
                        rank = get_rank(player["Subject"], seasonID)
                        rankStatus = rank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            rank = get_rank(player["Subject"], seasonID)
                            rankStatus = rank[1]
                        rank = rank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        if player["PlayerIdentity"]["Incognito"]:
                            NameColor = get_color_from_team(pregame_stats['Teams'][0]['team_id'],
                                                            names[player["Subject"]],
                                                            player["Subject"], puuid, agent=player["CharacterID"])
                        else:
                            NameColor = get_color_from_team(pregame_stats['Teams'][0]['team_id'],
                                                            names[player["Subject"]],
                                                            player["Subject"], puuid)

                        PLcolor = level_to_color(player_level)
                        if player["CharacterSelectionState"] == "locked":
                            agent_color = color(str(agent_dict.get(player["CharacterID"].lower())),
                                                fore=(255, 255, 255))
                        elif player["CharacterSelectionState"] == "selected":
                            agent_color = color(str(agent_dict.get(player["CharacterID"].lower())),
                                                fore=(128, 128, 128))
                        else:
                            agent_color = color(str(agent_dict.get(player["CharacterID"].lower())), fore=(54, 53, 51))

                        # AGENT
                        agent = agent_color

                        # NAME
                        name = NameColor

                        # VIEWS
                        # views = get_views(names[player["Subject"]])

                        # skin
                        skin = loadouts[player["Subject"]]

                        # RANK
                        rankName = NUMBERTORANKS[rank[0]]

                        # RANK RATING
                        rr = rank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[rank[3]]

                        # LEADERBOARD
                        leaderboard = rank[2]

                        # LEVEL
                        level = PLcolor

                        add_row_table(table, [party_icon,
                                              agent,
                                              name,
                                              # views,
                                              skin,
                                              rankName,
                                              rr,
                                              peakRank,
                                              leaderboard,
                                              level,
                                              ])
                        bar()
            if game_state == "MENUS":
                Players = get_party_members(puuid, presence)
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    names = get_names_from_puuids(Players)
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    for player in Players:
                        party_icon = PARTYICONLIST[0]
                        rank = get_rank(player["Subject"], seasonID)
                        rankStatus = rank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            rank = get_rank(player["Subject"], seasonID)
                            rankStatus = rank[1]
                        rank = rank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        PLcolor = level_to_color(player_level)

                        # AGENT
                        agent = ""

                        # NAME
                        name = names[player["Subject"]]

                        # RANK
                        rankName = NUMBERTORANKS[rank[0]]

                        # RANK RATING
                        rr = rank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[rank[3]]

                        # LEADERBOARD
                        leaderboard = rank[2]

                        # LEVEL
                        level = str(player_level)

                        add_row_table(table, [party_icon,
                                              agent,
                                              name,
                                              "",
                                              rankName,
                                              rr,
                                              peakRank,
                                              leaderboard,
                                              level
                                              ])
                        # table.add_rows([])
                        bar()
            if (title := game_state_dict.get(game_state)) is None:
                program_exit(1)
            if server != "":
                table.title = f"Valorant status: {title} - {server}"
            else:
                table.title = f"Valorant status: {title}"
            server = ""
            table.field_names = ["Party", "Agent", "Name", "Skin", "Rank", "RR", "Peak Rank", "pos.", "Level"]
            print(table)
            print(f"VALORANT rank yoinker v{version}")
        if cfg.cooldown == 0:
            input("Press enter to fetch again...")
        else:
            time.sleep(cfg.cooldown)
except:
    print(color(
        "The program has encountered an error. If the problem persists, please reach support"
        f" with the logs found in {os.getcwd()}\logs", fore=(255, 0, 0)))
    traceback.print_exc()
    input("press enter to exit...\n")
    os._exit(1)
