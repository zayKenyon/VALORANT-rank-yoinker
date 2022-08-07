import json

from InquirerPy import inquirer, prompt
from src.constants import DEFAULT_CONFIG

from src.questions import basic_questions, advance_questions, flags_question 


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
        "Basic Config (Suitable for most users)",
        "Advance Config (I know what i am doing!)",
        "Optional Feature Flags"
    ]

    choice = inquirer.select(
        message="Please select type of configuration:",
        choices=menu_choices,
        default=menu_choices[0],
    ).execute()

    if choice is menu_choices[0]:
        changed_config = prompt(basic_questions(config=user_config))
    elif choice is menu_choices[2]:
        changed_config = prompt([flags_question(config=user_config)])
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
