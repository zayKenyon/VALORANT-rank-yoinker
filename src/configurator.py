import json

from InquirerPy import inquirer, prompt

from src.questions.advance import advance_questions
from src.questions.basic import basic_questions


def configure():
    default_config = {
        "cooldown": 10,
        "weapon": "Vandal",
        "port": 1100,
        "table": {
            "skin": True,
            "rr": True,
            "peakrank": True,
            "leaderboard": True,
        },
    }

    try:
        with open("config.json", "r") as openfile:
            user_config = json.load(openfile)
    except FileNotFoundError:
        print("Generating default configuration")
        user_config = default_config
    except json.JSONDecodeError: 
        print("config file maybe broken, using default instead")
        user_config = default_config

    menu_choices = [
        "Basic Config (Suitable for most users)",
        "Advance Config (I know what i am doing!)",
    ]

    choice = inquirer.select(
        message="Please select type of configuration:",
        choices=menu_choices,
        default=menu_choices[0],
    ).execute()

    if choice is menu_choices[0]:
        changed_config = prompt(basic_questions(config=user_config))
    else:
        changed_config = prompt(advance_questions(config=user_config))

    proceed = inquirer.confirm(
        message="Do you want to apply new config?", default=True
    ).execute()

    if proceed:
        config = default_config | user_config | changed_config
        with open("config.json", "w") as outfile:
            json.dump(config, outfile, indent=4)
    else:
        config = default_config | user_config

    return config
