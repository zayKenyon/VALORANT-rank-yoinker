from InquirerPy.base.control import Choice
from src.constants import WEAPONS

TABLE_OPTS = {
    "skin": "Skin",
    "rr": "Ranked Rating",
    "leaderboard": "Leaderboard Position",
    "peakrank": "Peak Rank",
}

basic_questions = lambda config: [
    {
        "type": "fuzzy",
        "name": "weapon",
        "message": "Please select a weapon to show skin for:",
        "choices": WEAPONS,
    },
    {
        "type": "checkbox",
        "name": "table",
        "message": "Please select table columns to display:",
        "choices": [
            Choice(k, name=v, enabled=config.get("table").get(k, True))
            for k, v in TABLE_OPTS.items()
        ],
        "filter": lambda table: {k: k in table for k in TABLE_OPTS.keys()},
    },
]
