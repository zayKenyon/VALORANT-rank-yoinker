from prettytable import PrettyTable


class Table:
    def __init__(self,config):
        self.pretty_table = PrettyTable()
        self.row_flags = [
            True,  # Party
            True,  # Agent
            True,  # Name
            bool(config.table.get("skin", True)),  # Skin
            True,  # Rank
            bool(config.table.get("rr", True)),  # RR
            bool(config.table.get("peakrank", True)),  # Peak Rank
            bool(config.table.get("leaderboard", True)),  # Leaderboard Position
            True,  # Level
        ]
        self.field_names_candidates = [
            "Party",
            "Agent",
            "Name",
            "Skin",
            "Rank",
            "RR",
            "Peak Rank",
            "Pos.",
            "Level",
        ]
        self.field_names = [
            c for c, i in zip(self.field_names_candidates, self.row_flags) if i
        ]

    def set_title(self, title):
        self.pretty_table.title = title

    def set_default_field_names(self):
        self.pretty_table.field_names = self.field_names

    def set_field_names(self, field_names):
        self.pretty_table.field_names = field_names

    def add_row_table(self, args: list):
        row = [c for c, i in zip(args, self.row_flags) if i]
        self.pretty_table.add_rows([row])

    def add_empty_row(self):
        empty_row = [""] * sum(self.row_flags)
        self.pretty_table.add_rows([empty_row])

    def display(self):
        print(self.pretty_table)

    def clear(self):
        self.pretty_table.clear()