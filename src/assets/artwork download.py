import requests
import urllib

response = requests.get("https://playvalorant.com/page-data/en-us/agents/page-data.json")



for agent in response.json()["result"]["data"]["allContentstackAgentList"]["nodes"][0]["agent_list"]:
    urllib.request.urlretrieve(agent["agent_image"]["url"], agent["title"] + "Artwork.png")
    urllib.request.urlretrieve(agent["role_icon"]["url"], agent["role"] + ".png")