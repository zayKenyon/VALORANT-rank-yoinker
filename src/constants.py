import requests
from colr import color

version = "2.60"
enablePrivateLogging = True
hide_names = True
hide_levels = True

gamemodes = {
    "newmap": "New Map",
    "competitive": "Competitive",
    "unrated": "Unrated",
    "swiftplay": "Swiftplay",
    "spikerush": "Spike Rush",
    "deathmatch": "Deathmatch",
    "ggteam": "Escalation",
    "onefa": "Replication",
    "hurm": "Team Deathmatch",
    "custom": "Custom",
    "snowball": "Snowball Fight",
    "": "Custom",
}

before_ascendant_seasons = [
    "0df5adb9-4dcb-6899-1306-3e9860661dd3",
    "3f61c772-4560-cd3f-5d3f-a7ab5abda6b3",
    "0530b9c4-4980-f2ee-df5d-09864cd00542",
    "46ea6166-4573-1128-9cea-60a15640059b",
    "fcf2c8f4-4324-e50b-2e23-718e4a3ab046",
    "97b6e739-44cc-ffa7-49ad-398ba502ceb0",
    "ab57ef51-4e59-da91-cc8d-51a5a2b9b8ff",
    "52e9749a-429b-7060-99fe-4595426a0cf7",
    "71c81c67-4fae-ceb1-844c-aab2bb8710fa",
    "2a27e5d2-4d30-c9e2-b15a-93b8909a442c",
    "4cb622e1-4244-6da3-7276-8daaf1c01be2",
    "a16955a5-4ad0-f761-5e9e-389df1c892fb",
    "97b39124-46ce-8b55-8fd1-7cbf7ffe173f",
    "573f53ac-41a5-3a7d-d9ce-d6a6298e5704",
    "d929bc38-4ab6-7da4-94f0-ee84f8ac141e",
    "3e47230a-463c-a301-eb7d-67bb60357d4f",
    "808202d6-4f2b-a8ff-1feb-b3a0590ad79f",
]
sockets = {
    "skin": "bcef87d6-209b-46c6-8b19-fbe40bd95abc",
    "skin_level": "e7c63390-eda7-46e0-bb7a-a6abdacd2433",
    "skin_chroma": "3ad1b2b2-acdb-4524-852f-954a76ddae0a",
    "skin_buddy": "77258665-71d1-4623-bc72-44db9bd5b3b3",
    "skin_buddy_level": "dd3bf334-87f3-40bd-b043-682a57a8dc3a"
}



AGENTCOLORLIST = {
    "none": (100, 100, 100),
    "astra": (113, 42, 232),
    "breach": (217, 122, 46),
    "brimstone": (217, 122, 46),
    "cypher": (245, 240, 230),
    "chamber": (200, 200, 200),
    "deadlock": (102, 119, 176),
    "fade": (92, 92, 94),
    "jett": (154, 222, 255),
    "kay/o": (133, 146, 156),
    "killjoy": (255, 217, 31),
    "omen": (71, 80, 143),
    "phoenix": (254, 130, 102),
    "raze": (217, 122, 46),
    "reyna": (181, 101, 181),
    "sage": (90, 230, 213),
    "skye": (192, 230, 158),
    "sova": (37, 143, 204),
    "neon": (28, 69, 161),
    "viper": (48, 186, 135),
    "yoru": (52, 76, 207),
}


GAMEPODS = requests.get("https://valorant-api.com/internal/locres/en-US").json()["data"]["UI_GamePodStrings"]

symbol = "■"
PARTYICONLIST = [
    (symbol, (227, 67, 67)),
    (symbol, (216, 67, 227)),
    (symbol, (67, 70, 227)),
    (symbol, (67, 227, 208)),
    (symbol, (94, 227, 67)),
    (symbol, (226, 237, 57)),
    (symbol, (212, 82, 207)),
    (symbol, (255, 255, 255)),
]

GAMESATEDICT = {
    "INGAME": ('In-Game', (241, 39, 39)),
    "PREGAME": ('Agent Select', (103, 237, 76)),
    "MENUS": ('In-Menus', (238, 241, 54)),
}

NUMBERTORANKS = [
    ('Unranked', (46, 46, 46)),
    ('Unranked', (46, 46, 46)),
    ('Unranked', (46, 46, 46)),
    ('Iron 1', (72, 69, 62)),
    ('Iron 2', (72, 69, 62)),
    ('Iron 3', (72, 69, 62)),
    ('Bronze 1', (187, 143, 90)),
    ('Bronze 2', (187, 143, 90)),
    ('Bronze 3', (187, 143, 90)),
    ('Silver 1', (174, 178, 178)),
    ('Silver 2', (174, 178, 178)),
    ('Silver 3', (174, 178, 178)),
    ('Gold 1', (197, 186, 63)),
    ('Gold 2', (197, 186, 63)),
    ('Gold 3', (197, 186, 63)),
    ('Platinum 1', (24, 167, 185)),
    ('Platinum 2', (24, 167, 185)),
    ('Platinum 3', (24, 167, 185)),
    ('Diamond 1', (216, 100, 199)),
    ('Diamond 2', (216, 100, 199)),
    ('Diamond 3', (216, 100, 199)),
    ('Ascendant 1', (24, 148, 82)),
    ('Ascendant 2', (24, 148, 82)),
    ('Ascendant 3', (24, 148, 82)),
    ('Immortal 1', (221, 68, 68)),
    ('Immortal 2', (221, 68, 68)),
    ('Immortal 3', (221, 68, 68)),
    ('Radiant', (255, 253, 205)),
]

tierDict = {
    "0cebb8be-46d7-c12a-d306-e9907bfc5a25": (0, 149, 135),
    "e046854e-406c-37f4-6607-19a9ba8426fc": (241, 184, 45),
    "60bca009-4182-7998-dee7-b8a2558dc369": (209, 84, 141),
    "12683d76-48d7-84a3-4e09-6985794f0445": (90, 159, 226),
    "411e4a55-4e59-7757-41f0-86a53f101bb5": (239, 235, 101),
    None: None
}

WEAPONS = [
    "Classic",
    "Shorty",
    "Frenzy",
    "Ghost",
    "Sheriff",
    "Stinger",
    "Spectre",
    "Bucky",
    "Judge",
    "Bulldog",
    "Guardian",
    "Phantom",
    "Vandal",
    "Marshal",
    "Operator",
    "Ares",
    "Odin",
    "Melee",
]

DEFAULT_CONFIG = {
    "gui": True,
    "cooldown": 10,
    "port": 1100,
    "weapon": "Vandal, Phantom",
    "weapon_amount": 2,
    "chat_limit": 5,
    "calculation_range": 1,
    "table": {
        "party": True,
        "agent": True,
        "top_agent": False,
        "top_agent_map": False,
        "top_role": False,
        "name": True,
        "skin": True,
        "rank": True,
        "rr": True,
        "peakrank": True,
        "previousrank" : False,
        "leaderboard": True,
        "headshot_percent": True,
        "winrate": True,
        "kd": False,
        "level": True
    },
    "flags": {
        "last_played": True,
        "auto_hide_leaderboard": True,
        "pre_cls": False,
        "game_chat": True,
        "peak_rank_act": True,
        "discord_rpc": True,
        "aggregate_rank_rr": True
    }
}
