from InquirerPy.base.control import Choice
from src.constants import WEAPONS

TABLE_OPTS = {
    "skin": "Skin",
    "rr": "Ranked Rating",
    "leaderboard": "Leaderboard Position",
    "peakrank": "Peak Rank",
}

weapon_question = {
        "type": "fuzzy",
        "name": "weapon",
        "message": "Please select a weapon to show skin for:",
        "choices": WEAPONS,
    }

table_question = lambda config: {
        "type": "checkbox",
        "name": "table",
        "message": "Please select table columns to display:",
        "choices": [
            Choice(k, name=v, enabled=config.get("table",{}).get(k, True))
            for k, v in TABLE_OPTS.items()
        ],
        "filter": lambda table: {k: k in table for k in TABLE_OPTS.keys()},
        "long_instruction": "Press 'space' to toggle selection and 'enter' to submit"
    }

port_question = lambda config: {
        "type": "number",
        "name": "port",
        "message": "Please enter port for server to run:",
        "default": config.get("port", 1100),
        "min_allowed":0,
        "max_allowed": 65535,
        "filter": lambda ans: int(ans)
    }

cooldown_question = lambda config: {
        "type": "number",
        "name": "cooldown",
        "message": "Please enter cooldown time in seconds:",
        "default": config.get("cooldown", 10),
        "filter": lambda ans: int(ans)
    }

basic_questions = lambda config: [
    weapon_question,
    table_question(config=config)
]

advance_questions = lambda config: [
    port_question(config=config),
    cooldown_question(config=config),
] + basic_questions(config=config)