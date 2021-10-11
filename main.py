def main(config:dict, locale:dict):
    Proc(config, locale).init()

if __name__ == "__main__":
    from src.Process import Proc
    from src.Utils import Utils as UtilsObj
    import json
    import glob
    from ctypes import windll
    import os
    import requests

    if not os.path.exists(R"locales"):
        UtilsObj.copyLocales()

    #CONFIG KEYS
    configKeys = ["colors", "respectPrivacy", "sortingMethod", "locale"]
    try:
        with open("config.json", "r") as configFile:
            parsedConfig = json.load(configFile)
            for key in configKeys:
                if key not in parsedConfig:
                    print("Configuration file is outdated!")
                    raise FileNotFoundError

        with open(f"./locales/{parsedConfig['locale']}.json", "r", encoding='utf-8') as localeFile: locale = json.load(localeFile)
        main(parsedConfig, locale)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        if not windll.shell32.IsUserAnAdmin():
            from elevate import elevate
            elevate()
        UtilsObj.createConfig()

        with open("config.json", "r") as configFile: parsedConfig = json.load(configFile)
        with open(f"./locales/{parsedConfig['locale']}.json", "r", encoding='utf-8') as localeFile: locale = json.load(localeFile)
        main(parsedConfig, locale)
