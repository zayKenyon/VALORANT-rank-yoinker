import traceback
import requests
import urllib3
import os
import sys
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
from src.errors import Error

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.system('cls')
os.system(f"title VALORANT rank yoinker v{version}")

server = ""


def program_exit(status: int):  # so we don't need to import the entire sys module
    log(f"exited program with error code {status}")
    raise sys.exit(status)


try:
    Logging = Logging()
    log = Logging.log

    ErrorSRC = Error(log)
    
    Requests = Requests(version, log, ErrorSRC)
    Requests.check_version()
    Requests.check_status()

    cfg = Config(log)

    rank = Rank(Requests, log, before_ascendant_seasons)

    content = Content(Requests, log)

    namesClass = Names(Requests, log)

    presences = Presences(Requests, log)


    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(log, ErrorSRC)
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

    print(color("\nVisit https://vry.netlify.app/matchLoadouts to view full player inventories\n", fore=(255, 253, 205)))
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
                try:
                    server = GAMEPODS[coregame_stats["GamePodID"]]
                except KeyError:
                    server = "New server"
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
                                tableClass.add_row_table(table, ["", "", "", "", "", "", "", "", ""])
                        lastTeam = player['TeamID']
                        lastTeamBoolean = True
                        PLcolor = colors.level_to_color(player_level)

                        # AGENT
                        # agent = str(agent_dict.get(player["CharacterID"].lower()))
                        agent = colors.get_agent_from_uuid(player["CharacterID"].lower())

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
                try:
                    server = GAMEPODS[pregame_stats["GamePodID"]]
                except KeyError:
                    server = "New server"
                Players = pregame_stats["AllyTeam"]["Players"]
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                #temporary until other regions gets fixed?
                # loadouts = loadoutsClass.get_match_loadouts(pregame.get_pregame_match_id(), pregame_stats, cfg.weapon, valoApiSkins, names,
                                            #   state="pregame")
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

                        # AGENT
                        agent = agent_color

                        # NAME
                        name = NameColor

                        # VIEWS
                        # views = get_views(names[player["Subject"]])

                        #temporary until other regions gets fixed?
                        # skin
                        # skin = loadouts[player["Subject"]]

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
                                              # views,
                                              "",
                                              rankName,
                                              rr,
                                              peakRank,
                                              leaderboard,
                                              level,
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

                        tableClass.add_row_table(table, [party_icon,
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
                # program_exit(1)
                time.sleep(9)
            if server != "":
                table.title = f"Valorant status: {title} - {server}"
            else:
                table.title = f"Valorant status: {title}"
            server = ""
            table.field_names = ["Party", "Agent", "Name", "Skin", "Rank", "RR", "Peak Rank", "pos.", "Level"]
            if title is not None:
                print(table)
                print(f"VALORANT rank yoinker v{version}")
        if cfg.cooldown == 0:
            input("Press enter to fetch again...")
        else:
            time.sleep(cfg.cooldown)
except:
    log(traceback.format_exc())
    print(color(
        "The program has encountered an error. If the problem persists, please reach support"
        f" with the logs found in {os.getcwd()}\logs", fore=(255, 0, 0)))
    input("press enter to exit...\n")
    os._exit(1)
