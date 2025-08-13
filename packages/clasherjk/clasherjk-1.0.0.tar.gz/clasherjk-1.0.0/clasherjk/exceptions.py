"""Custom exceptions for ClasherJK library."""


class ClasherJKException(Exception):
    """Base exception for ClasherJK library."""
    pass


class PlayerNotFound(ClasherJKException):
    """Raised when a player is not found."""
    def __init__(self, player_tag: str):
        super().__init__(f"Player with tag '{player_tag}' not found")
        self.player_tag = player_tag


class ClanNotFound(ClasherJKException):
    """Raised when a clan is not found."""
    def __init__(self, clan_tag: str):
        super().__init__(f"Clan with tag '{clan_tag}' not found")
        self.clan_tag = clan_tag


class InvalidTag(ClasherJKException):
    """Raised when an invalid tag is provided."""
    def __init__(self, tag: str):
        super().__init__(f"Invalid tag format: '{tag}'")
        self.tag = tag


class RateLimitExceeded(ClasherJKException):
    """Raised when API rate limit is exceeded."""
    def __init__(self):
        super().__init__("API rate limit exceeded. Please try again later.")


class APIError(ClasherJKException):
    """Raised when the API returns an error."""
    def __init__(self, status_code: int, message: str):
        super().__init__(f"API Error {status_code}: {message}")
        self.status_code = status_code
        self.message = message