from colr import color

class Colors:
    def __init__(self, colored:bool) -> None:
        self.colorsEnabled = colored
        self.partyIcon = "■"
        self.rankColors = [
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
            color('Radiant', fore=(255, 253, 205))
        ]
        self.ranks = [
            'Unrated', 
            'Unrated', 
            'Unrated', 
            'Iron 1',
            'Iron 2',
            'Iron 3',
            'Bronze 1',
            'Bronze 2',
            'Bronze 3',
            'Silver 1',
            'Silver 2',
            'Silver 3',
            'Gold 1',
            'Gold 2',
            'Gold 3',
            'Platinum 1',
            'Platinum 2',
            'Platinum 3',
            'Diamond 1',
            'Diamond 2',
            'Diamond 3',
            'Immortal 1',
            'Immortal 2',
            'Immortal 3',
            'Radiant', 
        ]
        self.partyIcons = [
            color(self.partyIcon, fore=(227, 67, 67)),
            color(self.partyIcon, fore=(216, 67, 227)),
            color(self.partyIcon, fore=(67, 70, 227)),
            color(self.partyIcon, fore=(67, 227, 208)),
            color(self.partyIcon, fore=(94, 227, 67)),
            color(self.partyIcon, fore=(226, 237, 57)),
            color(self.partyIcon, fore=(212, 82, 207)),
            self.partyIcon
        ]
    
    def level_to_color(self, level):
        if not self.colorsEnabled: return level
        
        foreColor = (0,0,0)
        if level >= 400: foreColor=(0, 255, 255)
        elif level >= 300: foreColor=(255, 255, 0)
        elif level >= 200: foreColor=(0, 0, 255)
        elif level >= 100: foreColor=(241, 144, 54)
        elif level < 100: foreColor=(211, 211, 211)
        return color(level, fore=foreColor)

    def getTeamColor(self, TeamID:str, IGN:str, puuid:str, selfPuuid:str):
        if not self.colorsEnabled: return IGN
        if puuid == selfPuuid: return color(IGN, fore=(221, 224, 41))

        if TeamID == "Red": teamColor = color(IGN, fore=(238, 77, 77))
        elif TeamID == "Blue": teamColor = color(IGN, fore=(76, 151, 237))
        else: teamColor = ""
        return teamColor