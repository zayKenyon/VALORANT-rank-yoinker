def main(config:dict):
    Proc(config).init()

if __name__ == "__main__":
    from src.Process import Proc
    import json
    
    try:
        with open("config.json", "r") as configFile:
            parsedConfig = json.load(configFile)
            if "colors" in parsedConfig and "respectPrivacy" in parsedConfig and "sortingMethod" in parsedConfig:
                main(parsedConfig)
            else:
                print("Configuration file is outdated!")
                raise FileNotFoundError
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        print("Please remember that you can always change these values in \"config.json\" under the same folder.\n")
        
        defaultConfig = {"colors":False,
                            "respectPrivacy":True,
                            "sortingMethod":"LEVEL"}
        colors = input("Do you love colors? Y/n: ")
        showNames = input("Do you want to respect other player's privacy? Y/n: ")
        sortingMethod = input("What sorting method you would like to use? ASC_LEVEL, DESC_LEVEL, ASC_RANK, DESC_RANK: ")

        if colors.upper() == "Y": defaultConfig["colors"] = True
        if showNames.upper() == "N": defaultConfig["respectPrivacy"] = False
        if sortingMethod.upper() == "ASC_RANK": defaultConfig["sortingMethod"] = "ASC_RANK"
        elif sortingMethod.upper() == "ASC_LEVEL": defaultConfig["sortingMethod"] = "ASC_LEVEL"
        elif sortingMethod.upper() == "DESC_RANK": defaultConfig["sortingMethod"] = "DESC_RANK"
        elif sortingMethod.upper() == "DESC_LEVEL": defaultConfig["sortingMethod"] = "DESC_LEVEL"
        else: print("Invalid input. exiting...")

        with open("config.json", "w") as configFile:
            json.dump(defaultConfig, configFile)

        with open("config.json", "r") as configFile:
            parsedConfig = json.load(configFile)
            main(parsedConfig)