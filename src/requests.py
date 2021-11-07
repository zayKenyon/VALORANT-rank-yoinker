import requests
from colr import color



class Requests:
    def __init__(self, version):
        self.version = version

    def check_version(self):
        # checking status
        rStatus = requests.get(
            "https://raw.githubusercontent.com/isaacKenyon/VALORANT-rank-yoinker/main/status.json").json()
        if not rStatus["status_ok"] or rStatus["print_message"]:
            status_color = (255, 0, 0) if not rStatus["status_ok"] else (0, 255, 0)
            print(color(rStatus["message"], fore=status_color))

        # checking for latest release
        r = requests.get("https://api.github.com/repos/isaacKenyon/VALORANT-rank-yoinker/releases")
        json_data = r.json()
        release_version = json_data[0]["tag_name"]  # get release version
        link = json_data[0]["assets"][0]["browser_download_url"]  # link for the latest release

        if float(release_version) > float(self.version):
            print(f"New version available! {link}")

    def check_status(self):
        # checking status
        rStatus = requests.get(
            "https://raw.githubusercontent.com/isaacKenyon/VALORANT-rank-yoinker/main/status.json").json()
        if not rStatus["status_ok"] or rStatus["print_message"]:
            status_color = (255, 0, 0) if not rStatus["status_ok"] else (0, 255, 0)
            print(color(rStatus["message"], fore=status_color))