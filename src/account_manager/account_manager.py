import InquirerPy, subprocess, re

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
    def __init__(self, log, account_config, auth, NUMBERTORANKS):
        self.log = log
        self.auth = auth(log, NUMBERTORANKS)
        self.account_config = account_config(log)



    def escape_ansi(self, line):
        ansi_escape = re.compile(r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]')
        return ansi_escape.sub('', line)

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
                "Add account with username & password",
                "Add account by signing into riot client"
            ],
        }

        self.account_config.load_accounts_config()
        for account in self.account_config.accounts_data:
            change_accounts_prompt["choices"].append("Change to: " + self.account_config.accounts_data[account]["name"])
        change_accounts_prompt["choices"].append("Add new account")
        result = InquirerPy.prompt(change_accounts_prompt)
        #Add new account
        if result["menu"] == "Add new account":
            result = InquirerPy.prompt(add_account_prompt)
            option = add_account_prompt["choices"].index(result["menu"])
            #Add account with username & password
            if option == 0:
                username = InquirerPy.text(message="Username:").execute()
                password = InquirerPy.password(message="Password:").execute()
                self.auth.auth_account(username=username, password=password)
            #Add account by signing into riot client
            elif option == 1:
                self.account_config.add_account_with_client()
        #Change to: {account_name}
        else:
            #change to one of saved accounts
            account_name = result["menu"].split("Change to: ")[1]
            for account in self.accounts_data:
                if self.account_config.accounts_data[account]["name"] == account_name:
                    #better way of doing this?
                    self.account_config.switch_to_account(self.account_config.accounts_data[account])

                    current_account_auth_data = self.auth.auth_account(cookies=self.accounts_data[account]["cookies"])
                    current_account_data = self.auth.get_account_data()
                    self.account_config.save_account_to_config(current_account_auth_data, current_account_data)
                    self.menu(current_account_data)

    def menu(self, account_data):
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
            self.save_account_to_config(current_account_auth_data, current_account_data)
            self.menu(current_account_data)
        else:
            self.menu(None)

    def start_valorant(self):
        subprocess.Popen([self.riot_client_path, "--launch-product=valorant", "--launch-patchline=live"])

if __name__ == "__main__":
    from account_config import AccountConfig
    from account_auth import AccountAuth
    print(AccountAuth)
    acc = AccountManager("a", AccountConfig, AccountAuth, NUMBERTORANKS)
    acc.start_menu()
    # username = input("Username: ")
    # password = input("Password: ")
    # acc.add_account_with_user_pass_login(username, password)
