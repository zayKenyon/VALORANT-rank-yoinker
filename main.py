import asyncio
import os
import socket
import sys
import time
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor

import requests
import urllib3
from colr import color as colr
from InquirerPy import inquirer
from rich.console import Console as RichConsole

from src.colors import Colors
from src.config import Config
from src.configurator import configure
from src.constants import *
from src.content import Content
from src.errors import Error
from src.Loadouts import Loadouts
from src.logs import Logging
from src.names import Names
from src.player_stats import PlayerStats, get_estimated_remaining_time
from src.presences import Presences
from src.rank import Rank
from src.requestsV import Requests
from src.rpc import Rpc
from src.server import Server
from src.states.coregame import Coregame
from src.states.menu import Menu
from src.states.pregame import Pregame
from src.stats import Stats
from src.table import Table
from src.websocket import Ws
from src.os_info import get_os

from src.account_manager.account_manager import AccountManager
from src.account_manager.account_config import AccountConfig
from src.account_manager.account_auth import AccountAuth

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

os.system(f"title VALORANT rank yoinker v{version}")

server = ""


def program_exit(status: int):  # so we don't need to import the entire sys module
    log(f"exited program with error code {status}")
    raise sys.exit(status)


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(("10.254.254.254", 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = "127.0.0.1"
    finally:
        s.close()
    return IP



try:
    Logging = Logging()
    log = Logging.log

    # OS Logging
    log(f"Operating system: {get_os()}\n")

    try:
        if len(sys.argv) > 1 and sys.argv[1] == "--config":
            configure()
            run_app = inquirer.confirm(
                message="Do you want to run vRY now?", default=True
            ).execute()
            if run_app:
                os.system("cls")
            else:
                os._exit(0)
        else:
            os.system("cls")
    except Exception as e:
        print("Something went wrong while running configurator!")
        log(f"configurator encountered an error")
        log(str(traceback.format_exc()))
        input("press enter to exit...\n")
        os._exit(1)

    acc_manager = AccountManager(log, AccountConfig, AccountAuth, NUMBERTORANKS)

    ErrorSRC = Error(log, acc_manager)

    Requests.check_version(version, Requests.copy_run_update_script)
    Requests.check_status()
    Requests = Requests(version, log, ErrorSRC)

    cfg = Config(log)

    content = Content(Requests, log)

    rank = Rank(Requests, log, content, before_ascendant_seasons)
    pstats = PlayerStats(Requests, log, cfg)

    namesClass = Names(Requests, log)

    presences = Presences(Requests, log)

    menu = Menu(Requests, log, presences)
    pregame = Pregame(Requests, log)
    coregame = Coregame(Requests, log)

    Server = Server(log, ErrorSRC)
    Server.start_server()

    agent_dict, dynamic_agent_colors = content.get_all_agents()
    for name_lower, rgb in dynamic_agent_colors.items():
        if name_lower not in AGENTCOLORLIST:
            AGENTCOLORLIST[name_lower] = rgb

    map_info = content.get_all_maps()
    map_urls = content.get_map_urls(map_info)
    map_splashes = content.get_map_splashes(map_info)

    current_map = coregame.get_current_map(map_urls, map_splashes)

    colors = Colors(log, hide_names, agent_dict, AGENTCOLORLIST)

    loadoutsClass = Loadouts(Requests, log, colors, Server, current_map)
    table = Table(cfg, log)

    stats = Stats()

    if cfg.get_feature_flag("discord_rpc"):
        rpc = Rpc(map_urls, gamemodes, colors, log)
    else:
        rpc = None

    Wss = Ws(Requests.lockfile, Requests, cfg, colors, hide_names, Server, rpc)
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    # loop.run_forever()

    log(f"VALORANT rank yoinker v{version}")

    valoApiSkins = requests.get("https://valorant-api.com/v1/weapons/skins")
    gameContent = content.get_content()
    seasonID = content.get_latest_season_id(gameContent)
    previousSeasonID = content.get_previous_season_id(gameContent)
    lastGameState = ""

    # Cache rank+stats per player for the current match so PREGAME data can be reused in INGAME
    match_player_cache = {
        "match_id": None,
        "players": {},  # puuid -> {"playerRank", "previousPlayerRank", "ppstats", "ts"}
    }
    MATCH_PLAYER_CACHE_TTL_SECONDS = 300  # safety TTL

    def reset_match_player_cache(match_id=None):
        match_player_cache["match_id"] = match_id
        match_player_cache["players"] = {}

    def ensure_match_player_cache(match_id):
        if not match_id:
            return

        # New match => reset cache
        if match_player_cache["match_id"] != match_id:
            reset_match_player_cache(match_id)
            return

        # TTL cleanup (safety)
        now = time.time()
        expired = []
        for puuid, cached in match_player_cache["players"].items():
            ts = cached.get("ts", now)
            if (now - ts) > MATCH_PLAYER_CACHE_TTL_SECONDS:
                expired.append(puuid)

        for puuid in expired:
            del match_player_cache["players"][puuid]

    def get_or_fetch_rank_and_stats(player_subject, current_match_id):
        if current_match_id:
            ensure_match_player_cache(current_match_id)
            cached = match_player_cache["players"].get(player_subject)
            if cached is not None:
                return (
                    cached["playerRank"],
                    cached["previousPlayerRank"],
                    cached["ppstats"],
                )

        # Cache miss -> fetch
        playerRank = rank.get_rank(player_subject, seasonID)
        previousPlayerRank = rank.get_rank(player_subject, previousSeasonID)
        ppstats = pstats.get_stats(player_subject)

        if current_match_id and match_player_cache["match_id"] == current_match_id:
            match_player_cache["players"][player_subject] = {
                "playerRank": dict(playerRank) if isinstance(playerRank, dict) else playerRank,
                "previousPlayerRank": dict(previousPlayerRank) if isinstance(previousPlayerRank, dict) else previousPlayerRank,
                "ppstats": dict(ppstats) if isinstance(ppstats, dict) else ppstats,
                "ts": time.time(),
            }

        return playerRank, previousPlayerRank, ppstats

    print("\nvRY Mobile", color(f"- {get_ip()}:{cfg.port}", fore=(255, 127, 80)))

    print(
        color(
            "\nVisit https://vry.netlify.app/matchLoadouts to view full player inventories\n",
            fore=(255, 253, 205),
        )
    )

    richConsole = RichConsole()

    firstTime = True
    firstPrint = True
    while True:
        table.clear()
        table.set_default_field_names()
        table.reset_runtime_col_flags()
        lobby_ranks = []

        # check if short ranks should be used
        if cfg.get_feature_flag("short_ranks"):
            Ranks = SHORT_NUMBERTORANKS
        else:
            Ranks = NUMBERTORANKS

        try:

            # loop = asyncio.get_event_loop()
            # loop.run_until_complete(Wss.conntect_to_websocket())
            # if firstTime:
            #     loop = asyncio.new_event_loop()
            #     asyncio.set_event_loop(loop)
            #     game_state = loop.run_until_complete(Wss.conntect_to_websocket(game_state))
            if firstTime:
                run = True
                while run:
                    presence = presences.get_presence()
                    private_presence = presences.get_private_presence(presence)
                    # wait until your own valorant presence is initialized
                    if private_presence is not None:
                        if cfg.get_feature_flag("discord_rpc"):
                            rpc.set_rpc(private_presence)
                        game_state = presences.get_game_state(presence)
                        if game_state is not None:
                            run = False
                    time.sleep(2)
                log(f"first game state: {game_state}")
            else:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                previous_game_state = game_state
                game_state = loop.run_until_complete(
                    Wss.recconect_to_websocket(game_state)
                )
                # We invalidate the cached responses when going from any state to menus
                if previous_game_state != game_state and game_state == "MENUS":
                    rank.invalidate_cached_responses()
                    reset_match_player_cache()
                    if hasattr(pstats, "clear_runtime_cache"):
                        pstats.clear_runtime_cache()
                log(f"new game state: {game_state}")
                loop.close()
            firstTime = False
            # loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(loop)
            # loop.run_until_complete()
        except TypeError:
            game_state = "DISCONNECTED"
            reset_match_player_cache()
            if hasattr(pstats, "clear_runtime_cache"):
                pstats.clear_runtime_cache()

        if game_state == "DISCONNECTED":
            richConsole.print("[yellow]Disconnected from Valorant. Attempting to reconnect...[/yellow]")
            # Loop waits for the Valorant client to respond
            while True:
                # Rereads the lockfile
                Requests.lockfile = Requests.get_lockfile()

                if Requests.lockfile is None:
                    time.sleep(5)
                    continue

                presence_check = presences.get_presence()
                
                if presence_check is not None:
                    break 
                
                time.sleep(5)

            richConsole.print("[green]Reconnected successfully! Loading...[/green]")
            
            Requests.get_headers(refresh=True)

            Wss = Ws(Requests.lockfile, Requests, cfg, colors, hide_names, Server, rpc)

            firstTime = True 
            lastGameState = ""
            reset_match_player_cache()
            if hasattr(pstats, "clear_runtime_cache"):
                pstats.clear_runtime_cache()
            continue

        if True:
            log(f"getting new {game_state} scoreboard")
            lastGameState = game_state
            game_state_dict = {
                "INGAME": color("In-Game", fore=(241, 39, 39)),
                "PREGAME": color("Agent Select", fore=(103, 237, 76)),
                "MENUS": color("In-Menus", fore=(238, 241, 54)),
            }

            if (not firstPrint) and cfg.get_feature_flag("pre_cls"):
                os.system("cls")

            is_leaderboard_needed = False
            
            # get new presence
            presence = presences.get_presence()
            priv_presence = presences.get_private_presence(presence)
            
            # Temp fix: Riot is swapping between nested and flat API structures.
            party_state = ""
            if "partyPresenceData" in priv_presence: # Check for nested structure
                party_state = priv_presence["partyPresenceData"]["partyState"]
            elif "partyState" in priv_presence: # Check for flattened structure
                party_state = priv_presence["partyState"]
            else:
                # No known structure found, log and fail
                log("ERROR: Unknown presence API structure in 'main'.")
                party_state = priv_presence["partyPresenceData"]["partyState"]
            
            if (
                priv_presence["provisioningFlow"] == "CustomGame"
                or party_state == "CUSTOM_GAME_SETUP"
            ):
                gamemode = "Custom Game"
            else:
                gamemode = gamemodes.get(priv_presence["queueId"])

            heartbeat_data = {
                "time": int(time.time()),
                "state": game_state,
                "mode": gamemode,
                "puuid": Requests.puuid,
                "players": {},
            }

            if game_state == "INGAME":
                coregame_stats = coregame.get_coregame_stats()
                if coregame_stats == None:
                    continue
                coregame_match_id = coregame.get_coregame_match_id()
                ensure_match_player_cache(coregame_match_id)
                Players = coregame_stats["Players"]
                # data for chat to function
                partyMembers = menu.get_party_members(Requests.puuid, presence)
                partyMembersList = [a["Subject"] for a in partyMembers]

                players_data = {}
                players_data.update({"ignore": partyMembersList})
                for player in Players:
                    if player["Subject"] == Requests.puuid:
                        if cfg.get_feature_flag("discord_rpc"):
                            rpc.set_data({"agent": player["CharacterID"]})
                    players_data.update(
                        {
                            player["Subject"]: {
                                "team": player["TeamID"],
                                "agent": player["CharacterID"],
                                "streamer_mode": player["PlayerIdentity"]["Incognito"],
                            }
                        }
                    )
                Wss.set_player_data(players_data)

                server = coregame_stats.get("GamePodID", "")
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                loadouts_arr = loadoutsClass.get_match_loadouts(
                    coregame_match_id,
                    Players,
                    cfg.weapon,
                    valoApiSkins,
                    names,
                    state="game",
                )
                loadouts = loadouts_arr[0]
                loadouts_data = loadouts_arr[1]
                # with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                isRange = False
                playersLoaded = 1

                heartbeat_data["map"] = (map_urls[coregame_stats["MapID"].lower()],)
                with richConsole.status("Loading Players...") as status:
                    partyOBJ = menu.get_party_json(
                        namesClass.get_players_puuid(Players), presence
                    )
                    # log(f"retrieved names dict: {names}")
                    Players.sort(
                        key=lambda Players: Players["PlayerIdentity"].get(
                            "AccountLevel"
                        ),
                        reverse=True,
                    )
                    Players.sort(key=lambda Players: Players["TeamID"], reverse=True)
                    partyCount = 0
                    partyNum = 0
                    partyIcons = {}
                    lastTeamBoolean = False
                    lastTeam = "Red"

                    already_played_with = []
                    stats_data = stats.read_data()

                    # Pre-fetch player stats in parallel
                    ensure_match_player_cache(coregame_match_id)
                    with ThreadPoolExecutor(max_workers=len(Players)) as executor:
                        futures = [executor.submit(get_or_fetch_rank_and_stats, p["Subject"], coregame_match_id) for p in Players]
                        for future in futures: future.result()

                    for p in Players:
                        if p["Subject"] == Requests.puuid:
                            allyTeam = p["TeamID"]
                    for player in Players:
                        status.update(
                            f"Loading players... [{playersLoaded}/{len(Players)}]"
                        )
                        playersLoaded += 1

                        if player["Subject"] in stats_data.keys():
                            if (
                                player["Subject"] != Requests.puuid
                                and player["Subject"] not in partyMembersList
                            ):
                                curr_player_stat = stats_data[player["Subject"]][-1]
                                i = 1
                                while (
                                    curr_player_stat["match_id"] == coregame.match_id
                                    and len(stats_data[player["Subject"]]) > i
                                ):
                                    i += 1
                                    # if curr_player_stat["match_id"] == coregame.match_id and len(stats_data[player["Subject"]]) > 1:
                                    curr_player_stat = stats_data[player["Subject"]][-i]
                                if curr_player_stat["match_id"] != coregame.match_id:
                                    # checking for party memebers and self players
                                    times = 0
                                    times_with = 0
                                    times_against = 0
                                    m_set = ()
                                    for m in stats_data[player["Subject"]]:
                                        if (
                                            m["match_id"] != coregame.match_id
                                            and m["match_id"] not in m_set
                                        ):
                                            times += 1
                                            m_set += (m["match_id"],)
                                            role = m.get("team", "Ally")
                                            if role == "Ally":
                                                times_with += 1
                                            else:
                                                times_against += 1
                                    
                                    last_encountered_team = curr_player_stat.get("team", "Ally")
                                    last_encountered_team_str = "your" if last_encountered_team == "Ally" else "enemy"

                                    if player["PlayerIdentity"]["Incognito"] == False:
                                        already_played_with.append(
                                            {
                                                "times": times,
                                                "with": times_with,
                                                "against": times_against,
                                                "last_team": last_encountered_team_str,
                                                "name": curr_player_stat["name"],
                                                "agent": curr_player_stat["agent"],
                                                "time_diff": time.time()
                                                - curr_player_stat["epoch"],
                                            }
                                        )
                                    else:
                                        if player["TeamID"] == allyTeam:
                                            team_string = "your"
                                        else:
                                            team_string = "enemy"
                                        already_played_with.append(
                                            {
                                                "times": times,
                                                "with": times_with,
                                                "against": times_against,
                                                "last_team": last_encountered_team_str,
                                                "name": agent_dict.get(
                                                    player["CharacterID"].lower(), "Unknown"
                                                )
                                                + " on "
                                                + team_string
                                                + " team",
                                                "agent": curr_player_stat["agent"],
                                                "time_diff": time.time()
                                                - curr_player_stat["epoch"],
                                            }
                                        )

                        party_icon = ""
                        # set party premade icon
                        for party in partyOBJ:
                            if player["Subject"] in partyOBJ[party]:
                                if party not in partyIcons:
                                    partyIcons.update(
                                        {party: PARTYICONLIST[partyCount]}
                                    )
                                    # PARTY_ICON
                                    party_icon = PARTYICONLIST[partyCount]
                                    partyNum = partyCount + 1
                                    partyCount += 1
                                else:
                                    # PARTY_ICON
                                    party_icon = partyIcons[party]
                        playerRank, previousPlayerRank, ppstats = get_or_fetch_rank_and_stats(
                            player["Subject"], coregame_match_id
                        )
                        if playerRank["rank"] > 2:
                            lobby_ranks.append(playerRank["rank"])

                        if player["Subject"] == Requests.puuid:
                            if cfg.get_feature_flag("discord_rpc"):
                                rpc.set_data(
                                    {
                                        "rank": playerRank["rank"],
                                        "rank_name": colors.escape_ansi(
                                            NUMBERTORANKS[playerRank["rank"]]
                                        )
                                        + " | "
                                        + str(playerRank["rr"])
                                        + "rr",
                                    }
                                )
                        # rankStatus = playerRank[1]
                        # useless code since rate limit is handled in the requestsV
                        # while not rankStatus:
                        #     print("You have been rate limited, 😞 waiting 10 seconds!")
                        #     time.sleep(10)
                        #     playerRank = rank.get_rank(player["Subject"], seasonID)
                        #     rankStatus = playerRank[1]

                        hs = ppstats["hs"]
                        kd = ppstats["kd"]

                        rr_numeric_value = ppstats["RankedRatingEarned"]
                        afk_penalty = ppstats["AFKPenalty"]
                        ranked_rating_earned = colors.get_rr_gradient(
                            rr_numeric_value, afk_penalty
                        )

                        player_level = player["PlayerIdentity"].get("AccountLevel")

                        if player["PlayerIdentity"]["Incognito"]:
                            Namecolor = colors.get_color_from_team(
                                player["TeamID"],
                                names[player["Subject"]],
                                player["Subject"],
                                Requests.puuid,
                                agent=player["CharacterID"],
                                party_members=partyMembersList,
                            )
                        else:
                            Namecolor = colors.get_color_from_team(
                                player["TeamID"],
                                names[player["Subject"]],
                                player["Subject"],
                                Requests.puuid,
                                party_members=partyMembersList,
                            )
                        if lastTeam != player["TeamID"]:
                            if lastTeamBoolean:
                                table.add_empty_row()
                        lastTeam = player["TeamID"]
                        lastTeamBoolean = True
                        if player["PlayerIdentity"]["HideAccountLevel"]:
                            if (
                                player["Subject"] == Requests.puuid
                                or player["Subject"] in partyMembersList
                                or hide_levels == False
                            ):
                                PLcolor = colors.level_to_color(player_level)
                            else:
                                PLcolor = ""
                        else:
                            PLcolor = colors.level_to_color(player_level)
                        # AGENT
                        # agent = str(agent_dict.get(player["CharacterID"].lower()))
                        agent = colors.get_agent_from_uuid(
                            player["CharacterID"].lower()
                        )
                        if agent == "" and len(Players) == 1:
                            isRange = True

                        # NAME
                        name = Namecolor

                        # VIEWS
                        # views = get_views(names[player["Subject"]])

                        # skin
                        skin = loadouts.get(player["Subject"], "")

                        # RANK
                        rankName = Ranks[playerRank["rank"]]
                        if cfg.get_feature_flag("aggregate_rank_rr") and cfg.table.get(
                            "rr"
                        ):
                            rankName += f" ({playerRank['rr']})"

                        # RANK RATING
                        rr = playerRank["rr"]

                        # short peak rank string
                        has_letter = any(
                            c.isalpha() for c in str(playerRank["peakrankep"])
                        )
                        peakRankAct = (
                            f" ({playerRank['peakrankep']}a{playerRank['peakrankact']})"
                            if has_letter
                            else f" (e{playerRank['peakrankep']}a{playerRank['peakrankact']})"
                        )
                        if not cfg.get_feature_flag("peak_rank_act"):
                            peakRankAct = ""

                        # PEAK RANK
                        peakRank = Ranks[playerRank["peakrank"]] + peakRankAct

                        # PREVIOUS RANK
                        previousRank = Ranks[previousPlayerRank["rank"]]

                        # LEADERBOARD
                        leaderboard = playerRank["leaderboard"]

                        hs = colors.get_hs_gradient(hs)
                        wr = (
                            colors.get_wr_gradient(playerRank["wr"])
                            + f" ({playerRank['numberofgames']})"
                        )

                        if int(leaderboard) > 0:
                            is_leaderboard_needed = True

                        # LEVEL
                        level = PLcolor

                        # SMURF / BOOST PROBABILITY
                        warning = ""
                        smurf_prob = 0
                        if player_level != "N/A" and isinstance(player_level, int):
                            if player_level < 30: smurf_prob += 40
                            elif player_level < 50: smurf_prob += 20
                            elif player_level < 100: smurf_prob += 10
                            
                        # Advanced metrics from last 20 games
                        avg_rr_gain = ppstats.get("avg_rr_gain", "N/A")
                        win_rate_last_20 = ppstats.get("win_rate_last_20", "N/A")
                        streak = ppstats.get("streak", "N/A")
                        
                        if avg_rr_gain != "N/A":
                            try:
                                if float(avg_rr_gain) >= 28: smurf_prob += 40
                                elif float(avg_rr_gain) >= 25: smurf_prob += 25
                                elif float(avg_rr_gain) >= 22: smurf_prob += 10
                            except ValueError: pass

                        if win_rate_last_20 != "N/A":
                            try:
                                if float(win_rate_last_20) >= 75: smurf_prob += 35
                                elif float(win_rate_last_20) >= 65: smurf_prob += 20
                                elif float(win_rate_last_20) <= 35: smurf_prob -= 30
                            except ValueError: pass

                        if streak != "N/A":
                            try:
                                if int(streak) >= 5: smurf_prob += 20
                                elif int(streak) >= 3: smurf_prob += 10
                                elif int(streak) <= -5: smurf_prob -= 30
                            except ValueError: pass
                            
                        if kd != "N/A":
                            try:
                                raw_kd = float(kd)
                                if raw_kd > 1.5: smurf_prob += 20
                                elif raw_kd > 1.3: smurf_prob += 10
                                elif raw_kd < 0.7: smurf_prob -= 20
                            except ValueError: pass

                        # Check for headshot percentage in smurf probability
                        hs_raw = ppstats.get("hs", "N/A")
                        if hs_raw != "N/A":
                            try:
                                raw_hs = float(hs_raw)
                                if raw_hs >= 40: smurf_prob += 20
                                elif raw_hs >= 35: smurf_prob += 10
                            except ValueError: pass
                            
                        smurf_prob = max(0, min(100, smurf_prob))
                        
                        if smurf_prob >= 75:
                            warning = colr("🔥 SMURF 🔥", fore=(255, 50, 50))
                        elif smurf_prob >= 50:
                            warning = colr("⚠ SUSPECT", fore=(255, 165, 0))
                        elif smurf_prob <= 10 and kd != "N/A":
                            try:
                                if float(kd) < 0.7:
                                    warning = colr("Boosted?", fore=(128, 128, 128))
                            except ValueError: pass

                        fav_weapon = ppstats.get("fav_weapon", "N/A")
                        fav_weapon_kills = ppstats.get("fav_weapon_kills", 0)
                        notes_parts = []
                        if warning:
                            notes_parts.append(warning)
                        if fav_weapon != "N/A" and fav_weapon_kills > 0:
                            notes_parts.append(f"Fav: {fav_weapon} ({fav_weapon_kills}k)")
                        final_notes = " | ".join(notes_parts)

                        table.add_row_table(
                            [
                                party_icon,
                                agent,
                                name,
                                # views,
                                skin,
                                rankName,
                                rr,
                                peakRank,
                                previousRank,
                                leaderboard,
                                hs,
                                wr,
                                kd,
                                level,
                                ranked_rating_earned,
                                final_notes,
                            ]
                        )

                        heartbeat_data["players"][player["Subject"]] = {
                            "puuid": player["Subject"],
                            "name": names[player["Subject"]],
                            "partyNumber": partyNum if party_icon != "" else 0,
                            "agent": agent_dict.get(player["CharacterID"].lower(), "Unknown"),
                            "rank": playerRank["rank"],
                            "peakRank": playerRank["peakrank"],
                            "peakRankAct": peakRankAct,
                            "rr": rr,
                            "kd": ppstats["kd"],
                            "headshotPercentage": ppstats["hs"],
                            "winPercentage": f"{playerRank['wr']} ({playerRank['numberofgames']})",
                            "level": player_level,
                            "agentImgLink": loadouts_data["Players"][
                                player["Subject"]
                            ].get("Agent", None),
                            "team": loadouts_data["Players"][player["Subject"]].get(
                                "Team", None
                            ),
                            "sprays": loadouts_data["Players"][player["Subject"]].get(
                                "Sprays", None
                            ),
                            "title": loadouts_data["Players"][player["Subject"]].get(
                                "Title", None
                            ),
                            "playerCard": loadouts_data["Players"][
                                player["Subject"]
                            ].get("PlayerCard", None),
                            "weapons": loadouts_data["Players"][player["Subject"]].get(
                                "Weapons", None
                            ),
                        }

                        stats.save_data(
                            {
                                player["Subject"]: {
                                    "name": names[player["Subject"]],
                                    "agent": agent_dict.get(player["CharacterID"].lower(), "Unknown"),
                                    "map": current_map,
                                    "rank": playerRank["rank"],
                                    "rr": rr,
                                    "match_id": coregame.match_id,
                                    "epoch": time.time(),
                                    "team": "Ally" if player["TeamID"] == allyTeam else "Enemy",
                                }
                            }
                        )
                        # bar()
            elif game_state == "PREGAME":
                already_played_with = []
                pregame_stats = pregame.get_pregame_stats()
                if pregame_stats == None:
                    continue
                server = pregame_stats.get("GamePodID", "")
                Players = pregame_stats["AllyTeam"]["Players"]
                presences.wait_for_presence(namesClass.get_players_puuid(Players))
                names = namesClass.get_names_from_puuids(Players)
                pregame_match_id = pregame_stats.get("ID")
                ensure_match_player_cache(pregame_match_id)
                # temporary until other regions gets fixed?
                # loadouts = loadoutsClass.get_match_loadouts(pregame.get_pregame_match_id(), pregame_stats, cfg.weapon, valoApiSkins, names,
                #   state="pregame")
                playersLoaded = 1
                with richConsole.status("Loading Players...") as status:
                    # with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    presence = presences.get_presence()
                    partyOBJ = menu.get_party_json(
                        namesClass.get_players_puuid(Players), presence
                    )
                    partyMembers = menu.get_party_members(Requests.puuid, presence)
                    partyMembersList = [a["Subject"] for a in partyMembers]
                    # log(f"retrieved names dict: {names}")
                    Players.sort(
                        key=lambda Players: Players["PlayerIdentity"].get(
                            "AccountLevel"
                        ),
                        reverse=True,
                    )
                    partyCount = 0
                    partyIcons = {}

                    # Pre-fetch player stats in parallel
                    with ThreadPoolExecutor(max_workers=len(Players)) as executor:
                        futures = [executor.submit(get_or_fetch_rank_and_stats, p["Subject"], pregame_match_id) for p in Players]
                        for future in futures: future.result()

                    for player in Players:
                        status.update(
                            f"Loading players... [{playersLoaded}/{len(Players)}]"
                        )
                        playersLoaded += 1
                        party_icon = ""

                        # set party premade icon
                        for party in partyOBJ:
                            if player["Subject"] in partyOBJ[party]:
                                if party not in partyIcons:
                                    partyIcons.update(
                                        {party: PARTYICONLIST[partyCount]}
                                    )
                                    # PARTY_ICON
                                    party_icon = PARTYICONLIST[partyCount]
                                    partyNum = partyCount + 1
                                else:
                                    # PARTY_ICON
                                    party_icon = partyIcons[party]
                                partyCount += 1
                        playerRank, previousPlayerRank, ppstats = get_or_fetch_rank_and_stats(
                            player["Subject"], pregame_match_id
                        )
                        if playerRank["rank"] > 2:
                            lobby_ranks.append(playerRank["rank"])

                        if player["Subject"] == Requests.puuid:
                            if cfg.get_feature_flag("discord_rpc"):
                                rpc.set_data(
                                    {
                                        "rank": playerRank["rank"],
                                        "rank_name": colors.escape_ansi(
                                            NUMBERTORANKS[playerRank["rank"]]
                                        )
                                        + " | "
                                        + str(playerRank["rr"])
                                        + "rr",
                                    }
                                )
                        # rankStatus = playerRank[1]
                        # useless code since rate limit is handled in the requestsV
                        # while not rankStatus:
                        #     print("You have been rate limited, 😞 waiting 10 seconds!")
                        #     time.sleep(10)
                        #     playerRank = rank.get_rank(player["Subject"], seasonID)
                        #     rankStatus = playerRank[1]
                        # playerRank = playerRank[0]

                        hs = ppstats["hs"]
                        kd = ppstats["kd"]

                        rr_numeric_value = ppstats["RankedRatingEarned"]
                        afk_penalty = ppstats["AFKPenalty"]
                        ranked_rating_earned = colors.get_rr_gradient(
                            rr_numeric_value, afk_penalty
                        )

                        player_level = player["PlayerIdentity"].get("AccountLevel")
                        if player["PlayerIdentity"]["Incognito"]:
                            NameColor = colors.get_color_from_team(
                                pregame_stats["Teams"][0]["TeamID"],
                                names[player["Subject"]],
                                player["Subject"],
                                Requests.puuid,
                                agent=player["CharacterID"],
                                party_members=partyMembersList,
                            )
                        else:
                            NameColor = colors.get_color_from_team(
                                pregame_stats["Teams"][0]["TeamID"],
                                names[player["Subject"]],
                                player["Subject"],
                                Requests.puuid,
                                party_members=partyMembersList,
                            )

                        if player["PlayerIdentity"]["HideAccountLevel"]:
                            if (
                                player["Subject"] == Requests.puuid
                                or player["Subject"] in partyMembersList
                                or hide_levels == False
                            ):
                                PLcolor = colors.level_to_color(player_level)
                            else:
                                PLcolor = ""
                        else:
                            PLcolor = colors.level_to_color(player_level)
                        if player["CharacterSelectionState"] == "locked":
                            agent_color = color(
                                agent_dict.get(player["CharacterID"].lower(), "Unknown"),
                                fore=(255, 255, 255),
                            )
                        elif player["CharacterSelectionState"] == "selected":
                            agent_color = color(
                                agent_dict.get(player["CharacterID"].lower(), "Unknown"),
                                fore=(128, 128, 128),
                            )
                        else:
                            agent_color = color(
                                agent_dict.get(player["CharacterID"].lower(), "Unknown"),
                                fore=(54, 53, 51),
                            )

                        # AGENT
                        agent = agent_color

                        # NAME
                        name = NameColor

                        # VIEWS
                        # views = get_views(names[player["Subject"]])

                        # temporary until other regions gets fixed?
                        # skin
                        # skin = loadouts[player["Subject"]]

                        # RANK
                        rankName = Ranks[playerRank["rank"]]
                        if cfg.get_feature_flag("aggregate_rank_rr") and cfg.table.get(
                            "rr"
                        ):
                            rankName += f" ({playerRank['rr']})"

                        # RANK RATING
                        rr = playerRank["rr"]

                        # short peak rank string
                        has_letter = any(
                            c.isalpha() for c in str(playerRank["peakrankep"])
                        )
                        peakRankAct = (
                            f" ({playerRank['peakrankep']}a{playerRank['peakrankact']})"
                            if has_letter
                            else f" (e{playerRank['peakrankep']}a{playerRank['peakrankact']})"
                        )
                        if not cfg.get_feature_flag("peak_rank_act"):
                            peakRankAct = ""
                        # PEAK RANK
                        peakRank = Ranks[playerRank["peakrank"]] + peakRankAct

                        # PREVIOUS RANK
                        previousRank = Ranks[previousPlayerRank["rank"]]

                        # LEADERBOARD
                        leaderboard = playerRank["leaderboard"]

                        hs = colors.get_hs_gradient(hs)
                        wr = (
                            colors.get_wr_gradient(playerRank["wr"])
                            + f" ({playerRank['numberofgames']})"
                        )

                        if int(leaderboard) > 0:
                            is_leaderboard_needed = True

                        # LEVEL
                        level = PLcolor

                        # SMURF / BOOST PROBABILITY
                        warning = ""
                        smurf_prob = 0
                        if player_level != "N/A" and isinstance(player_level, int):
                            if player_level < 30: smurf_prob += 40
                            elif player_level < 50: smurf_prob += 20
                            elif player_level < 100: smurf_prob += 10
                            
                        # Advanced metrics from last 20 games
                        avg_rr_gain = ppstats.get("avg_rr_gain", "N/A")
                        win_rate_last_20 = ppstats.get("win_rate_last_20", "N/A")
                        streak = ppstats.get("streak", "N/A")
                        
                        if avg_rr_gain != "N/A":
                            try:
                                if float(avg_rr_gain) >= 28: smurf_prob += 40
                                elif float(avg_rr_gain) >= 25: smurf_prob += 25
                                elif float(avg_rr_gain) >= 22: smurf_prob += 10
                            except ValueError: pass

                        if win_rate_last_20 != "N/A":
                            try:
                                if float(win_rate_last_20) >= 75: smurf_prob += 35
                                elif float(win_rate_last_20) >= 65: smurf_prob += 20
                                elif float(win_rate_last_20) <= 35: smurf_prob -= 30
                            except ValueError: pass

                        if streak != "N/A":
                            try:
                                if int(streak) >= 5: smurf_prob += 20
                                elif int(streak) >= 3: smurf_prob += 10
                                elif int(streak) <= -5: smurf_prob -= 30
                            except ValueError: pass
                            
                        if kd != "N/A":
                            try:
                                raw_kd = float(kd)
                                if raw_kd > 1.5: smurf_prob += 20
                                elif raw_kd > 1.3: smurf_prob += 10
                                elif raw_kd < 0.7: smurf_prob -= 20
                            except ValueError: pass

                        # Check for headshot percentage in smurf probability
                        hs_raw = ppstats.get("hs", "N/A")
                        if hs_raw != "N/A":
                            try:
                                raw_hs = float(hs_raw)
                                if raw_hs >= 40: smurf_prob += 20
                                elif raw_hs >= 35: smurf_prob += 10
                            except ValueError: pass
                            
                        smurf_prob = max(0, min(100, smurf_prob))
                        
                        if smurf_prob >= 75:
                            warning = colr("🔥 SMURF 🔥", fore=(255, 50, 50))
                        elif smurf_prob >= 50:
                            warning = colr("⚠ SUSPECT", fore=(255, 165, 0))
                        elif smurf_prob <= 10 and kd != "N/A":
                            try:
                                if float(kd) < 0.7:
                                    warning = colr("Boosted?", fore=(128, 128, 128))
                            except ValueError: pass

                        fav_weapon = ppstats.get("fav_weapon", "N/A")
                        fav_weapon_kills = ppstats.get("fav_weapon_kills", 0)
                        notes_parts = []
                        if warning:
                            notes_parts.append(warning)
                        if fav_weapon != "N/A" and fav_weapon_kills > 0:
                            notes_parts.append(f"Fav: {fav_weapon} ({fav_weapon_kills}k)")
                        final_notes = " | ".join(notes_parts)

                        table.add_row_table(
                            [
                                party_icon,
                                agent,
                                name,
                                # views,
                                "",
                                rankName,
                                rr,
                                peakRank,
                                previousRank,
                                leaderboard,
                                hs,
                                wr,
                                kd,
                                level,
                                ranked_rating_earned,
                                final_notes,
                            ]
                        )

                        heartbeat_data["players"][player["Subject"]] = {
                            "name": names[player["Subject"]],
                            "partyNumber": partyNum if party_icon != "" else 0,
                            "agent": agent_dict.get(player["CharacterID"].lower(), "Unknown"),
                            "rank": playerRank["rank"],
                            "peakRank": playerRank["peakrank"],
                            "peakRankAct": peakRankAct,
                            "level": player_level,
                            "rr": rr,
                            "kd": ppstats["kd"],
                            "headshotPercentage": ppstats["hs"],
                            "winPercentage": f"{playerRank['wr']} ({playerRank['numberofgames']})",
                        }

                        # bar()
            if game_state == "MENUS":
                reset_match_player_cache()
                if hasattr(pstats, "clear_runtime_cache"):
                    pstats.clear_runtime_cache()

                server = ""
                already_played_with = []
                Players = menu.get_party_members(Requests.puuid, presence)
                names = namesClass.get_names_from_puuids(Players)
                playersLoaded = 1
                with richConsole.status("Loading Players...") as status:
                    # with alive_bar(total=len(Players), title='Fetching Players', bar='classic2') as bar:
                    # log(f"retrieved names dict: {names}")
                    Players.sort(
                        key=lambda Players: Players["PlayerIdentity"].get(
                            "AccountLevel"
                        ),
                        reverse=True,
                    )
                    seen = []
                    for player in Players:

                        if player not in seen:
                            status.update(
                                f"Loading players... [{playersLoaded}/{len(Players)}]"
                            )
                            playersLoaded += 1
                            party_icon = PARTYICONLIST[0]
                            playerRank = rank.get_rank(player["Subject"], seasonID)
                            previousPlayerRank = rank.get_rank(
                                player["Subject"], previousSeasonID
                            )
                            if player["Subject"] == Requests.puuid:
                                if cfg.get_feature_flag("discord_rpc"):
                                    rpc.set_data(
                                        {
                                            "rank": playerRank["rank"],
                                            "rank_name": colors.escape_ansi(
                                                NUMBERTORANKS[playerRank["rank"]]
                                            )
                                            + " | "
                                            + str(playerRank["rr"])
                                            + "rr",
                                        }
                                    )

                            # rankStatus = playerRank[1]
                            # useless code since rate limit is handled in the requestsV
                            # while not rankStatus:
                            #     print("You have been rate limited, 😞 waiting 10 seconds!")
                            #     time.sleep(10)
                            #     playerRank = rank.get_rank(player["Subject"], seasonID)
                            #     rankStatus = playerRank[1]
                            # playerRank = playerRank["rank"]

                            ppstats = pstats.get_stats(player["Subject"])
                            hs = ppstats["hs"]
                            kd = ppstats["kd"]

                            rr_numeric_value = ppstats["RankedRatingEarned"]
                            afk_penalty = ppstats["AFKPenalty"]
                            ranked_rating_earned = colors.get_rr_gradient(
                                rr_numeric_value, afk_penalty
                            )

                            player_level = player["PlayerIdentity"].get("AccountLevel")
                            PLcolor = colors.level_to_color(player_level)

                            # AGENT
                            agent = ""

                            # NAME
                            name = color(names[player["Subject"]], fore=(76, 151, 237))

                            # RANK
                            rankName = Ranks[playerRank["rank"]]
                            if cfg.get_feature_flag(
                                "aggregate_rank_rr"
                            ) and cfg.table.get("rr"):
                                rankName += f" ({playerRank['rr']})"

                            # RANK RATING
                            rr = playerRank["rr"]

                            # short peak rank string
                            has_letter = any(
                                c.isalpha() for c in str(playerRank["peakrankep"])
                            )
                            peakRankAct = (
                                f" ({playerRank['peakrankep']}a{playerRank['peakrankact']})"
                                if has_letter
                                else f" (e{playerRank['peakrankep']}a{playerRank['peakrankact']})"
                            )
                            if not cfg.get_feature_flag("peak_rank_act"):
                                peakRankAct = ""

                            # PEAK RANK
                            peakRank = (
                                Ranks[playerRank["peakrank"]] + peakRankAct
                            )

                            # PREVIOUS RANK
                            previousRank = Ranks[previousPlayerRank["rank"]]

                            # LEADERBOARD
                            leaderboard = playerRank["leaderboard"]

                            hs = colors.get_hs_gradient(hs)
                            wr = (
                                colors.get_wr_gradient(playerRank["wr"])
                                + f" ({playerRank['numberofgames']})"
                            )

                            if int(leaderboard) > 0:
                                is_leaderboard_needed = True

                            # LEVEL
                            level = PLcolor

                            table.add_row_table(
                                [
                                    party_icon,
                                    agent,
                                    name,
                                    "",
                                    rankName,
                                    rr,
                                    peakRank,
                                    previousRank,
                                    leaderboard,
                                    hs,
                                    wr,
                                    kd,
                                    level,
                                    ranked_rating_earned,
                                ]
                            )

                            heartbeat_data["players"][player["Subject"]] = {
                                "name": names[player["Subject"]],
                                "rank": playerRank["rank"],
                                "peakRank": playerRank["peakrank"],
                                "peakRankAct": peakRankAct,
                                "level": player_level,
                                "rr": rr,
                                "kd": ppstats["kd"],
                                "headshotPercentage": ppstats["hs"],
                                "winPercentage": f"{playerRank['wr']} ({playerRank['numberofgames']})",
                                "playerCard": f"https://media.valorant-api.com/playercards/{player['PlayerIdentity']['PlayerCardID']}/wideart.png" if player["PlayerIdentity"].get("PlayerCardID") else None,
                                "agent": "Unknown",
                                "agentImgLink": "assets/Logo.png"
                            }

                            # bar()
                    seen.append(player["Subject"])
            if (title := game_state_dict.get(game_state)) is None:
                # program_exit(1)
                time.sleep(9)
            
            title_parts = [f"VALORANT status: {title}"]

            if cfg.get_feature_flag("server_id") and server != "":
                parts = server.split('.')
                if len(parts) > 2:
                    short_serverID = '.'.join(parts[2:])
                else:
                    short_serverID = server
                title_parts.append(f" {colr('- ' + short_serverID, fore=(200, 200, 200))}")
            
            table.set_title(''.join(title_parts))
            
            if title is not None:
                if cfg.get_feature_flag("auto_hide_leaderboard") and (
                    not is_leaderboard_needed
                ):
                    table.set_runtime_col_flag("Pos.", False)

                if game_state == "MENUS":
                    table.set_runtime_col_flag("Party", False)
                    table.set_runtime_col_flag("Agent", False)
                    table.set_runtime_col_flag(cfg.weapon.capitalize(), False)

                if game_state == "INGAME":
                    if isRange:
                        table.set_runtime_col_flag("Party", False)
                        table.set_runtime_col_flag("Agent", False)

                # We don't to show the RR column if the "aggregate_rank_rr" feature flag is True.
                table.set_runtime_col_flag(
                    "RR",
                    cfg.table.get("rr")
                    and not cfg.get_feature_flag("aggregate_rank_rr"),
                )

                table.set_caption(f"VALORANT rank yoinker v{version}")
                Server.send_payload("heartbeat", heartbeat_data)
                table.display()
                firstPrint = False

                # Print lobby rank details and estimated remaining time
                if game_state in ("INGAME", "PREGAME") and len(lobby_ranks) > 0:
                    avg_rank_val = round(sum(lobby_ranks) / len(lobby_ranks))
                    avg_rank_val = max(0, min(len(Ranks) - 1, avg_rank_val))
                    avg_rank_name = Ranks[avg_rank_val]
                    
                    min_rank_val = min(lobby_ranks)
                    max_rank_val = max(lobby_ranks)
                    min_rank_val = max(0, min(len(Ranks) - 1, min_rank_val))
                    max_rank_val = max(0, min(len(Ranks) - 1, max_rank_val))
                    
                    extra_info = [f"Lobby Avg Rank: {avg_rank_name} (Spread: {Ranks[min_rank_val]} - {Ranks[max_rank_val]})"]
                    
                    if game_state == "INGAME":
                        presence = presences.get_presence()
                        priv_presence = presences.get_private_presence(presence) or {}
                        
                        ally_score = priv_presence.get("partyOwnerMatchScoreAllyTeam")
                        enemy_score = priv_presence.get("partyOwnerMatchScoreEnemyTeam")
                        if ally_score is None and "partyPresenceData" in priv_presence:
                            party_data = priv_presence.get("partyPresenceData", {}) or {}
                            ally_score = party_data.get("partyOwnerMatchScoreAllyTeam")
                            enemy_score = party_data.get("partyOwnerMatchScoreEnemyTeam")
                            
                        queue_id = priv_presence.get("queueId")
                        if queue_id is None and "partyPresenceData" in priv_presence:
                            party_data = priv_presence.get("partyPresenceData", {}) or {}
                            queue_id = party_data.get("queueId")
                            
                        if ally_score is not None and enemy_score is not None:
                            est_time = get_estimated_remaining_time(queue_id, ally_score, enemy_score)
                            if est_time:
                                score_str = colr(f"{ally_score} - {enemy_score}", fore=(255, 255, 100))
                                est_time_str = colr(est_time, fore=(0, 255, 255))
                                extra_info.append(f"Score: {score_str} (Est. Time Left: {est_time_str})")
                                
                    print("\n" + " | ".join(extra_info))

                if cfg.get_feature_flag("last_played"):
                    if len(already_played_with) > 0:
                        print("\n--- Confrontation History ---")
                        for played in already_played_with:
                            print(
                                f"• {played['name']} (last {played['agent']}) {stats.convert_time(played['time_diff'])} ago. "
                                f"(Played WITH you: {played.get('with', 0)}x, AGAINST you: {played.get('against', 0)}x. "
                                f"Last match they were on {played.get('last_team', 'your')} team)"
                            )
                already_played_with = []
        if cfg.cooldown == 0:
            input("Press enter to fetch again...")
        else:
            # time.sleep(cfg.cooldown)
            pass
except KeyboardInterrupt:
    # lame implementation of fast ctrl+c exit
    os._exit(0)
except:
    log(traceback.format_exc())
    print(
        color(
            "The program has encountered an error. If the problem persists, please reach support"
            f" with the logs found in {os.getcwd()}\\logs",
            fore=(255, 0, 0),
        )
    )
    input("press enter to exit...\n")
    os._exit(1)