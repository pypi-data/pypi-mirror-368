import requests

class Client:
    """
    Clash of Clans API client using a proxy.
    """
    def __init__(self, base_url="https://proxy-8xxn9b5ke-jklildevs-projects.vercel.app"):
        self.base_url = base_url.rstrip("/")

    def get_clan(self, clan_tag: str):
        """Fetch clan data by tag."""
        tag = clan_tag.replace("#", "%23")
        url = f"{self.base_url}/v1/clans/{tag}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_player(self, player_tag: str):
        """Fetch player data by tag."""
        tag = player_tag.replace("#", "%23")
        url = f"{self.base_url}/v1/players/{tag}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()