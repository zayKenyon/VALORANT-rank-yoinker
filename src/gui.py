from PIL import Image, ImageTk
import ttkbootstrap as ttk
from io import BytesIO
import tkinter as tk
import requests

import urllib.parse
import webbrowser

from src.constants import *

def on_label_click(event):
    label_text = labels[event.widget.row][event.widget.column]['text']
    webbrowser.open_new_tab(f"https://tracker.gg/valorant/profile/riot/{urllib.parse.quote(label_text)}/overview")

class LabelGrid(tk.Frame):
    """
    Creates a grid of labels that have their cells populated by content.
    """

    def __init__(self, master, content=([0, 0], [0, 0]), *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.content = content
        self.content_size = (len(content), len(content[0]))
        self._create_labels()
        self._display_labels()

    def _create_labels(self):
        def __put_content_in_label(row, column):
            content = self.content[row][column]
            if row == 0:
                label = tk.Label(self, font=("Segoe UI", 12, "bold", "underline"), pady=3, padx=5, anchor="center")
            else:
                label = tk.Label(self, font=("Segoe UI", 12), pady=3, padx=5, anchor="center")
            label.row = row  # Store the row information as an attribute
            label.column = column  # Store the column information as an attribute

            if type(content).__name__ == "tuple":
                content, clr = content
                label['foreground'] = clr
            if column == 1 and row != 0:
                label['text'] = content
                label.bind("<Button-1>", on_label_click)
            content_type = type(content).__name__
            if content_type in ('str', 'int'):
                label['text'] = content
            elif content_type == 'PhotoImage':
                label['image'] = content

            labels[row].append(label)  # Append the label to the appropriate row list

        global labels
        labels = []
        for i in range(self.content_size[0]):
            labels.append([])
            for j in range(self.content_size[1]):
                __put_content_in_label(i, j)

    def _display_labels(self):
        for i in range(self.content_size[0]):
            for j in range(self.content_size[1]):
                labels[i][j].grid(row=i, column=j)

class GUI:
    def __init__(self):
        self.frame = tk.Tk()
        self.frame.title(f"VALORANT rank yoinker v{version}")

        self.screen_width = self.frame.winfo_screenwidth()
        self.screen_height = self.frame.winfo_screenheight()

        self.frame.geometry(f"{int(self.screen_width // 1.75)}x{int(self.screen_height // 1.7)}")

        self.frame.iconbitmap("../assets/Logo.ico")
        self.style = ttk.Style(theme="darkly")

        self.tab_frame = ttk.Frame(self.frame, padding=5)
        self.create_tabs()
        self.tab_frame.grid(row=0, column=0)

        self.live_game_frame = ttk.Frame(self.frame, padding=5, relief="solid", borderwidth=1)
        self.game_info_frame = ttk.Frame(self.live_game_frame)
        self.game_time_label = ttk.Label(self.game_info_frame, text="00:00", font=("Segoe UI", 12))
        self.game_map_label = ttk.Label(self.game_info_frame, text="Ascent", font=("Segoe UI", 12))
        self.game_mode_label = ttk.Label(self.game_info_frame, text="Unrated", font=("Segoe UI", 12))
        self.game_state_label = ttk.Label(self.game_info_frame, text="In Game", font=("Segoe UI", 12))
        self.player_table = LabelGrid(self.live_game_frame)
        self.create_live_game_frame()
        self.live_game_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def create_tabs(self):
        self.live_game_tab = ttk.Button(self.tab_frame,
                                        text="Agents",
                                        command=self.show_live_game_frame,
                                        takefocus=False)
        self.live_skins_tab = ttk.Button(self.tab_frame,
                                         text="Skins",
                                         takefocus=False)
        self.settings_tab = ttk.Button(self.tab_frame,
                                       text="Settings",
                                       takefocus=False)

        self.live_game_tab.grid(row=0, column=0)
        self.live_skins_tab.grid(row=0, column=1)
        self.settings_tab.grid(row=0, column=2)

    def create_live_game_frame(self):
        self.ally_team_average_frame = ttk.Frame(self.live_game_frame, padding=3)
        self.enemy_team_average_frame = ttk.Frame(self.live_game_frame, padding=3)

        self.ally_team_average_label = ttk.Label(self.ally_team_average_frame, text="Ally Team Average", font=("Segoe UI", 12))
        self.enemy_team_average_label = ttk.Label(self.enemy_team_average_frame, text="Enemy Team Average", font=("Segoe UI", 12))

        ally_team_average_image = self.load_image(r"..\assets\Logo.png", 35, 35)
        enemy_team_average_image = self.load_image(r"..\assets\Logo.png", 35, 35)

        self.ally_team_average_image = ttk.Label(self.ally_team_average_frame)
        self.ally_team_average_image.image = ally_team_average_image
        self.ally_team_average_image.configure(image=ally_team_average_image)

        self.enemy_team_average_image = ttk.Label(self.enemy_team_average_frame)
        self.enemy_team_average_image.image = enemy_team_average_image
        self.enemy_team_average_image.configure(image=enemy_team_average_image)

        self.player_table = LabelGrid(self.live_game_frame,
                                      content=[
                                          ["Agent", "Name", "Rank", "Preak Rank", "Previous Rank", "HS", "WR", "KD", "Level"],

                                          [self.load_agent_image("eb93336a-449b-9c1b-0a54-a891f7921d69"), "SomeLongName#12345", "Platinum 2", "Diamond 2", "Platinum 1", "17", "50", "1.2", "125"],
                                          [self.load_agent_image("569fdd95-4d10-43ab-ca70-79becc718b46"), "Short#000", "Gold 3", "Platinum 1", "Gold 2", "22", "45", "1.1", "37"],
                                          [self.load_agent_image("add6443a-41bd-e414-f6ad-e58d267f4e95"), "MiddleName#0000", "Platinum 2", "Diamond 3", "Platinum 1", "17", "72", "1.2", "45"],
                                          [self.load_agent_image("95b78ed7-4637-86d9-7e41-71ba8c293152"), "Ranadad#210", "Platinum 2", "Immortal 1", "Platinum 1", "17", "50", "1.2", "321"],
                                          [self.load_agent_image("9f0d8ba9-4140-b941-57d3-a7ad57c6b417"), "EzWin#420", "Gold 3", "Gold 1", "Gold 2", "22", "45", "1.1", "42"],
                                          ["", "", "", "", "", "", "", "", ""],
                                          [self.load_agent_image("320b2a48-4d9b-a075-30f1-1f93a9b638fa"), "UnicodeNameッ#012", "Platinum 2", "Ascendant 2", "Platinum 1", "17", "30", "1.2", "93"],
                                          [self.load_agent_image("e370fa57-4757-3604-3648-499e1f642d3f"), "BB#231", "Gold 3", "Platinum 1", "Gold 2", "22", "60", "1.1", "54"],
                                          [self.load_agent_image("1e58de9c-4950-5125-93e9-a0aee9f98746"), "TRacker#2223", "Platinum 2", "Diamond 1", "Platinum 1", "17", "12", "1.2", "421"],
                                          [self.load_agent_image("41fb69c1-4189-7b37-f117-bcaf1e96f1bf"), "Randd#ezy", "Immortal 2", "Radiant", "Immortal 1", "17", "90", "2.3", "212"],
                                          [self.load_agent_image("7f94d92c-4234-0a36-9646-3a87eb8b5c89"), "TwinTower#plane", "Gold 3", "Platinum 1", "Gold 2", "22", "65", "1.1", "12"],
                                      ],
                                      takefocus=False)

        force_refresh_image = self.load_image(r"..\assets\gui\Refresh.png", 20, 20)
        clear_cash_image = self.load_image(r"..\assets\gui\Trash.png", 20, 20)

        self.force_refresh_button = ttk.Button(self.live_game_frame, takefocus=False, command=self.force_refresh)
        self.force_refresh_button.image = force_refresh_image
        self.force_refresh_button.configure(image=force_refresh_image)

        self.clear_cash_button = ttk.Button(self.live_game_frame, takefocus=False, command=self.clear_cash)
        self.clear_cash_button.image = clear_cash_image
        self.clear_cash_button.configure(image=clear_cash_image)

        self.ally_team_average_frame.grid(row=0, column=0, sticky="w")
        self.enemy_team_average_frame.grid(row=0, column=8, sticky="e")
        self.ally_team_average_label.grid(row=0, column=0)
        self.ally_team_average_image.grid(row=1, column=0)
        self.enemy_team_average_label.grid(row=0, column=0)
        self.enemy_team_average_image.grid(row=1, column=0)

        self.player_table.grid(row=2, column=0, columnspan=9)

        self.game_info_frame.grid(row=0, column=1, columnspan=7, sticky="nsew")
        self.game_time_label.pack(side="left", expand=True)
        self.game_map_label.pack(side="left", expand=True)
        self.game_mode_label.pack(side="left", expand=True)
        self.game_state_label.pack(side="left", expand=True)

        self.force_refresh_button.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.clear_cash_button.grid(row=3, column=8, sticky="e", padx=5, pady=5)

    def show_live_game_frame(self):
        print("showing live game frame")

    def load_image(self, path, x, y):
        img = Image.open(path)
        img = img.resize((x, y))
        return ImageTk.PhotoImage(img)

    def load_agent_image(self, agent):
        with requests.Session() as s:
            response = s.get(f"https://media.valorant-api.com/agents/{agent}/displayicon.png")
            img = Image.open(BytesIO(response.content))
            img = img.resize((35, 35))
            return ImageTk.PhotoImage(img)

    def clear_cash(self):
        # TODO clear cash
        print("clearing cash")

    def force_refresh(self):
        # TODO force refresh
        print("force refreshing")

if __name__ == "__main__":
    gui = GUI()
    gui.frame.mainloop()