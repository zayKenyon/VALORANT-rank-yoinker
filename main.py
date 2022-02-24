from tokenize import group
import traceback
import re
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
from src.presences import Presences
from src.Loadouts import Loadouts

from src.states.menu import Menu
from src.states.pregame import Pregame
from src.states.coregame import Coregame

from src.table import Table
from src.server import Server


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.system('cls')
os.system(f"title VALORANT rank yoinker v{version}")

server = ""


def program_exit(status: int):  # so we don't need to import the entire sys module
    log(f"exited program with error code {status}")
    raise SystemExit(status)

def winRate(username):
    #time.sleep(2.5)
    parsed = f"{username.split('#')[0]}%23{username.split('#')[1]}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion',
        'Accept': 'application/json, text/plain, /',
        'Accept-Language': 'en',
        'Connection': 'keep-alive',
    }
    r = requests.get(f'https://tracker.gg/valorant/profile/riot/{parsed}/overview?playlist=competitive', headers=headers)
    WinRate = re.findall('data-v-309b1f1e>((?:\d+\.\d*)|(?:\.?\d+))', r.text)
    #float(WinRate[3])
    if WinRate == []: 
        return "-"
    else: 
        if len(WinRate) > 0:  
            return WinRate[3] + "%"

def headShot(username):
    parsed = f"{username.split('#')[0]}%23{username.split('#')[1]}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion',
        'Accept': 'application/json, text/plain, /',
        'Accept-Language': 'en',
        'Connection': 'keep-alive',
    }
    r = requests.get(f'https://tracker.gg/valorant/profile/riot/{parsed}/overview?playlist=competitive', headers=headers)
    HeadShot = re.findall('data-v-309b1f1e>((?:\d+\.\d*)|(?:\.?\d+))', r.text)
    if HeadShot == []: 
        return "-"
    else: 
        if len(HeadShot) > 0:  
            return HeadShot[2] + "%"

def getrr(username):
    #time.sleep(2.5)
    parsed = f"{username.split('#')[0]}%23{username.split('#')[1]}"
    #print(parsed)
    headers = {
        'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion',
        'Accept': 'application/json, text/plain, /',
        'Accept-Language': 'en',
        'Connection': 'keep-alive',
    }
    r = requests.get(f'https://tracker.gg/valorant/profile/riot/{parsed}/overview?playlist=competitive', headers=headers)
    rr = re.findall('              ([0-9]{2,4})', r.text)
    #print(rr)
    #print(r.text)
    if rr == []: 
        return "-"
    else: 
        if len(rr) > 0: 
            return max(rr)

def mostPlayed(username):
    #time.sleep(2.5)
    parsed = f"{username.split('#')[0]}%23{username.split('#')[1]}"
    #print(parsed)
    headers = {
        'User-Agent': 'Mozilla/5.0 (platform; rv:geckoversion) Gecko/geckotrail Firefox/firefoxversion',
        'Accept': 'application/json, text/plain, /',
        'Accept-Language': 'en',
        'Connection': 'keep-alive',
    }
    r = requests.get(f'https://tracker.gg/valorant/profile/riot/{parsed}/overview?playlist=competitive', headers=headers)
    Agents = re.findall('<span class="agent__name" data-v-c68f241e data-v-5c0ca8ee>([a-zA-Z]+[/]*[a-zA-Z]+)', r.text)
    mystring=' '.join(map(str,Agents))
    return mystring 
    
