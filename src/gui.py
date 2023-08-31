from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk

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
            label = tk.Label(self, font=("Segoe UI", 12), pady=3, padx=5, anchor="center", relief="groove",
                             borderwidth=1)
            label.row = row  # Store the row information as an attribute
            label.column = column  # Store the column information as an attribute

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

        self.frame.geometry(f"{int(self.screen_width // 1.75)}x{int(self.screen_height // 1.75)}")

        self.frame.iconbitmap("../assets/Logo.ico")
        self.style = ttk.Style(theme="darkly")

        self.tab_frame = ttk.Frame(self.frame, relief="groove", borderwidth=1, padding=5)
        self.create_tabs()
        self.tab_frame.grid(row=0, column=0)

        self.live_game_frame = ttk.Frame(self.frame, relief="groove", borderwidth=1, padding=5)
        self.game_info_frame = ttk.Frame(self.live_game_frame, relief="groove", borderwidth=1, padding=10)
        self.game_time_label = ttk.Label(self.game_info_frame, text="00:00", relief="groove", borderwidth=1, padding=5, font=("Segoe UI", 12))
        self.game_map_label = ttk.Label(self.game_info_frame, text="Ascent", relief="groove", borderwidth=1, padding=5, font=("Segoe UI", 12))
        self.game_mode_label = ttk.Label(self.game_info_frame, text="Unrated", relief="groove", borderwidth=1, padding=5, font=("Segoe UI", 12))
        self.game_state_label = ttk.Label(self.game_info_frame, text="In Game", relief="groove", borderwidth=1, padding=5, font=("Segoe UI", 12))
        self.player_table = LabelGrid(self.live_game_frame)
        self.create_live_game_frame()
        self.live_game_frame.grid(row=1, column=0, padx=10)

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
        self.ally_team_average_frame = ttk.Frame(self.live_game_frame, relief="groove", borderwidth=1, padding=5)
        self.enemy_team_average_frame = ttk.Frame(self.live_game_frame, relief="groove", borderwidth=1, padding=5)

        self.ally_team_average_label = ttk.Label(self.ally_team_average_frame, text="Ally Team Average", font=("Segoe UI", 12))
        self.enemy_team_average_label = ttk.Label(self.enemy_team_average_frame, text="Enemy Team Average", font=("Segoe UI", 12))

        ally_img = Image.open(r"..\assets\Logo.png")
        ally_img = ally_img.resize((35, 35))
        ally_team_average_image = ImageTk.PhotoImage(ally_img)

        enemy_img = Image.open(r"..\assets\Logo.png")
        enemy_img = enemy_img.resize((35, 35))
        enemy_team_average_image = ImageTk.PhotoImage(enemy_img)

        self.ally_team_average_image = ttk.Label(self.ally_team_average_frame, padding=5)
        self.ally_team_average_image.image = ally_team_average_image
        self.ally_team_average_image.configure(image=ally_team_average_image)

        self.enemy_team_average_image = ttk.Label(self.enemy_team_average_frame, padding=5)
        self.enemy_team_average_image.image = enemy_team_average_image
        self.enemy_team_average_image.configure(image=enemy_team_average_image)

        self.ally_team_average_label.grid(row=0, column=0)
        self.ally_team_average_image.grid(row=1, column=0)
        self.enemy_team_average_label.grid(row=0, column=0)
        self.enemy_team_average_image.grid(row=1, column=0)

        self.ally_team_average_frame.grid(row=0, column=0, sticky="w")
        self.enemy_team_average_frame.grid(row=0, column=8, sticky="e")

        self.player_table = LabelGrid(self.live_game_frame,
                                      content=[
                                          ["Agent", "Name", "Rank", "Preak Rank", "Previous Rank", "HS", "WR", "KD", "Level"],

                                          ["Chamber", "SomeLongName#12345", "Platinum 2", "Diamond 2", "Platinum 1", "17", "50", "1.2", "125"],
                                          ["Sage", "Short#000", "Gold 3", "Platinum 1", "Gold 2", "22", "45", "1.1", "37"],
                                          ["Jett", "MiddleName#0000", "Platinum 2", "Diamond 3", "Platinum 1", "17", "72", "1.2", "45"],
                                          ["Harbor", "Ranadad#210", "Platinum 2", "Immortal 1", "Platinum 1", "17", "50", "1.2", "321"],
                                          ["Brimstone", "EzWin#420", "Gold 3", "Gold 1", "Gold 2", "22", "45", "1.1", "42"],
                                          ["", "", "", "", "", "", "", "", ""],
                                          ["Sova", "UnicodeNameッ#012", "Platinum 2", "Ascendant 2", "Platinum 1", "17", "30", "1.2", "93"],
                                          ["Deadlock", "BB#231", "Gold 3", "Platinum 1", "Gold 2", "22", "60", "1.1", "54"],
                                          ["Omen", "TRacker#2223", "Platinum 2", "Diamond 1", "Platinum 1", "17", "12", "1.2", "421"],
                                          ["Viper", "Randd#ezy", "Immortal 2", "Radiant", "Immortal 1", "17", "90", "2.3", "212"],
                                          ["Yoru", "TwinTower#plane", "Gold 3", "Platinum 1", "Gold 2", "22", "65", "1.1", "12"],
                                      ],
                                      takefocus=False)

        self.player_table.grid(row=2, column=0, columnspan=9)

        self.game_info_frame.grid(row=0, column=1, columnspan=7, sticky="nsew")
        self.game_time_label.pack(side="left", expand=True)
        self.game_map_label.pack(side="left", expand=True)
        self.game_mode_label.pack(side="left", expand=True)
        self.game_state_label.pack(side="left", expand=True)

    def show_live_game_frame(self):
        print("showing live game frame")


if __name__ == "__main__":
    gui = GUI()
    gui.frame.mainloop()