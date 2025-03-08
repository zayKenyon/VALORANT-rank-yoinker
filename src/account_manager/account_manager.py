import InquirerPy, subprocess, re
import ctypes
from InquirerPy import inquirer


class AccountManager:
    def __init__(self, log, AccountConfig, AccountAuth, NUMBERTORANKS):
        self.log = log
        self.account_config = AccountConfig(log)
        self.auth = AccountAuth(log, NUMBERTORANKS)
        self.last_account_data = None

        self.log("Account manager initialized")



    def menu_change_accounts(self):
        change_accounts_prompt = {
            "type": "list",
            "name": "menu",
            "message": "Please select optional features:",
            "choices": [],
        }

        add_account_prompt = {
            "type": "list",
            "name": "menu",
            "message": "Please select optional features:",
            "choices": [
                "Add account with username & password.",
                "Add account by signing into riot client."
            ],
        }

        self.account_config.load_accounts_config()
        account_order_list = []
        accounts_list = []
        for account in self.account_config.accounts_data:
            account_order_list.append(account)
            acc_string = f"Change to: {self.account_config.accounts_data[account]['name']:<16}  | {self.account_config.accounts_data[account].get('rank'):<12} | Level: {self.account_config.accounts_data[account].get('level'):<4} | Battlepass {self.account_config.accounts_data[account].get('bp_level'):<2}/55"
            accounts_list.append(acc_string)
            change_accounts_prompt["choices"].append(acc_string)
        change_accounts_prompt["choices"].append("Add new account")
        change_accounts_prompt["choices"].append("Remove account")
        change_accounts_prompt["choices"].append("Back")
        result = InquirerPy.prompt(change_accounts_prompt)
        #Add new account
        if result["menu"] == "Add new account":
            result = InquirerPy.prompt(add_account_prompt)
            option = add_account_prompt["choices"].index(result["menu"])
            #Add account with username & password
            if option == 0:
                questions = [
                    {"type": "input", "message": "Please type username of the account you want to add:", "name": "username"},
                    {"type": "password", "message": "Please type password of the account you want to add:", "name": "password"}
                ]
                try_again = True
                while try_again:
                    result = InquirerPy.prompt(questions)
                    username = result["username"]
                    password = result["password"]
                    current_account_auth_data = self.auth.auth_account(username=username, password=password)
                    if current_account_auth_data is None:
                        try_again = inquirer.confirm(message="Invalid username or password! Do you want to try again?", default=True).execute()
                    else:
                        try_again = False
                if current_account_auth_data is None:
                    self.menu(self.last_account_data)
                else:
                    current_account_data = self.auth.get_account_data()
                    #SAVING NEW COOKIES BECAUSE OLD DOESN'T EXIST
                    self.account_config.save_account_to_config(current_account_auth_data, current_account_data)
                    #switch to new account with new auth data
                    self.account_config.switch_to_account(current_account_auth_data)

                    self.menu(current_account_data)
            #Add account by signing into riot client
            elif option == 1:
                current_account_cookies = self.account_config.add_account_with_client()
                current_account_auth_data = self.auth.auth_account(cookies=current_account_cookies)
                if current_account_auth_data is not None:
                    current_account_data = self.auth.get_account_data()
                    self.account_config.save_account_to_config(current_account_auth_data, current_account_data)
                    self.menu(current_account_data)
                else:
                    self.log("Failed to add account with client! (cookies are fetched but auth_data is none)")
                    self.menu(self.last_account_data)
        #Remove account
        elif result["menu"] == "Remove account":
            remove_account_prompt = {
                "type": "list",
                "name": "menu",
                "message": "Please select account to remove:",
                "choices": accounts_list,
            }
            result = InquirerPy.prompt(remove_account_prompt)
            account_option = remove_account_prompt["choices"].index(result["menu"])
            account = account_order_list[account_option]

            
            if self.last_account_data["name"] == self.account_config.accounts_data[account]["name"]:
                self.account_config.remove_account(account)
                self.menu(None)
            else:
                self.account_config.remove_account(account)
                self.menu(self.last_account_data)
        #Back
        elif result["menu"] == "Back":
            self.menu(self.last_account_data)
        #Change to: {account_name}
        else:
            #change to one of saved accounts
            #no longer account name but more stats make it better in future
            account_option = change_accounts_prompt["choices"].index(result["menu"])
            account = account_order_list[account_option]

            current_account_auth_data = self.auth.auth_account(cookies=self.account_config.accounts_data[account]["cookies"])
            if current_account_auth_data is None:
                self.log("Failed to auth account with cookies! (change accounts) ")
                print("Cookies are invalid or have expired! Please login again. (Cookies only stays for few days, don't know why :/)")
                self.account_config.remove_account(account)
                self.menu(self.last_account_data)
            else:
                #SWITCH TO ACCOUNT WITH OLD COOKIES NOT RENEWED
                self.account_config.switch_to_account(self.account_config.accounts_data[account])

                current_account_data = self.auth.get_account_data()


                #OVERRIDING ACCOUNT DATA ONLY (Cookies maybe shouldn't be renewed but rather used original data, we'll see) NOT BEING OVERRIDDEN NOW
                #Testing with saving cookies, now happens that vry says it is logged in but can't launch valorant because riot client is not logged in
                self.account_config.save_account_to_config(current_account_auth_data, current_account_data, save_cookies=True)
                self.menu(current_account_data)

    def menu(self, account_data):
        self.last_account_data = account_data
        if account_data is not None:
            menu_prompt = {
                "type": "list",
                "name": "menu",
                "message": "Please select optional features:",
                "choices": [
                    f"Logged in as {account_data.get('name')} | {account_data.get('rank')} | Level: {account_data.get('level')} | Battlepass {account_data.get('bp_level')}/55",
                    "Change accounts",
                    "Start Valorant"
                ],
            }
        else:
            print("Not logged in!")
            menu_prompt = {
                "type": "list",
                "name": "menu",
                "message": "Please select optional features:",
                "choices": [
                    "Log in.",
                ],
            }


        result = InquirerPy.prompt(menu_prompt)
        option = menu_prompt["choices"].index(result["menu"])
        if account_data != None:
            #Logged in as....
            if option == 0:
                self.start_valorant()
            #Change accounts
            elif option == 1:
                self.menu_change_accounts()
            #Start Valorant
            elif option == 2:
                self.start_valorant()
        else:
            #Not logged in
            if option == 0:
                self.menu_change_accounts()
            #Log in
            # elif option == 1:
                # self.menu_change_accounts()

    def start_menu(self):
        self.log("Starting menu...")
        self.account_config.get_riot_client_path()
        current_account_cookies = self.account_config.load_current_account_cookies()
        current_account_auth_data = self.auth.auth_account(cookies=current_account_cookies)
        if current_account_auth_data is not None:
            self.log("Authed with cookies!")
            current_account_data = self.auth.get_account_data()
            self.account_config.save_account_to_config(current_account_auth_data, current_account_data)
            self.log("Opening menu")
            self.menu(current_account_data)
        else:
            self.log("Failed to auth account with cookies! (start menu) ")
            self.menu(None)

    def _is_valorant_running(self):
        try:
            output = subprocess.check_output(
                ["tasklist", "/FI", "IMAGENAME eq VALORANT.exe"],
                creationflags=subprocess.CREATE_NO_WINDOW
            ).decode().lower()
            return "valorant.exe" in output
        except:
            return False

    def start_valorant(self):
        if self._is_valorant_running():
            self.log("Valorant is already running")
            return
        
        self.log("Starting Valorant...")
        self.account_config.get_riot_client_path()
        args = "--launch-product=valorant --launch-patchline=live"
        ctypes.windll.shell32.ShellExecuteW(
            None,
            "open",
            self.account_config.riot_client_path,
            args,
            None,
            1
        )

# if __name__ == "__main__":
    # from account_config import AccountConfig
    # from account_auth import AccountAuth
    # acc = AccountManager("a", AccountConfig, AccountAuth, NUMBERTORANKS)
    # acc.start_menu()
    # username = input("Username: ")
    # password = input("Password: ")
    # acc.add_account_with_user_pass_login(username, password)
