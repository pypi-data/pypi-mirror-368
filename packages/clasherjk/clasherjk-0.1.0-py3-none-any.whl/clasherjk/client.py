import httpx

class ClashAPI:
    """
    Simple Clash of Clans API wrapper using JK's public proxy.
    """

    def __init__(self, base_url: str = "https://proxy-8xxn9b5ke-jklildevs-projects.vercel.app/v1"):
        self.base_url = base_url.rstrip("/")

    def _get(self, endpoint: str):
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = httpx.get(url)
        response.raise_for_status()
        return response.json()

    def get_player(self, player_tag: str):
        """Get player info by tag."""
        return self._get(f"players/{player_tag.replace('#', '%23')}")

    def get_clan(self, clan_tag: str):
        """Get clan info by tag."""
        return self._get(f"clans/{clan_tag.replace('#', '%23')}")

    def get_clan_warlog(self, clan_tag: str):
        """Get clan war log."""
        return self._get(f"clans/{clan_tag.replace('#', '%23')}/warlog")

    def get_current_war(self, clan_tag: str):
        """Get current clan war details."""
        return self._get(f"clans/{clan_tag.replace('#', '%23')}/currentwar")