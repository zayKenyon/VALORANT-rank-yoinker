def main(config:dict, locale:dict):
    Proc(config, locale).init()

def createConfig():
    print("Please remember that you can always change these values in \"config.json\" under the same folder.\n")
    defaultConfig = {"colors":False,
                            "respectPrivacy":True,
                            "sortingMethod":"DESC_LEVEL",
                            "locale":"en-US"}

    locales = []
    casedLocales = []
    localeFiles = glob.glob("./locales/*.json")          
    for k,localeCode in enumerate(localeFiles):
        localeName = localeCode.replace("./locales\\", "").replace("./locales/", "").split(".")[0]
        locales.append(localeName)
        casedLocales.append(localeName.upper())
    
    chosenLocale = None

    while chosenLocale == None:
        for k,v in enumerate(locales):
            print("["+str(k+1)+"] "+v)
        locale = input(f"Choose your locale. (Number only) : ")
        try:
            locale = locales[int(locale)-1]
        except:
            continue
        
        if locale.upper() in casedLocales:
            with open(f"./locales/{locale}.json", "r", encoding='utf-8') as localeFile:
                chosenLocale = json.load(localeFile)
                break
        else: print(f"Please choose one in the following: {locales}")

    sortingMethodArr = [chosenLocale["sorting_rank_ascending"],
    chosenLocale["sorting_rank_descending"],
    chosenLocale["sorting_level_ascending"],
    chosenLocale["sorting_level_descending"]]
    sortingMethod = None

    colors = input(chosenLocale["question_colors"])
    showNames = input(chosenLocale["question_names"])

    while sortingMethod == None:
        for k,v in enumerate(sortingMethodArr):
            print("["+str(k+1)+"] "+v)
        sortingMethod = input(chosenLocale["question_sorting_method"]+" : ")
        try:
            sortingMethod = sortingMethodArr[int(sortingMethod)-1]
        except:
            sortingMethod = None
            continue
    if colors[0].upper() == chosenLocale["yes_uppercase"]: defaultConfig["colors"] = True
    if showNames[0].upper() == chosenLocale["yes_uppercase"]: defaultConfig["respectPrivacy"] = False
    if sortingMethod.upper() == chosenLocale["sorting_rank_ascending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_rank_ascending"].upper()
    elif sortingMethod.upper() == chosenLocale["sorting_level_ascending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_level_ascending"].upper()
    elif sortingMethod.upper() == chosenLocale["sorting_rank_descending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_rank_descending"].upper()
    elif sortingMethod.upper() == chosenLocale["sorting_level_descending"].upper(): defaultConfig["sortingMethod"] = chosenLocale["sorting_level_descending"].upper()
    else:
        print(chosenLocale["err_invalid_input"])
        input(chosenLocale["exit"])
        exit()

    with open("config.json", "w") as configFile:
        json.dump(defaultConfig, configFile)

if __name__ == "__main__":
    from src.Process import Proc
    import json
    import glob
    from ctypes import windll
    
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
        createConfig()

        with open("config.json", "r") as configFile: parsedConfig = json.load(configFile)
        with open(f"./locales/{parsedConfig['locale']}.json", "r", encoding='utf-8') as localeFile: locale = json.load(localeFile)
        main(parsedConfig, locale)
