from typing import Literal, get_args

# from prettytable import PrettyTable
from rich.table import Table as RichTable
from rich.console import Console as RichConsole

TABLE_COLUMN_NAMES = Literal[
    "Party",
    "Agent",
    "Name",
    "Skin",
    "Rank",
    "RR",
    "Peak Rank",
    "Pos.",
    "HS",
    "WR",
    "KD",
    "Level"
]


class Table:
    def __init__(self, config, chatlog):
        self.rich_table = RichTable()
        self.col_flags = [
            True,  # Party
            True,  # Agent
            True,  # Name
            bool(config.table.get("skin", True)),  # Skin
            True,  # Rank
            bool(config.table.get("rr", True)),  # RR
            bool(config.table.get("peakrank", True)),  # Peak Rank
            bool(config.table.get("leaderboard", True)),  # Leaderboard Position
            bool(
                config.table.get("headshot_percent", True)
            ),  # hs need to be changed to be optional in future default true
            bool(
                config.table.get("winrate", True)
            ),  # wr need to be changed to be optional in future default true
            bool(config.table.get("kd", True)),  # KD
            True,  # Level
        ]
        self.runtime_col_flags = self.col_flags[:]  # making a copy
        self.field_names_candidates = list(get_args(TABLE_COLUMN_NAMES))
        self.field_names = [
            c for c, i in zip(self.field_names_candidates, self.col_flags) if i
        ]
        self.chatlog = chatlog
        self.console = RichConsole()

        self.rich_table.title_style = "bold"
        self.rich_table.caption_style = "italic rgb(5,5,5)"
        self.rich_table.caption = "VALORANT rank yoinker v2.5"
        self.rich_table.caption_justify = "left"


        overall_col_flags = [
            f1 & f2 for f1, f2 in zip(self.col_flags, self.runtime_col_flags)
        ]
        fields_to_display = [
            c for c, flag in zip(self.field_names_candidates, overall_col_flags) if flag
        ]

        for field in fields_to_display:
            self.rich_table.add_column(field, justify="center")

    def set_title(self, title):
        self.rich_table.title = self.ansi_to_console(title)

    def set_default_field_names(self):
        self.rich_table.field_names = self.field_names[:]

    def set_field_names(self, field_names):
        self.rich_table.field_names = field_names

    def add_row_table(self, args: list):
        row = [c for c, i in zip(args, self.col_flags) if i]
        row = [self.ansi_to_console(str(i)) for i in row]
        
        self.rich_table.add_row(*row)

    def add_empty_row(self):
        empty_row = [""] * sum(self.col_flags)
        self.rich_table.add_row(*empty_row)

    def reset_runtime_col_flags(self):
        self.runtime_col_flags = self.col_flags[:]

    def set_runtime_col_flag(self, field_name: TABLE_COLUMN_NAMES, flag: bool):
        index = self.field_names_candidates.index(field_name)
        self.runtime_col_flags[index] = flag

    def display(self):
        # overall_col_flags = [
        #     f1 & f2 for f1, f2 in zip(self.col_flags, self.runtime_col_flags)
        # ]
        # fields_to_display = [
        #     c for c, flag in zip(self.field_names_candidates, overall_col_flags) if flag
        # ]

        # all_fields = [c for c, flag in zip(self.field_names_candidates, overall_col_flags)]
        
        # extracting specific columns at runtime can sometimes lead to very minor padding issues
        # this can be problematic for OCD people, others might not notice
        # print(self.pretty_table.get_string(fields=fields_to_display))
        # RichConsole.print(self.pretty_table.get_string(fields=fields_to_display))
        # self.chatlog(self.pretty_table.get_string(fields=fields_to_display))
        self.console.print(self.rich_table)

    def clear(self):
        # self.pretty_table.clear()
        pass

    def ansi_to_console(self, line):
        string_to_return = ""
        strings = line.split("\x1b[38;2;")
        del strings[0]
        for string in strings:
            splits = string.split("m", 1)
            rgb = [int(i) for i in splits[0].split(";")]
            original_strings = splits[1].split("\x1b[0m")
            string_to_return += f"[rgb({rgb[0]},{rgb[1]},{rgb[2]})]{'[/]'.join(original_strings)}"
        return string_to_return
