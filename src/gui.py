from PIL import Image, ImageTk, ImageEnhance
from datetime import datetime, timedelta
from io import BytesIO

import ttkbootstrap as ttk
import tkinter as tk

import urllib.parse
import webbrowser
import threading
import requests
import base64
import queue
import json
import os

from src.colors import Colors
from src.constants import *

colors = Colors(hide_names, {}, AGENTCOLORLIST)
name_column = None
t = None

request_queue = queue.Queue()
result_queue = queue.Queue()


def submit_to_tkinter(callable, *args, **kwargs):
    request_queue.put((callable, args, kwargs))


class LabelGrid(tk.Frame):
    """
    Creates a grid of labels that have their cells populated by content.
    """
    def __init__(self, master, content=(["", ""], ["", ""]), *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.content = content
        self.content_size = (len(content), len(content[0]))
        self.labels = []
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
                    label.bind("<Button-1>", self.on_label_click)
            content_type = type(content).__name__
            if content_type in ('str', 'int', 'float'):
                label['text'] = content
            elif content_type == 'PhotoImage':
                label['image'] = content

            self.labels[row].append(label)

        for i in range(self.content_size[0]):
            self.labels.append([])
            for j in range(self.content_size[1]):
                __put_content_in_label(i, j)

    def _display_labels(self):
        for i in range(self.content_size[0]):
            for j in range(self.content_size[1]):
                self.labels[i][j].grid(row=i, column=j)

    def update_content(self, content):
        for i in range(self.content_size[0]):
            for j in range(self.content_size[1]):
                self.labels[i][j].destroy()

        self.content = content
        self.content_size = (len(content), len(content[0]))
        self.labels = []
        self._create_labels()
        self._display_labels()

    def on_label_click(self, event):
        label_text = self.labels[event.widget.row][event.widget.column]['text']
        webbrowser.open_new_tab(f"https://tracker.gg/valorant/profile/riot/{urllib.parse.quote(label_text)}/overview")

class GUI:
    def __init__(self, config):
        self.config = config
        self.cfg = {}

    def init_gui(self):
        global t

        t.title(f"VALORANT rank yoinker v{version}")

        self.screen_width = t.winfo_screenwidth()
        self.screen_height = t.winfo_screenheight()

        self.start_time = datetime.now()

        t.geometry(f"{int(self.screen_width // 1.75)}x{int(self.screen_height // 1.7)}")

        t.iconbitmap("assets/Logo.ico")
        self.style = ttk.Style(theme="darkly")

        self.tab_frame = ttk.Frame(t, padding=5)
        self.create_tabs()
        self.tab_frame.grid(row=0, column=0, sticky="w")

        self.live_game_frame = ttk.Frame(t, padding=5, relief="solid", borderwidth=1)
        self.game_info_frame = ttk.Frame(self.live_game_frame)
        self.map_info_frame = ttk.Frame(self.live_game_frame)

        self.game_time_var = tk.StringVar()
        self.game_time_label = ttk.Label(self.game_info_frame, text="0:00", font=("Segoe UI", 12))

        self.game_map_image_label = ttk.Label(self.map_info_frame, text="", font=("Segoe UI", 12), compound="center")

        self.game_server_label = ttk.Label(self.map_info_frame, text="", font=("Segoe UI", 12))
        self.game_server_label.configure(foreground=colors.rgb_to_hex((200, 200, 200)))

        # TODO add game_mode
        self.game_mode_label = ttk.Label(self.game_info_frame, text="", font=("Segoe UI", 12))

        self.game_state_label = ttk.Label(self.game_info_frame, text="Loading...", font=("Segoe UI", 12))

        self.player_table = LabelGrid(self.live_game_frame)
        self.create_live_game_frame()
        self.live_game_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

        self.skins_frame = ttk.Frame(t, padding=5, relief="solid", borderwidth=1)
        self.player_skin_table = LabelGrid(self.skins_frame)
        self.create_skin_frame()

        self.settings_frame = ttk.Frame(t, padding=5, relief="solid", borderwidth=1)
        self.table_column_vars = {}
        self.optional_feature_vars = {}
        self.weapon_amount_frame = ttk.LabelFrame()
        self.weapon_amount_entry = ttk.Entry()
        self.weapon_comboboxes = []
        self.create_settings_frame()

    def process_queue_batch(self):
        while not request_queue.empty():
            callable, args, kwargs = request_queue.get()
            print("Processing something in queue")
            retval = callable(*args, **kwargs)
            result_queue.put(retval)
            print("Finished processing something in queue")

        # Schedule the next batch processing after 2 seconds
        self.update_game_time()
        threading.Timer(1.0, self.process_queue_batch).start()

    def threadmain(self):
        global t
        t = tk.Tk()
        self.init_gui()

        self.process_queue_batch()  # Start processing the queue in batches
        t.mainloop()

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
        self.player_table = LabelGrid(self.live_game_frame, takefocus=False)

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
        self.game_map_image_label.pack(side="left", expand=True)

        self.force_refresh_button.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.clear_cash_button.grid(row=3, column=8, sticky="e", padx=5, pady=5)

    def create_skin_frame(self):
        # TODO add real data, get gui working while program is running
        header = ["Agent", "Name"]
        for weapon in self.config.weapons:
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
                                               self.skin_seperator(),
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
        weapon_list = self.config.weapons
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
        self.cfg["weapon"] = ", ".join([weapon_combobox.get() for weapon_combobox in self.weapon_comboboxes])
        self.cfg["weapon_amount"] = self.weapon_amount_entry.get()
        self.cfg["port"] = self.port_entry.get()
        self.cfg["chat_limit"] = self.chat_limit_entry.get()
        self.cfg["table"] = {key: var.get() for key, var in self.table_column_vars.items()}
        self.cfg["flags"] = {key: var.get() for key, var in self.optional_feature_vars.items()}
        self.cfg = DEFAULT_CONFIG | self.cfg

        with open("config.json", "w") as outfile:
            json.dump(self.cfg, outfile, indent=2)

    def reset_config(self):
        """ resets the configuration to default """
        self.config = DEFAULT_CONFIG.copy()
        self.weapon_amount_entry.delete(0, "end")
        self.weapon_amount_entry.insert(0, "1")
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

    def load_image(self, path, x, y):
        # check if path exists
        if not os.path.exists(path):
            print(f"Could not find image at {path}")
            return ""
        img = Image.open(path)
        img = img.resize((x, y))
        return ImageTk.PhotoImage(img)

    def load_agent_image(self, agent):
        if agent == "":
            return ""
        cache_file = r"assets\gui\cache\agents.json"

        # check if the cache file exists
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                agents = json.load(f)

        else:
            agents = {}

        if agent in agents:
            # load image from cache
            base64_data = agents[agent]
            img_data = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)

        # fetch image from the web
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
        if rank == "":
            return ""
        rank = str(rank)
        cache_file = r"assets\gui\cache\ranks.json"

        # check if the cache file exists
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8") as f:
                ranks = json.load(f)

        else:
            ranks = {}

        if rank in ranks:
            # load image from cache
            base64_data = ranks[rank]
            img_data = base64.b64decode(base64_data)
            img = Image.open(BytesIO(img_data))
            return ImageTk.PhotoImage(img)

        # fetch image from the web
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

    def load_map(self, map_uuid):
        if map_uuid == "":
            return ""

        def load_map_image():
            cache_file = r"assets\gui\cache\map_images.json"

            # check if the cache file exists
            if os.path.exists(cache_file):
                with open(cache_file, "r") as f:
                    map_images = json.load(f)

            else:
                map_images = {}

            if map_uuid in map_images:
                # load image from cache
                base64_data = map_images[map_uuid]
                img_data = base64.b64decode(base64_data)
                img = Image.open(BytesIO(img_data))
                return ImageTk.PhotoImage(img)

            # fetch image from the web
            with requests.Session() as s:
                response = s.get(f"https://media.valorant-api.com/maps/{map_uuid}/splash.png")
                img = Image.open(BytesIO(response.content))
                img = img.resize((187, 105))
                img = img.crop((21, 30, 165, 65))
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(0.75)

                # Store the fetched image in the cache
                img_bytesio = BytesIO()
                img.save(img_bytesio, format="PNG")
                base64_data = base64.b64encode(img_bytesio.getvalue()).decode("utf-8")
                map_images[map_uuid] = base64_data
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(map_images, f)

                return ImageTk.PhotoImage(img)

        def load_map_name():
            cache_file = r"assets\gui\cache\map_names.json"

            # check if the cache file exists
            if os.path.exists(cache_file):
                with open(cache_file, "r", encoding="utf-8") as f:
                    map_names = json.load(f)

            else:
                map_names = {}

            if map_uuid in map_names:
                # load image from cache
                map_name = map_names[map_uuid]

            # fetch image from the web
            with requests.Session() as s:
                response = s.get(f"https://valorant-api.com/v1/maps/{map_uuid}").json()
                map_name = response["data"]["displayName"]

                # Store the fetched image in the cache
                map_names[map_uuid] = map_name
                with open(cache_file, "w", encoding="utf-8") as f:
                    json.dump(map_names, f)

                return map_name

        return load_map_name(), load_map_image()

    def clear_frame(self):
        """ hide all frames, apart from the tabs """
        for widget in t.winfo_children():
            if widget not in [self.tab_frame]:
                widget.grid_forget()

    def show_live_game_frame(self):
        self.clear_frame()
        self.live_game_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def show_skins_frame(self):
        self.clear_frame()
        self.skins_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def show_settings_frame(self):
        self.clear_frame()
        self.settings_frame.grid(row=1, column=0, columnspan=10, padx=5, pady=5, sticky="nsew")

    def clear_cash(self):
        cash_folder = r"assets\gui\cache"
        for file in os.listdir(cash_folder):
            file_path = os.path.join(cash_folder, file)
            try:
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print(e)

    def force_refresh(self):
        # TODO force refresh
        ...

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

    def skin_seperator(self):
        table_length = int(self.config.weapon_amount) + 2
        return [""] * table_length

    def emtpy_row(self):
        return [" "] * sum(1 for value in self.config.table.values() if value)

    def update_game_server(self, server):
        self.game_server_label["text"] = server

    def update_game_state(self, mode, clr):
        self.start_time = datetime.now()
        self.game_state_label["text"] = mode
        self.game_state_label.configure(foreground=colors.rgb_to_hex(clr))

        if mode == "In-Menus":
            self.game_map_image_label.image = ""
            self.game_map_image_label.configure(image="")
            self.game_map_image_label.configure(text="")

    def update_player_table(self, data):
        players_data = data.get('players', {})
        table_data = [['Party', 'Agent', 'Name', 'Rank', "RR", 'Prev. Rank', 'Peak Rank', 'Peak. Episode', 'Leaderboard', 'HS', 'WR', 'KD', 'Level']]

        for player_id, player_info in players_data.items():
            if int(player_id) != float(player_id):
                table_data.append(self.emtpy_row())
                continue

            party_icon = player_info.get('party_icon', ('', (0, 0, 0)))
            agent = self.load_agent_image(player_info.get('agent', ''))
            name = player_info.get('name', '')
            rank = self.load_rank_image(player_info.get('rank', 0))
            rr = player_info.get('rr', 0)
            prev_rank = self.load_rank_image(player_info.get('prev_rank', 0))
            peak_rank = self.load_rank_image(player_info.get('peak_rank', 0))
            peak_rank_ep = player_info.get('peak_rank_ep', ('', (0, 0, 0)))
            leaderboard = player_info.get('leaderboard', 0)
            hs = player_info.get('hs', (0, [0, 0, 0]))
            wr = player_info.get('wr', (0, [0, 0, 0]))
            kd = player_info.get('kd', 0.0)
            level = player_info.get('level', ('', (0, 0, 0)))

            # Append player data to the table_data
            table_data.append([party_icon, agent, name, rank, rr, prev_rank, peak_rank, peak_rank_ep, leaderboard, hs, wr, kd, level])

        print(table_data)

        self.player_table.update_content(table_data)

    def update_game_time(self):
        passed_time = datetime.now() - self.start_time
        passed_time = str(passed_time).split(".")[0][2:]
        self.game_time_label["text"] = passed_time

    def update_map(self, map_id):
        game_map_name, game_map_image = self.load_map(map_id)
        self.game_map_image_label.image = game_map_image
        self.game_map_image_label.configure(image=game_map_image)
        self.game_map_image_label.configure(text=game_map_name)