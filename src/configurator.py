import json
import os

from InquirerPy import inquirer, prompt
from InquirerPy.separator import Separator

from src.constants import DEFAULT_CONFIG

from src.questions import *


def configure():
    default_config = DEFAULT_CONFIG

    try:
        with open("config.json", "r") as openfile:
            user_config = default_config | json.load(openfile)
    except FileNotFoundError:
        print("Generating default configuration")
        user_config = default_config
    except json.JSONDecodeError: 
        print("config file maybe broken, using default instead")
        user_config = default_config

    menu_choices = [
        "Weapon Selection",
        "Table Customization",
        "Optional Feature Flags",
        Separator(),
        "Full Basic Config (Suitable for most users)",
        "Full Advance Config (I know what i am doing!)",
        Separator(),
        "Save and Exit Configurator",
        "Exit Configurator"
    ]

    changed_config = {}
    while True:
        loop_config = user_config | changed_config

        choice = inquirer.select(
            message="Please select an option:",
            choices=menu_choices,
            default=menu_choices[0],
        ).execute()

        if choice is menu_choices[0]:
            changed_config |= prompt([weapon_question(config=loop_config)])
        elif choice is menu_choices[1]:
            changed_config |= prompt([table_question(config=loop_config)])
        elif choice is menu_choices[2]:
            changed_config |= prompt([flags_question(config=loop_config)])
        elif choice is menu_choices[4]:
            changed_config |= prompt(basic_questions(config=loop_config))
        elif choice is menu_choices[5]:
            changed_config |= prompt(advance_questions(config=loop_config))
        elif choice is menu_choices[7]:
            proceed=True
            break
        else:
            proceed = (not len(changed_config.keys()) > 0) or inquirer.confirm(
                message="Do you want to save new config?", default=True
            ).execute()
            break

        os.system('cls')

    if proceed:
        config = default_config | user_config | changed_config
        with open("config.json", "w") as outfile:
            json.dump(config, outfile, indent=4)
    else:
        config = default_config | user_config

    return config
