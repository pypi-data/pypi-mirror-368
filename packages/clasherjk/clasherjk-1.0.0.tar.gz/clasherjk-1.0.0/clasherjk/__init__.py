"""
ClasherJK - A Python library for Clash of Clans API

A simple and easy-to-use Python wrapper for the Clash of Clans API
using the clasherjk.vercel.app proxy server.

Example:
    from clasherjk import ClasherJK
    
    client = ClasherJK()
    player = client.get_player("#YCQ2PJGCJ")
    print(f"Player: {player.name} - Level: {player.exp_level}")
"""

from .client import ClasherJK
from .models import Player, Clan, League, War, ClanMember
from .exceptions import (
    ClasherJKException, 
    PlayerNotFound, 
    ClanNotFound, 
    InvalidTag, 
    RateLimitExceeded, 
    APIError
)

__version__ = "1.0.0"
__author__ = "ClasherJK"
__email__ = "your.email@example.com"

__all__ = [
    "ClasherJK", 
    "Player", 
    "Clan", 
    "League", 
    "War", 
    "ClanMember",
    "ClasherJKException", 
    "PlayerNotFound", 
    "ClanNotFound",
    "InvalidTag",
    "RateLimitExceeded", 
    "APIError"
]