try:
    Requests = Requests(version)
    Requests.check_version()
    Requests.check_status()
    
    Logging = Logging()
    log = Logging.log

    cfg = Config(log)

    rank = Rank(Requests, log)

    content = Content(Requests, log)

    namesClass = Names(Requests, log)

    presences = Presences(Requests, log)


    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(Requests)
    Server.start_server()


    agent_dict = content.get_all_agents()

    colors = Colors(hide_names, agent_dict, AGENTCOLORLIST)

    loadoutsClass = Loadouts(Requests, log, colors, Server)
    tableClass = Table()



    log(f"VALORANT rank yoinker v{version}")




    valoApiSkins = requests.get("https://valorant-api.com/v1/weapons/skins")
    gameContent = content.get_content()
    seasonID = content.get_latest_season_id(gameContent)
    lastGameState = ""

    while True:
        table = PrettyTable()
        try:
            presence = presences.get_presence()
            game_state = presences.get_game_state(presence)
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
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                loadouts = loadoutsClass.get_match_loadouts(coregame.get_coregame_match_id(), Players, cfg.weapon, valoApiSkins, names, state="game")
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = presences.get_presence()
                    partyOBJ = menu.get_party_json(namesClass.get_players_puuid(Players), presence)
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
                        playerRank = rank.get_rank(player["Subject"], seasonID)
                        rankStatus = playerRank[1]
                        while not rankStatus:
                            print("You have been rate limited, 😞 waiting 10 seconds!")
                            time.sleep(10)
                            playerRank = rank.get_rank(player["Subject"], seasonID)
                            rankStatus = playerRank[1]
                        playerRank = playerRank[0]
                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        Namecolor = colors.get_color_from_team(player["TeamID"], names[player["Subject"]], player["Subject"],
                                                        Requests.puuid)
                        if lastTeam != player["TeamID"]:
                            if lastTeamBoolean:
                                tableClass.add_row_table(table, ["", "", "", "", "", "", "", "", "", "", "", "",""])
                        lastTeam = player['TeamID']
                        lastTeamBoolean = True
                        PLcolor = colors.level_to_color(player_level)
                        
                        #WRcolor = colors.Winrate_to_color(WinRate)

                        # AGENT
                        # agent = str(agent_dict.get(player["CharacterID"].lower()))
                        agent = colors.get_agent_from_uuid(player["CharacterID"].lower())
                        
                        #Winrate
                        name = names[player["Subject"]]
                        WinRate = winRate(name)

                        #Headshot%
                        name = names[player["Subject"]]
                        HeadShot = headShot(name)
                        
                        # Top 3 Played Agents
                        name = names[player["Subject"]]
                        MostPlayed = mostPlayed(name)

                        # Peak RR
                        name = names[player["Subject"]]
                        peakRR = getrr(name)

                        # NAME
                        name = Namecolor

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
                        tableClass.add_row_table(table, [party_icon,
                                              agent,
                                              name,
                                              WinRate,
                                              HeadShot,
                                              # views,
                                              skin,
                                              rankName,
                                              rr,
                                              peakRank,
                                              peakRR,
                                              leaderboard,
                                              level,
                                              MostPlayed,
                                              ])
                        bar()
            elif game_state == "PREGAME":
                pregame_stats = pregame.get_pregame_stats()
                server = GAMEPODS[pregame_stats["GamePodID"]]
                Players = pregame_stats["AllyTeam"]["Players"]
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                loadouts = loadoutsClass.get_match_loadouts(pregame.get_pregame_match_id(), pregame_stats, cfg.weapon, valoApiSkins, names,
                                              state="pregame")
                with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = presences.get_presence()
                    partyOBJ = menu.get_party_json(namesClass.get_players_puuid(Players), presence)
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
                        
                        #WRcolor = colors.Winrate_to_color(WinRate)

                        # AGENT
                        agent = agent_color

                        # NAME
                        name = NameColor

                        #Winrate
                        name = names[player["Subject"]]
                        WinRate = winRate(name)

                        #Headshot%
                        name = names[player["Subject"]]
                        HeadShot = headShot(name)
                        
                        # Top 3 Played Agents
                        name = names[player["Subject"]]
                        MostPlayed = mostPlayed(name)

                        # Peak RR
                        name = names[player["Subject"]]
                        peakRR = getrr(name)

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

                        tableClass.add_row_table(table, [party_icon,
                                              agent,
                                              name,
                                              WinRate,
                                              HeadShot,
                                              # views,
                                              skin,
                                              rankName,
                                              rr,
                                              peakRank,
                                              peakRR,
                                              leaderboard,
                                              level,
                                              MostPlayed,
                                              ])
                        bar()
            if game_state == "MENUS":
                Players = menu.get_party_members(Requests.puuid, presence)
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
                        
                        #Winrate
                        WinRate = winRate(name)
                        #WRcolor = colors.Winrate_to_color(WinRate)

                        #Headshot%
                        HeadShot = headShot(name)

                        # RANK
                        rankName = NUMBERTORANKS[playerRank[0]]

                        # RANK RATING
                        rr = playerRank[1]

                        # PEAK RANK
                        peakRank = NUMBERTORANKS[playerRank[3]]

                        # Top 3 Played Agents
                        MostPlayed = mostPlayed(name)

                        # Peak RR
                        peakRR = getrr(name)

                        # LEADERBOARD
                        leaderboard = playerRank[2]

                        # LEVEL
                        level = str(player_level)

                        tableClass.add_row_table(table, [party_icon,
                                              agent,
                                              name,
                                              WinRate,
                                              HeadShot,
                                              "", #Menu only no skin
                                              rankName,
                                              rr,
                                              peakRank,
                                              peakRR,
                                              leaderboard,
                                              level,
                                              MostPlayed
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
            table.field_names = ["Party", "Agent", "Name", "Winrate", "HS %", "Skin", "Rank", "RR", "Peak Rank","peakRR", "pos.", "Level", "Most Played"]
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
