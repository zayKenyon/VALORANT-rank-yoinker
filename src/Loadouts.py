import time
import requests
from colr import color
from src.constants import sockets, hide_names
import json


class Loadouts:
    def __init__(self, Requests, log, colors, Server, current_map):
        self.Requests = Requests
        self.log = log
        self.colors = colors
        self.Server = Server
        self.current_map = current_map

    def get_match_loadouts(self, match_id, players, weaponChoose, valoApiSkins, names, state="game"):
        playersBackup = players
        weaponLists = {}
        valApiWeapons = requests.get("https://valorant-api.com/v1/weapons").json()
        PlayerInventorys = self.Requests.fetch("glz", f"/core-game/v1/matches/{match_id}/loadouts", "get")
        for idx, player in enumerate(players):
            inv = PlayerInventorys["Loadouts"][idx]["Loadout"]
            weaponLists[player["Subject"]] = {}

            # console skin color
            for weapon in valApiWeapons["data"]:
                if weapon["displayName"].lower() not in [weapon.lower() for weapon in weaponChoose]:
                    continue
                weaponLists[player["Subject"]][weapon["displayName"]] = {}
                skin_id = inv["Items"][weapon["uuid"].lower()]["Sockets"]["bcef87d6-209b-46c6-8b19-fbe40bd95abc"]["Item"]["ID"]
                for skin in valoApiSkins.json()["data"]:
                    if skin_id.lower() != skin["uuid"].lower():
                        continue
                    skin_rgb_color = self.colors.get_rgb_color_from_skin(skin["uuid"].lower(), valoApiSkins)
                    weaponLists[player["Subject"]][weapon["displayName"]]["color"] = skin_rgb_color
                    break

        final_json = self.convertLoadoutToJsonArray(PlayerInventorys, playersBackup, state, names)
        # self.Server.send_message(json.dumps(final_json))

        for player_id in final_json["Players"]:
            player_weapons = final_json["Players"][player_id]["Weapons"]
            for weapon_id in player_weapons:
                weapon = player_weapons[weapon_id]["weapon"]
                if weapon not in weaponChoose:
                    continue

                skin_name = " ".join(player_weapons[weapon_id]["skinDisplayName"].split(" ")[0:-1])
                skin_image = player_weapons[weapon_id]["skinDisplayIcon"]
                skin_buddy = player_weapons[weapon_id]["buddy_displayIcon"] if "buddy_displayIcon" in player_weapons[weapon_id] else None

                weaponLists[player_id][weapon]["name"] = skin_name
                weaponLists[player_id][weapon]["image"] = skin_image
                weaponLists[player_id][weapon]["buddy"] = skin_buddy

        print(weaponLists)
        return weaponLists

    # this will convert valorant loadouts to json with player names
    def convertLoadoutToJsonArray(self, PlayerInventorys, players, state, names):
        # get agent dict from main in future
        # names = self.namesClass.get_names_from_puuids(players)
        valoApiSprays = requests.get("https://valorant-api.com/v1/sprays")
        valoApiWeapons = requests.get("https://valorant-api.com/v1/weapons")
        valoApiBuddies = requests.get("https://valorant-api.com/v1/buddies")
        valoApiAgents = requests.get("https://valorant-api.com/v1/agents")
        valoApiTitles = requests.get("https://valorant-api.com/v1/playertitles")
        valoApiPlayerCards = requests.get("https://valorant-api.com/v1/playercards")

        final_final_json = {"Players": {},
                            "time": int(time.time()),
                            "map": self.current_map}

        final_json = final_final_json["Players"]
        if state == "game":
            PlayerInventorys = PlayerInventorys["Loadouts"]
            for i in range(len(PlayerInventorys)):
                PlayerInventory = PlayerInventorys[i]["Loadout"]
                final_json.update(
                    {
                        players[i]["Subject"]: {}
                    }
                )

                # creates name field
                if hide_names:
                    for agent in valoApiAgents.json()["data"]:
                        if agent["uuid"] == players[i]["CharacterID"]:
                            final_json[players[i]["Subject"]].update({"Name": agent["displayName"]})
                else:
                    final_json[players[i]["Subject"]].update({"Name": names[players[i]["Subject"]]})

                # creates team field
                final_json[players[i]["Subject"]].update({"Team": players[i]["TeamID"]})

                # create spray field
                final_json[players[i]["Subject"]].update({"Sprays": {}})
                # append sprays to field

                final_json[players[i]["Subject"]].update({"Level": players[i]["PlayerIdentity"]["AccountLevel"]})

                for title in valoApiTitles.json()["data"]:
                    if title["uuid"] == players[i]["PlayerIdentity"]["PlayerTitleID"]:
                        final_json[players[i]["Subject"]].update({"Title": title["titleText"]})

                for PCard in valoApiPlayerCards.json()["data"]:
                    if PCard["uuid"] == players[i]["PlayerIdentity"]["PlayerCardID"]:
                        final_json[players[i]["Subject"]].update({"PlayerCard": PCard["largeArt"]})

                for agent in valoApiAgents.json()["data"]:
                    if agent["uuid"] == players[i]["CharacterID"]:
                        final_json[players[i]["Subject"]].update({"AgentArtworkName": agent["displayName"] + "Artwork"})
                        final_json[players[i]["Subject"]].update({"Agent": agent["displayIcon"]})

                for j in range(len(PlayerInventory["Sprays"]["SpraySelections"])):
                    spray = PlayerInventory["Sprays"]["SpraySelections"][j]
                    final_json[players[i]["Subject"]]["Sprays"].update({j: {}})
                    for sprayValApi in valoApiSprays.json()["data"]:
                        if spray["SprayID"] == sprayValApi["uuid"]:
                            final_json[players[i]["Subject"]]["Sprays"][j].update({
                                "displayName": sprayValApi["displayName"],
                                "displayIcon": sprayValApi["displayIcon"],
                                "fullTransparentIcon": sprayValApi["fullTransparentIcon"]
                            })

                # create weapons field
                final_json[players[i]["Subject"]].update({"Weapons": {}})

                for skin in PlayerInventory["Items"]:

                    # create skin field
                    final_json[players[i]["Subject"]]["Weapons"].update({skin: {}})

                    for socket in PlayerInventory["Items"][skin]["Sockets"]:
                        # predefined sockets
                        for var_socket in sockets:
                            if socket == sockets[var_socket]:
                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                    {
                                        var_socket: PlayerInventory["Items"][skin]["Sockets"][socket]["Item"]["ID"]
                                    }
                                )

                    # buddies
                    for socket in PlayerInventory["Items"][skin]["Sockets"]:
                        if sockets["skin_buddy"] == socket:
                            for buddy in valoApiBuddies.json()["data"]:
                                if buddy["uuid"] == PlayerInventory["Items"][skin]["Sockets"][socket]["Item"]["ID"]:
                                    final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                        {
                                            "buddy_displayIcon": buddy["displayIcon"]
                                        }
                                    )

                    # append names to field
                    for weapon in valoApiWeapons.json()["data"]:
                        if skin == weapon["uuid"]:
                            final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                {
                                    "weapon": weapon["displayName"]
                                }
                            )
                            for skinValApi in weapon["skins"]:
                                if skinValApi["uuid"] == PlayerInventory["Items"][skin]["Sockets"][sockets["skin"]]["Item"]["ID"]:
                                    final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                        {
                                            "skinDisplayName": skinValApi["displayName"]
                                        }
                                    )
                                    for chroma in skinValApi["chromas"]:
                                        if chroma["uuid"] == PlayerInventory["Items"][skin]["Sockets"][sockets["skin_chroma"]]["Item"]["ID"]:
                                            if chroma["displayIcon"] != None:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": chroma["displayIcon"]
                                                    }
                                                )
                                            elif chroma["fullRender"] != None:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": chroma["fullRender"]
                                                    }
                                                )
                                            elif skinValApi["displayIcon"] != None:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": skinValApi["displayIcon"]
                                                    }
                                                )
                                            else:
                                                final_json[players[i]["Subject"]]["Weapons"][skin].update(
                                                    {
                                                        "skinDisplayIcon": skinValApi["levels"][0]["displayIcon"]
                                                    }
                                                )
                                    if skinValApi["displayName"].startswith("Standard") or skinValApi["displayName"].startswith("Melee"):
                                        final_json[players[i]["Subject"]]["Weapons"][skin]["skinDisplayIcon"] = weapon["displayIcon"]

        return final_final_json
