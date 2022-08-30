import InquirerPy, subprocess, re
from InquirerPy import inquirer

#temporary until it is implemented in main
from colr import color
NUMBERTORANKS = [
            color('Unranked', fore=(46, 46, 46)),
            color('Unranked', fore=(46, 46, 46)),
            color('Unranked', fore=(46, 46, 46)),
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
            color('Ascendant 1', fore=(24, 148, 82)),
            color('Ascendant 2', fore=(24, 148, 82)),
            color('Ascendant 3', fore=(24, 148, 82)),
            color('Immortal 1', fore=(221, 68, 68)),
            color('Immortal 2', fore=(221, 68, 68)),
            color('Immortal 3', fore=(221, 68, 68)),
            color('Radiant', fore=(255, 253, 205)),
        ]


class AccountManager:
    def __init__(self, log, AccountConfig, AccountAuth, NUMBERTORANKS):
        self.log = log
        self.account_config = AccountConfig(log)
        self.auth = AccountAuth(log, NUMBERTORANKS)
        self.last_account_data = None



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
                "Add account with username & password. (MFA/2FA not supported yet)",
                "Add account by signing into riot client."
            ],
        }

        self.account_config.load_accounts_config()
        account_order_list = []
        for account in self.account_config.accounts_data:
            account_order_list.append(account)
            change_accounts_prompt["choices"].append(f"Change to: {self.account_config.accounts_data[account]['name']:<16}  | {self.account_config.accounts_data[account].get('rank'):<12} | Level: {self.account_config.accounts_data[account].get('level'):<4} | Battlepass {self.account_config.accounts_data[account].get('bp_level'):<2}/55")
        change_accounts_prompt["choices"].append("Add new account")
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
        #Change to: {account_name}
        else:
            #change to one of saved accounts
            #no longer account name but more stats make it better in future
            account_option = change_accounts_prompt["choices"].index(result["menu"])
            account = account_order_list[account_option]
            #SWITCH TO ACCOUNT WITH OLD COOKIES NOT RENEWED
            self.account_config.switch_to_account(self.account_config.accounts_data[account])

            current_account_auth_data = self.auth.auth_account(cookies=self.account_config.accounts_data[account]["cookies"])
            current_account_data = self.auth.get_account_data()
            #OVERRIDING ACCOUNT DATA ONLY (Cookies maybe shouldn't be renewed but rather used original data, we'll see) NOT BEING OVERRIDDEN NOW
            self.account_config.save_account_to_config(current_account_auth_data, current_account_data, save_cookies=False)
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
            menu_prompt = {
                "type": "list",
                "name": "menu",
                "message": "Please select optional features:",
                "choices": [
                    "Not logged in",
                    "Log in",
                ],
            }


        result = InquirerPy.prompt(menu_prompt)
        option = menu_prompt["choices"].index(result["menu"])
        if account_data != None:
            #Logged in as....
            if option == 0:
                pass
            #Change accounts
            elif option == 1:
                self.menu_change_accounts()
            #Start Valorant
            elif option == 2:
                self.start_valorant()
        else:
            #Not logged in
            if option == 0:
                pass
            #Log in
            elif option == 1:
                self.menu_change_accounts()

    def start_menu(self):
        self.account_config.get_riot_client_path()
        current_account_cookies = self.account_config.load_current_account_cookies()
        current_account_auth_data = self.auth.auth_account(cookies=current_account_cookies)
        if current_account_auth_data is not None:
            current_account_data = self.auth.get_account_data()
            self.account_config.save_account_to_config(current_account_auth_data, current_account_data)
            self.menu(current_account_data)
        else:
            self.menu(None)

    def start_valorant(self):
        subprocess.Popen([self.account_config.riot_client_path, "--launch-product=valorant", "--launch-patchline=live"])

if __name__ == "__main__":
    from account_config import AccountConfig
    from account_auth import AccountAuth
    acc = AccountManager("a", AccountConfig, AccountAuth, NUMBERTORANKS)
    acc.start_menu()
    # username = input("Username: ")
    # password = input("Password: ")
    # acc.add_account_with_user_pass_login(username, password)
