from colr import color
import requests

version = "1.255"
enablePrivateLogging = False
hide_names = False



sockets = {
    "skin": "bcef87d6-209b-46c6-8b19-fbe40bd95abc",
    "skin_level": "e7c63390-eda7-46e0-bb7a-a6abdacd2433",
    "skin_chroma": "3ad1b2b2-acdb-4524-852f-954a76ddae0a",
    "skin_buddy": "77258665-71d1-4623-bc72-44db9bd5b3b3",
    "skin_buddy_level": "dd3bf334-87f3-40bd-b043-682a57a8dc3a"
}



AGENTCOLORLIST = {
            "neon": (28, 69, 161),
            "none": (100, 100, 100),
            "viper": (48, 186, 135),
            "yoru": (52, 76, 207),
            "astra": (113, 42, 232),
            "breach": (217, 122, 46),
            "brimstone": (217, 122, 46),
            "cypher": (245, 240, 230),
            "jett": (154,222,255),
            "kay/o": (133, 146, 156),
            "killjoy": (255, 217, 31),
            "omen": (71, 80, 143),
            "phoenix": (254, 130, 102),
            "raze": (217, 122, 46),
            "reyna": (181, 101, 181),
            "sage": (90, 230, 213),
            "skye": (192, 230, 158),
            "sova": (37, 143, 204),
            "chamber": (200, 200, 200),
            "fade": (92, 92, 94)
        }


GAMEPODS = requests.get("https://valorant-api.com/internal/locres/en-US").json()["data"]["UI_GamePodStrings"]


symbol = "■"
PARTYICONLIST = [
            color(symbol, fore=(227, 67, 67)),
            color(symbol, fore=(216, 67, 227)),
            color(symbol, fore=(67, 70, 227)),
            color(symbol, fore=(67, 227, 208)),
            color(symbol, fore=(94, 227, 67)),
            color(symbol, fore=(226, 237, 57)),
            color(symbol, fore=(212, 82, 207)),
            symbol
        ]


NUMBERTORANKS = [
            color('Unrated', fore=(46, 46, 46)),
            color('Unrated', fore=(46, 46, 46)),
            color('Unrated', fore=(46, 46, 46)),
            color('Iron 1', fore=(72, 69, 62)),
            color('Iron 2', fore=(72, 69, 62)),
            color('Iron 3', fore=(72, 69, 62)),
            color('Bronze 1', fore=(187, 143, 90)),
            color('Bronze 2', fore=(187, 143, 90)),
            color('Bronze 3', fore=(187, 143, 90)),
            color('Silver 1', fore=(174, 178, 178)),
            color('Silver 2', fore=(174, 178, 178)),
            color('Silver 3', fore=(174, 178, 178)),
            color('Gold 1', fore=(197, 186, 63)),
            color('Gold 2', fore=(197, 186, 63)),
            color('Gold 3', fore=(197, 186, 63)),
            color('Platinum 1', fore=(24, 167, 185)),
            color('Platinum 2', fore=(24, 167, 185)),
            color('Platinum 3', fore=(24, 167, 185)),
            color('Diamond 1', fore=(216, 100, 199)),
            color('Diamond 2', fore=(216, 100, 199)),
            color('Diamond 3', fore=(216, 100, 199)),
            color('Immortal 1', fore=(221, 68, 68)),
            color('Immortal 2', fore=(221, 68, 68)),
            color('Immortal 3', fore=(221, 68, 68)),
            color('Radiant', fore=(255, 253, 205)),
        ]

tierDict = {
            "0cebb8be-46d7-c12a-d306-e9907bfc5a25": (0, 149, 135),
            "e046854e-406c-37f4-6607-19a9ba8426fc": (241, 184, 45),
            "60bca009-4182-7998-dee7-b8a2558dc369": (209, 84, 141),
            "12683d76-48d7-84a3-4e09-6985794f0445": (90, 159, 226),
            "411e4a55-4e59-7757-41f0-86a53f101bb5": (239, 235, 101),
            None: None
        }
