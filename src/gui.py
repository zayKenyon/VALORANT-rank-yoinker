from PIL import Image, ImageTk
from datetime import datetime
import ttkbootstrap as ttk
from io import BytesIO
import tkinter as tk
import requests
import base64
import json
import os

import urllib.parse
import webbrowser

from src.colors import Colors
from src.constants import *

colors = Colors(hide_names, {}, AGENTCOLORLIST)
name_column = None

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
            global name_column
            content = self.content[row][column]
            if content == "Name":
                name_column = column
            if row == 0:
                label = tk.Label(self, font=("Segoe UI", 12, "bold", "underline"), pady=3, padx=5, anchor="center")
            else:
                label = tk.Label(self, font=("Segoe UI", 12), pady=3, padx=5, anchor="center")
            label.row = row  # store the row information as an attribute to have clickable names
            label.column = column  # store the column information as an attribute to have clickable names

            if type(content).__name__ == "tuple":  # ability to color, using a tuple
                content, clr = content
                label['foreground'] = colors.rgb_to_hex(clr)
            if name_column:
                if name_column == column and row != 0:  # ability to click on the name to open tracker.gg
                    label['text'] = content
                    label.bind("<Button-1>", on_label_click)
            content_type = type(content).__name__
            if content_type in ('str', 'int'):
                label['text'] = content
            elif content_type == 'PhotoImage':
                label['image'] = content

            labels[row].append(label)

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
    def __init__(self, cfg):
        self.config = cfg

        self.frame = tk.Tk()
        self.frame.title(f"VALORANT rank yoinker v{version}")

        self.screen_width = self.frame.winfo_screenwidth()
        self.screen_height = self.frame.winfo_screenheight()

        self.start_time = datetime.now()

        self.frame.geometry(f"{int(self.screen_width // 1.75)}x{int(self.screen_height // 1.7)}")

        self.frame.iconbitmap("assets/Logo.ico")
        self.style = ttk.Style(theme="darkly")

        self.tab_frame = ttk.Frame(self.frame, padding=5)
        self.create_tabs()
        self.tab_frame.grid(row=0, column=0, sticky="w")

        self.live_game_frame = ttk.Frame(self.frame, padding=5, relief="solid", borderwidth=1)
        self.game_info_frame = ttk.Frame(self.live_game_frame)
        self.map_info_frame = ttk.Frame(self.live_game_frame)

        self.game_time_var = tk.StringVar()
        self.game_time_label = ttk.Label(self.game_info_frame, textvariable=self.game_time_var, font=("Segoe UI", 12))
        self.game_time_var.set("00:00")

        game_map_image = self.load_map_image("7eaecc1b-4337-bbf6-6ab9-04b8f06b3319")

        self.game_map_label = ttk.Label(self.map_info_frame)
        self.game_map_label.image = game_map_image
        self.game_map_label.configure(image=game_map_image)

        self.game_server_var = tk.StringVar()
        self.game_server_label = ttk.Label(self.map_info_frame, textvariable=self.game_server_var, font=("Segoe UI", 12))
        self.game_server_var.set("Frankfurt")
        self.game_server_label.configure(foreground=colors.rgb_to_hex((200, 200, 200)))

        self.game_mode_var = tk.StringVar()
        self.game_mode_label = ttk.Label(self.game_info_frame, textvariable=self.game_mode_var, font=("Segoe UI", 12))
        self.game_mode_var.set("Unrated")

        self.game_state_var = tk.StringVar()
        self.game_state_label = ttk.Label(self.game_info_frame, textvariable=self.game_state_var, font=("Segoe UI", 12))
        self.game_state_var.set("In Game")
        self.game_state_label.configure(foreground=colors.rgb_to_hex((241, 39, 39)))

        self.player_table = LabelGrid(self.live_game_frame)
        self.create_live_game_frame()
        self.live_game_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

        self.skins_frame = ttk.Frame(self.frame, padding=5, relief="solid", borderwidth=1)
        self.player_skin_table = LabelGrid(self.skins_frame)
        self.create_skin_frame()

        self.settings_frame = ttk.Frame(self.frame, padding=5, relief="solid", borderwidth=1)
        self.table_column_vars = {}
        self.optional_feature_vars = {}
        self.weapon_amount_frame = ttk.LabelFrame()
        self.weapon_amount_entry = ttk.Entry()
        self.weapon_comboboxes = []
        self.create_settings_frame()

    def create_tabs(self):
        self.live_game_tab = ttk.Button(self.tab_frame,
                                        text="Agents",
                                        command=self.show_live_game_frame,
                                        takefocus=False)
        self.skins_tab = ttk.Button(self.tab_frame,
                                    text="Skins",
                                    command=self.show_skins_frame,
                                    takefocus=False)
        self.settings_tab = ttk.Button(self.tab_frame,
                                       text="Settings",
                                       command=self.show_settings_frame,
                                       takefocus=False)

        self.live_game_tab.grid(row=0, column=0)
        self.skins_tab.grid(row=0, column=1)
        self.settings_tab.grid(row=0, column=2)

    def create_live_game_frame(self):
        # TODO calculate average rank and fetch according rank image
        self.ally_team_average_frame = ttk.Frame(self.live_game_frame, padding=3)
        self.enemy_team_average_frame = ttk.Frame(self.live_game_frame, padding=3)

        self.ally_team_average_label = ttk.Label(self.ally_team_average_frame, text="Ally Team Average", font=("Segoe UI", 12))
        self.enemy_team_average_label = ttk.Label(self.enemy_team_average_frame, text="Enemy Team Average", font=("Segoe UI", 12))

        ally_team_average_image = self.load_image(r"assets\Logo.png", 35, 35)
        enemy_team_average_image = self.load_image(r"assets\Logo.png", 35, 35)

        self.ally_team_average_image = ttk.Label(self.ally_team_average_frame)
        self.ally_team_average_image.image = ally_team_average_image
        self.ally_team_average_image.configure(image=ally_team_average_image)

        self.enemy_team_average_image = ttk.Label(self.enemy_team_average_frame)
        self.enemy_team_average_image.image = enemy_team_average_image
        self.enemy_team_average_image.configure(image=enemy_team_average_image)

        # TODO add real data, get gui working while program is running
        self.player_table = LabelGrid(self.live_game_frame,
                                      content=[
                                          ["Party", "Agent", "Name", "Rank", "Peak Rank", "Prev. Rank", "HS", "WR", "KD", "Level"],

                                          ["", self.load_agent_image("eb93336a-449b-9c1b-0a54-a891f7921d69"), "SomeLongName#12345", self.load_rank_image(19), self.load_rank_image(25) ,self.load_rank_image(23), colors.get_hs_gradient(17), colors.get_wr_gradient(50), "1.2", colors.level_to_color(321)],
                                          ["", self.load_agent_image("569fdd95-4d10-43ab-ca70-79becc718b46"), "Short#000", self.load_rank_image(9), self.load_rank_image(12), self.load_rank_image(11), colors.get_hs_gradient(22), colors.get_wr_gradient(45), "1.1", colors.level_to_color(125)],
                                          ["", self.load_agent_image("add6443a-41bd-e414-f6ad-e58d267f4e95"), "MiddleName#0000", self.load_rank_image(15), self.load_rank_image(18), self.load_rank_image(16), colors.get_hs_gradient(17), colors.get_wr_gradient(72), "1.2", colors.level_to_color(72)],
                                          ["", self.load_agent_image("95b78ed7-4637-86d9-7e41-71ba8c293152"), "Ranadad#210", self.load_rank_image(13), self.load_rank_image(16), self.load_rank_image(14), colors.get_hs_gradient(17), colors.get_wr_gradient(50), "1.2", colors.level_to_color(51)],
                                          ["", self.load_agent_image("9f0d8ba9-4140-b941-57d3-a7ad57c6b417"), "EzWin#420", self.load_rank_image(17), self.load_rank_image(19), self.load_rank_image(17), colors.get_hs_gradient(22), colors.get_wr_gradient(45), "1.1", colors.level_to_color(42)],
                                          # TODO add a seperator
                                          ["", "", "", "", "", "", "", "", "", ""],
                                          ["", self.load_agent_image("320b2a48-4d9b-a075-30f1-1f93a9b638fa"), "UnicodeNameッ#012", self.load_rank_image(17), self.load_rank_image(19), self.load_rank_image(15), colors.get_hs_gradient(17), colors.get_wr_gradient(30), "1.2", colors.level_to_color(421)],
                                          ["", self.load_agent_image("e370fa57-4757-3604-3648-499e1f642d3f"), "BB#231", self.load_rank_image(9), self.load_rank_image(16), self.load_rank_image(15), colors.get_hs_gradient(22), colors.get_wr_gradient(60), "1.1", colors.level_to_color(212)],
                                          ["", self.load_agent_image("1e58de9c-4950-5125-93e9-a0aee9f98746"), "TRacker#2223", self.load_rank_image(20), self.load_rank_image(23), self.load_rank_image(21), colors.get_hs_gradient(17), colors.get_wr_gradient(12), "1.2", colors.level_to_color(90)],
                                          ["", self.load_agent_image("41fb69c1-4189-7b37-f117-bcaf1e96f1bf"), "Randd#ezy", self.load_rank_image(15), self.load_rank_image(21), self.load_rank_image(20), colors.get_hs_gradient(17), colors.get_wr_gradient(90), "2.3", colors.level_to_color(72)],
                                          ["", self.load_agent_image("7f94d92c-4234-0a36-9646-3a87eb8b5c89"), "TwinTower#plane", self.load_rank_image(11), self.load_rank_image(13), self.load_rank_image(12), colors.get_hs_gradient(22), colors.get_wr_gradient(65), "1.1", colors.level_to_color(12)],
                                      ],
                                      takefocus=False)

        force_refresh_image = self.load_image(r"assets\gui\Refresh.png", 20, 20)
        clear_cash_image = self.load_image(r"assets\gui\Trash.png", 20, 20)

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
        self.game_mode_label.pack(side="left", expand=True)
        self.game_state_label.pack(side="left", expand=True)

        self.map_info_frame.grid(row=3, column=1, columnspan=7, sticky="nsew")
        self.game_server_label.pack(side="left", expand=True)
        self.game_map_label.pack(side="left", expand=True)

        self.force_refresh_button.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.clear_cash_button.grid(row=3, column=8, sticky="e", padx=5, pady=5)

    def create_skin_frame(self):
        # TODO add real data, get gui working while program is running
        header = ["Agent", "Name"]
        print(self.config.weapon)
        for weapon in self.config.weapon.split(", "):
            print(weapon)
            header.append(weapon)
        # TODO add real data, get gui working while program is running
        self.player_skin_table = LabelGrid(self.skins_frame,
                                           content=[
                                               header,
                                               [self.load_agent_image("eb93336a-449b-9c1b-0a54-a891f7921d69"), "SomeLongName#12345", "Ion", "Prime//2.0", "Luxe", "Sentinels of Light"],
                                               [self.load_agent_image("569fdd95-4d10-43ab-ca70-79becc718b46"), "Short#000", "Winterwunderland", "Silvanus", "Gravitational Uranium Neuroblaster", "Singularity"],
                                               [self.load_agent_image("add6443a-41bd-e414-f6ad-e58d267f4e95"), "MiddleName#0000", "Prism II", "Ruination", "Elderflame", "Nebula"],
                                               [self.load_agent_image("95b78ed7-4637-86d9-7e41-71ba8c293152"), "Ranadad#210", "Sovereign", "Glitchpop", "Spline", "Sakura"],
                                               [self.load_agent_image("9f0d8ba9-4140-b941-57d3-a7ad57c6b417"), "EzWin#420", "Origin", "Spectrum", "VALORANT GO! Vol. 2", "Magepunk"],
                                               self.seperator(),
                                               [self.load_agent_image("320b2a48-4d9b-a075-30f1-1f93a9b638fa"), "UnicodeNameッ#012", "RGX 11z Pro", "Glitchpop", "Glitchpop", "Glitchpop"],
                                               [self.load_agent_image("e370fa57-4757-3604-3648-499e1f642d3f"), "BB#231", "Origin", "Recon", "Sentinels of Light", "Magepunk"],
                                               [self.load_agent_image("1e58de9c-4950-5125-93e9-a0aee9f98746"), "TRacker#2223", "Sovereign", "Spline", "Spline", "Spline"],
                                               [self.load_agent_image("41fb69c1-4189-7b37-f117-bcaf1e96f1bf"), "Randd#ezy", "Prism III", "Silvanus", "Glitchpop", "Crimsonbeast"],
                                               [self.load_agent_image("7f94d92c-4234-0a36-9646-3a87eb8b5c89"), "TwinTower#plane", "Origin", "Recon", "Recon", "Protocol 781-A"],
                                           ],
                                           takefocus=False)

        self.player_skin_table.grid(row=0, column=0, columnspan=9)

    def create_settings_frame(self):
        table_options = {
            "party": "Party",
            "agent": "Agent",
            "top_agent": "Top Agent",
            "top_agent_map": "Top Agent for Map",
            "top_role": "Top Role",
            "name": "Name",
            "skin": "Skin",
            "rank": "Rank",
            "rr": "Ranked Rating",
            "leaderboard": "Leaderboard Position",
            "peakrank": "Peak Rank",
            "previousrank": "Previous Rank",
            "headshot_percent": "Headshot Percentage",
            "winrate": "WinRate",
            "kd": "K/D Ratio",
            "level": "Account Level"
        }
        # TODO and feature ideas: top-agent for map, top-agent overall, top-role, range for calculations

        flag_options = {
            "last_played": "Last Played Stats",
            "auto_hide_leaderboard": "Auto Hide Leaderboard Column",
            "game_chat": "Print Game Chat",
            "peak_rank_act": "Peak Rank Act",
            "discord_rpc": "Discord Rich Presence",
            "aggregate_rank_rr": "Display Rank and Ranked Rating in the same column"
        }

        default_config = DEFAULT_CONFIG.copy()

        self.settings_label = ttk.Label(self.settings_frame, text="Settings", font=("Segoe UI", 14, "bold"))

        # Create a frame for the weapon amount
        self.weapon_combobox_frame = ttk.Frame(self.settings_frame, borderwidth=0, relief="flat")
        self.weapon_amount_frame = ttk.LabelFrame(self.settings_frame, borderwidth=0, relief="flat")
        self.weapon_amount_lable = ttk.Label(self.weapon_amount_frame, text="Weapons", font=("Segoe UI", 12, "bold"))
        self.weapon_amount_explanation_lable = ttk.Label(self.weapon_amount_frame, text="Enter the amount of weapons to show:")
        self.weapon_amount_refresh_button = ttk.Button(self.weapon_amount_frame, text="Refresh", command=self.refresh_weapon_amount, takefocus=False)

        # Load the weapon amount from the configuration
        weapon_list = self.config.weapon.split(", ")
        weapon_amount = self.config.weapon_amount
        self.weapon_amount_entry.insert(0, str(weapon_amount))

        # Create the weapon comboboxes based on the configuration
        for weapon in weapon_list:
            weapon_combobox = ttk.Combobox(self.weapon_combobox_frame, values=WEAPONS)
            weapon_combobox.set(weapon)
            self.weapon_comboboxes.append(weapon_combobox)

        self.refresh_weapon_amount()

        self.weapon_amount_entry = ttk.Entry(self.weapon_amount_frame)
        self.weapon_amount_entry.insert(0, self.config.weapon_amount)

        # Create a frame for table columns
        self.table_frame = ttk.LabelFrame(self.settings_frame, borderwidth=0, relief="flat")
        self.table_columns_lable = ttk.Label(self.table_frame, text="Table Columns", font=("Segoe UI", 12, "bold"))
        self.table_columns_explanation_lable = ttk.Label(self.table_frame, text="Select table columns to display:")
        for i, (key, value) in enumerate(table_options.items()):
            var = tk.BooleanVar(value=bool(self.config.get_table_flag(key)))
            checkbox = ttk.Checkbutton(self.table_frame, text=value, variable=var)
            checkbox.grid(row=i + 2, column=0, columnspan=2, sticky="w")
            self.table_column_vars[key] = var

        # Create a frame for server port
        self.port_frame = ttk.LabelFrame(self.settings_frame, borderwidth=0, relief="flat")
        self.port_lable = ttk.Label(self.port_frame, text="Server Port", font=("Segoe UI", 12, "bold"))
        self.port_explanation_lable = ttk.Label(self.port_frame, text="Enter the port for the server to run:")

        self.port_entry = ttk.Entry(self.port_frame)
        self.port_entry.insert(0, self.config.port)

        # Create a frame for optional features
        self.optional_flags_frame = ttk.LabelFrame(self.settings_frame, borderwidth=0, relief="flat")
        self.optional_flag_label = ttk.Label(self.optional_flags_frame, text="Optional Features", font=("Segoe UI", 12, "bold"))
        self.optional_flag_explanation_label = ttk.Label(self.optional_flags_frame, text="Select optional features:")
        for i, (key, value) in enumerate(flag_options.items()):
            var = tk.BooleanVar(value=bool(self.config.get_feature_flag(key)))
            checkbox = ttk.Checkbutton(self.optional_flags_frame, text=value, variable=var)
            checkbox.grid(row=i + 2, column=0, columnspan=2, sticky="w")
            self.optional_feature_vars[key] = var

        # Create a frame for chat limit
        self.chat_limit_frame = ttk.LabelFrame(self.settings_frame, borderwidth=0, relief="flat")
        self.chat_limit_label = ttk.Label(self.chat_limit_frame, text="Chat Limit", font=("Segoe UI", 12, "bold"))
        self.chat_limit_label_explanation = ttk.Label(self.chat_limit_frame, text="Enter the length of chat messages history:")
        self.chat_limit_entry = ttk.Entry(self.chat_limit_frame)
        self.chat_limit_entry.insert(0, self.config.chat_limit)

        # Create a frame for calculation range
        self.calculation_range_frame = ttk.LabelFrame(self.settings_frame, borderwidth=0, relief="flat")
        self.calculation_range_label = ttk.Label(self.calculation_range_frame, text="Calculation Range", font=("Segoe UI", 12, "bold"))
        self.calculation_range_label_explanation = ttk.Label(self.calculation_range_frame, text="Backtracking of stats for KD, Top-Agent:\nSignificant time increase for higher values!")
        self.calculation_range_entry = ttk.Entry(self.calculation_range_frame)
        self.calculation_range_entry.insert(0, self.config.calculation_range)

        # Create a Save button to apply the configuration
        self.continue_config_frame = ttk.Frame(self.settings_frame, borderwidth=0, relief="flat")
        self.save_config_button = ttk.Button(self.continue_config_frame, text="Save", command=self.save_config, takefocus=False)
        self.reset_config_button = ttk.Button(self.continue_config_frame, text="Reset", command=self.reset_config, takefocus=False)

        self.settings_label.grid(row=0, column=0, columnspan=2)

        self.weapon_amount_frame.grid(row=1, column=1, padx=10, pady=3, sticky="w")
        self.weapon_amount_lable.grid(row=0, column=0, sticky="w")
        self.weapon_amount_explanation_lable.grid(row=1, column=0, sticky="w")
        self.weapon_amount_entry.grid(row=1, column=1, sticky="w")
        self.weapon_amount_refresh_button.grid(row=1, column=2, sticky="w")

        self.port_frame.grid(row=1, column=0, padx=10, pady=3, sticky="w")
        self.port_lable.grid(row=0, column=0, sticky="w")
        self.port_explanation_lable.grid(row=1, column=0, sticky="w")
        self.port_entry.grid(row=1, column=1, sticky="w")

        self.table_frame.grid(row=2, column=0, padx=10, pady=3, sticky="w")
        self.table_columns_lable.grid(row=0, column=0, columnspan=2, sticky="w")
        self.table_columns_explanation_lable.grid(row=1, column=0, columnspan=2, sticky="w")

        self.optional_flags_frame.grid(row=2, column=1, padx=10, pady=3, sticky="w")
        self.optional_flag_label.grid(row=0, column=0, columnspan=2, sticky="w")
        self.optional_flag_explanation_label.grid(row=1, column=0, columnspan=2, sticky="w")

        self.chat_limit_frame.grid(row=3, column=0, padx=10, pady=3, sticky="w")
        self.chat_limit_label.grid(row=0, column=0, sticky="w")
        self.chat_limit_label_explanation.grid(row=1, column=0, sticky="w")
        self.chat_limit_entry.grid(row=1, column=1, sticky="w")

        self.calculation_range_frame.grid(row=3, column=1, padx=10, pady=3, sticky="w")
        self.calculation_range_label.grid(row=0, column=0, sticky="w")
        self.calculation_range_label_explanation.grid(row=1, column=0, sticky="w")
        self.calculation_range_entry.grid(row=1, column=1, sticky="w")

        self.continue_config_frame.grid(row=4, column=0, columnspan=2, pady=5)
        self.save_config_button.grid(row=0, column=0, padx=5, pady=5)
        self.reset_config_button.grid(row=0, column=1, padx=5, pady=5)

    def save_config(self):
        """saves the configuration to config.json"""
        self.config["weapon"] = ", ".join([weapon_combobox.get() for weapon_combobox in self.weapon_comboboxes])
        self.config["weapon_amount"] = self.weapon_amount_entry.get()
        self.config["port"] = self.port_entry.get()
        self.config["chat_limit"] = self.chat_limit_entry.get()
        self.config["table"] = {key: var.get() for key, var in self.table_column_vars.items()}
        self.config["flags"] = {key: var.get() for key, var in self.optional_feature_vars.items()}
        self.config = DEFAULT_CONFIG | self.config

        with open("config.json", "w") as outfile:
            json.dump(self.config, outfile, indent=2)

        print("Config saved successfully")

    def reset_config(self):
        """ resets the configuration to default """
        self.config = DEFAULT_CONFIG.copy()
        self.weapon_amount_entry.delete(0, "end")
        self.weapon_amount_entry.insert(0, 1)
        for weapon_combobox in self.weapon_comboboxes:
            weapon_combobox.destroy()
        self.weapon_comboboxes = []
        self.refresh_weapon_amount()
        self.port_entry.delete(0, "end")
        self.port_entry.insert(0, DEFAULT_CONFIG["port"])
        self.chat_limit_entry.delete(0, "end")
        self.chat_limit_entry.insert(0, DEFAULT_CONFIG.get("chat_limit", 5))
        for key, var in self.table_column_vars.items():
            var.set(DEFAULT_CONFIG.get("table", DEFAULT_CONFIG["table"]).get(key, DEFAULT_CONFIG["table"][key]))
        for key, var in self.optional_feature_vars.items():
            var.set(DEFAULT_CONFIG.get("flags", DEFAULT_CONFIG["flags"]).get(key, DEFAULT_CONFIG["flags"][key]))
        print("Config reset successfully")

    def load_image(self, path, x, y):
        img = Image.open(path)
        img = img.resize((x, y))
        return ImageTk.PhotoImage(img)

    def load_agent_image(self, agent):
        cache_file = r"assets\gui\cache\agents.json"

        # check if the cache file exists
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                agents = json.load(f)

        else:
            agents = {}

        if agent in agents:
            # load image from cache
            print("Loading Agent image from cache")
            base64_data = agents[agent]
            img_data = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)

        # fetch image from the web
        print("Fetching Agent image from web")
        with requests.Session() as s:
            response = s.get(f"https://media.valorant-api.com/agents/{agent}/displayicon.png")
            img = Image.open(BytesIO(response.content))
            img = img.resize((35, 35))
            # Store the fetched image in the cache
            img_bytesio = BytesIO()
            img.save(img_bytesio, format="PNG")
            base64_data = base64.b64encode(img_bytesio.getvalue()).decode("utf-8")
            agents[agent] = base64_data
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(agents, f)

            return ImageTk.PhotoImage(img)

    def load_rank_image(self, rank):
        cache_file = r"assets\gui\cache\ranks.json"

        # check if the cache file exists
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                ranks = json.load(f)

        else:
            ranks = {}

        if rank in ranks:
            # load image from cache
            print("Loading Rank image from cache")
            base64_data = ranks[rank]
            img_data = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)

        # fetch image from the web
        print("Fetching Rank image from web")
        with requests.Session() as s:
            response = s.get(f"https://media.valorant-api.com/competitivetiers/03621f52-342b-cf4e-4f86-9350a49c6d04/{rank}/smallicon.png")
            img = Image.open(BytesIO(response.content))
            img = img.resize((35, 35))
            # Store the fetched image in the cache
            img_bytesio = BytesIO()
            img.save(img_bytesio, format="PNG")
            base64_data = base64.b64encode(img_bytesio.getvalue()).decode("utf-8")
            ranks[rank] = base64_data
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(ranks, f)

            return ImageTk.PhotoImage(img)

    def load_map_image(self, map):
        cache_file = r"assets\gui\cache\maps.json"

        # check if the cache file exists
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                maps = json.load(f)

        else:
            maps = {}

        if map in maps:
            # load image from cache
            print("Loading Map image from cache")
            base64_data = maps[map]
            img_data = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)

        # fetch image from the web
        print("Fetching Map image from web")
        with requests.Session() as s:
            response = s.get(f"https://media.valorant-api.com/maps/{map}/splash.png")
            img = Image.open(BytesIO(response.content))
            img = img.resize((83, 35))
            # Store the fetched image in the cache
            img_bytesio = BytesIO()
            img.save(img_bytesio, format="PNG")
            base64_data = base64.b64encode(img_bytesio.getvalue()).decode("utf-8")
            maps[map] = base64_data
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(maps, f)

            return ImageTk.PhotoImage(img)

    def clear_frame(self):
        """ hide all frames, apart from the tabs """
        print("clearing frame")
        for widget in self.frame.winfo_children():
            if widget not in [self.tab_frame]:
                widget.grid_forget()

    def show_live_game_frame(self):
        self.clear_frame()
        print("showing live game frame")
        self.live_game_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def show_skins_frame(self):
        self.clear_frame()
        self.skins_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def show_settings_frame(self):
        self.clear_frame()
        print("showing settings frame")
        self.settings_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def clear_cash(self):
        # Path to the JSON cache file
        cache_file = r"assets\gui\cache\agents.json"

        try:
            # Check if the cache file exists
            if os.path.exists(cache_file):
                # Delete the cache file
                os.remove(cache_file)
                print("Cache cleared successfully.")
            else:
                print("Cache file does not exist.")
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")

    def force_refresh(self):
        # TODO force refresh
        print("force refreshing")

    def refresh_weapon_amount(self):
        # TODO refresh weapon amount
        weapon_amount = self.weapon_amount_entry.get()

        if not weapon_amount:
            weapon_amount = 1

        weapon_amount = int(weapon_amount)

        if weapon_amount > len(self.weapon_comboboxes):
            # Add weapon comboboxes
            for i in range(weapon_amount - len(self.weapon_comboboxes)):
                weapon_combobox = ttk.Combobox(self.weapon_combobox_frame, values=WEAPONS)
                weapon_combobox.current(0)
                self.weapon_comboboxes.append(weapon_combobox)

        elif weapon_amount < len(self.weapon_comboboxes):
            # Remove weapon comboboxes
            for i in range(len(self.weapon_comboboxes) - weapon_amount):
                self.weapon_comboboxes[-1].destroy()
                self.weapon_comboboxes.pop()

        # Clear the existing grid
        for widget in self.weapon_combobox_frame.winfo_children():
            widget.grid_forget()

        # Display weapon comboboxes in the new frame
        for i, weapon_combobox in enumerate(self.weapon_comboboxes):
            weapon_combobox.grid(row=i + 2, column=0, columnspan=2, sticky="w")

        # Update the grid of the weapon_combobox_frame in the settings_frame
        self.weapon_combobox_frame.grid(row=1, column=3, rowspan=4, sticky="new")

    def seperator(self):
        table_length = int(self.config.weapon_amount) + 2
        return [""] * table_length

    def set_game_map(self, map_id):
        game_map_image = self.load_map_image(map_id)
        self.game_map_label.image = game_map_image
        self.game_map_label.configure(image=game_map_image)

    def set_game_mode(self, mode):
        self.game_mode_var.set(gamemodes.get(mode, "n/A"))

    def set_game_state(self, state):
        self.start_time = datetime.now()
        game_state = GAMESATEDICT.get(state, None)
        self.game_state_var.set(game_state[0])
        self.game_state_label.configure(foreground=game_state[1])

    def set_player_table(self, table):
        self.player_table.content = table
        self.player_table._create_labels()
        self.player_table._display_labels()
        self.frame.update()

    def refresh_game_time(self):
        diff = datetime.now() - self.start_time
        past_time = divmod(diff.days * 86400 + diff.seconds, 60)
        self.game_time_var.set(f"{past_time[0]}:{past_time[1]}")
