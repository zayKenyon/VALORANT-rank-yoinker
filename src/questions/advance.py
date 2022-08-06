from src.questions.basic import basic_questions

advance_questions = lambda config: [
    {
        "type": "number",
        "name": "port",
        "message": "Please enter port for server to run:",
        "default": config.get("port", 1100),
        "min_allowed":0,
        "max_allowed": 65535,
        "filter": lambda ans: int(ans)
    },
    {
        "type": "number",
        "name": "cooldown",
        "message": "Please enter cooldown time in seconds:",
        "default": config.get("cooldown", 10),
        "filter": lambda ans: int(ans)
    },
] + basic_questions(config=config)
