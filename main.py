import traceback
import requests
import urllib3
import os
import base64
import json
import time
from prettytable import PrettyTable
from alive_progress import alive_bar

from src.constants import *
from src.requests import Requests
from src.logs import Logging
from src.config import Config
from src.colors import Colors
from src.rank import Rank
from src.content import Content
from src.names import Names


from src.states.menu import Menu
from src.states.pregame import Pregame
from src.states.coregame import Coregame

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

version = "1.23"

os.system('cls')
os.system(f"title VALORANT rank yoinker v{version}")
enablePrivateLogging = False

hide_names = False

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

    cfg = Config(log)


    menu = Menu(Requests, log)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)


    rank = Rank(Requests, log)

    content = Content(Requests, log)

    namesClass = Names(Requests, log)




    agent_dict = content.get_all_agents()

    colors = Colors(hide_names, agent_dict)




    log(f"VALORANT rank yoinker v{version}")


    def get_presence():
        presences = Requests.fetch(url_type="local", endpoint="/chat/v4/presences", method="get")
        log(f"fethced presences:")
        return presences['presences']


    def get_game_state(presences):
        for presence in presences:
            if presence['puuid'] == Requests.puuid:
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



    def get_match_loadouts(match_id, players, weaponChoose, valoApiSkins, state="game"):
        weaponLists = {}
        valApiWeapons = requests.get("https://valorant-api.com/v1/weapons").json()
        if state == "game":
            team_id = "Blue"
            PlayerInventorys = Requests.fetch("glz", f"/core-game/v1/matches/{match_id}/loadouts", "get")
        elif state == "pregame":
            pregame_stats = players
            players = players["AllyTeam"]["Players"]
            team_id = pregame_stats['Teams'][0]['TeamID']
            PlayerInventorys = Requests.fetch("glz", f"/pregame/v1/matches/{match_id}/loadouts", "get")
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
                            rgb_color = colors.get_rgb_color_from_skin(skin["uuid"].lower(), valoApiSkins)
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
    gameContent = content.get_content()
    seasonID = content.get_latest_season_id(gameContent)
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
                coregame_stats = coregame.get_coregame_stats()
                Players = coregame_stats["Players"]
                server = GAMEPODS[coregame_stats["GamePodID"]]
                wait_for_presence(get_players_puuid(Players))
                loadouts = get_match_loadouts(coregame.get_coregame_match_id(), Players, "vandal", valoApiSkins, state="game")
                names = namesClass.get_names_from_puuids(Players)
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
                        rank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = rank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            rank = rank.get_rank(player["Subject"], seasonID)
                            rankStatus = rank[1]
                        rank = rank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        Namecolor = colors.get_color_from_team(player["TeamID"], names[player["Subject"]], player["Subject"],
                                                        Requests.puuid)
                        if lastTeam != player["TeamID"]:
                            if lastTeamBoolean:
                                add_row_table(table, ["", "", "", "", "", "", "", "", ""])
                        lastTeam = player['TeamID']
                        lastTeamBoolean = True
                        PLcolor = colors.level_to_color(player_level)

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
                pregame_stats = pregame.get_pregame_stats()
                server = GAMEPODS[pregame_stats["GamePodID"]]
                Players = pregame_stats["AllyTeam"]["Players"]
                wait_for_presence(get_players_puuid(Players))
                loadouts = get_match_loadouts(pregame.get_pregame_match_id(), pregame_stats, "vandal", valoApiSkins,
                                              state="pregame")
                names = namesClass.get_names_from_puuids(Players)
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
                        playerRank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            playerRank = rank.get_rank(player["Subject"], seasonID)
                            rankStatus = playerRank[1]
                        playerRank = playerRank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        if player["PlayerIdentity"]["Incognito"]:
                            NameColor = colors.get_color_from_team(pregame_stats['Teams'][0]['TeamID'],
                                                            names[player["Subject"]],
                                                            player["Subject"], Requests.puuid, agent=player["CharacterID"])
                        else:
                            NameColor = colors.get_color_from_team(pregame_stats['Teams'][0]['TeamID'],
                                                            names[player["Subject"]],
                                                            player["Subject"], Requests.puuid)

                        PLcolor = colors.level_to_color(player_level)
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
                        rankName = NUMBERTORANKS[playerRank[0]]

                        # RANK RATING
                        rr = playerRank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[playerRank[3]]

                        # LEADERBOARD
                        leaderboard = playerRank[2]

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
                Players = get_party_members(Requests.puuid, presence)
                names = namesClass.get_names_from_puuids(Players)
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    log(f"retrieved names dict: {names}")
                    Players.sort(key=lambda Players: Players["PlayerIdentity"].get("AccountLevel"), reverse=True)
                    for player in Players:
                        party_icon = PARTYICONLIST[0]
                        playerRank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            playerRank = rank.get_rank(player["Subject"], seasonID)
                            rankStatus = playerRank[1]
                        playerRank = playerRank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        PLcolor = colors.level_to_color(player_level)

                        # AGENT
                        agent = ""

                        # NAME
                        name = names[player["Subject"]]

                        # RANK
                        rankName = NUMBERTORANKS[playerRank[0]]

                        # RANK RATING
                        rr = playerRank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[playerRank[3]]

                        # LEADERBOARD
                        leaderboard = playerRank[2]

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
