"""Main client class for ClasherJK library."""

import httpx
from typing import List, Optional, Dict, Any
from urllib.parse import quote

from .models import Player, Clan, War, ClanMember, League, Location
from .exceptions import (
    ClasherJKException, 
    PlayerNotFound, 
    ClanNotFound, 
    InvalidTag, 
    RateLimitExceeded, 
    APIError
)
from .config import Config


class ClasherJK:
    """
    Main client for interacting with Clash of Clans API through clasherjk.vercel.app proxy.
    
    No authentication required - all requests go through the proxy server.
    
    Example:
        client = ClasherJK()
        player = client.get_player("#YCQ2PJGCJ")
        print(f"Player: {player.name}")
    """
    
    def __init__(self, base_url: str = None):
        """
        Initialize the ClasherJK client.
        
        Args:
            base_url: Custom proxy URL (optional, uses secure default proxy)
        """
        # Get proxy URL using configuration system
        self.base_url = Config.get_proxy_url(base_url).rstrip('/')
        self._client = httpx.Client(timeout=30.0)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        self._client.close()
    
    def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """
        Make a request to the proxy API.
        
        Args:
            endpoint: API endpoint (e.g., "v1/players/%23YCQ2PJGCJ")
            
        Returns:
            JSON response as dictionary
            
        Raises:
            APIError: If the request fails
            RateLimitExceeded: If rate limit is exceeded
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self._client.get(url)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise APIError(404, "Resource not found")
            elif response.status_code == 429:
                raise RateLimitExceeded()
            else:
                raise APIError(response.status_code, response.text)
                
        except httpx.RequestError as e:
            raise ClasherJKException(f"Request failed: {str(e)}")
    
    @staticmethod
    def _format_tag(tag: str) -> str:
        """
        Format a player/clan tag for API requests.
        
        Args:
            tag: Player or clan tag (with or without #)
            
        Returns:
            Properly formatted tag for URL
        """
        if not tag:
            raise InvalidTag(tag)
            
        # Remove # if present, then add %23 for URL encoding
        clean_tag = tag.lstrip('#').upper()
        if not clean_tag:
            raise InvalidTag(tag)
            
        return f"%23{clean_tag}"
    
    # Player Methods
    def get_player(self, player_tag: str) -> Player:
        """
        Get player information by tag.
        
        Args:
            player_tag: Player tag (e.g., "#YCQ2PJGCJ" or "YCQ2PJGCJ")
            
        Returns:
            Player object with all player information
            
        Raises:
            PlayerNotFound: If player doesn't exist
            InvalidTag: If tag format is invalid
        """
        formatted_tag = self._format_tag(player_tag)
        
        try:
            data = self._make_request(f"v1/players/{formatted_tag}")
            return Player.from_dict(data)
        except APIError as e:
            if e.status_code == 404:
                raise PlayerNotFound(player_tag)
            raise
    
    # Clan Methods
    def get_clan(self, clan_tag: str) -> Clan:
        """
        Get clan information by tag.
        
        Args:
            clan_tag: Clan tag (e.g., "#2PP" or "2PP")
            
        Returns:
            Clan object with all clan information
            
        Raises:
            ClanNotFound: If clan doesn't exist
            InvalidTag: If tag format is invalid
        """
        formatted_tag = self._format_tag(clan_tag)
        
        try:
            data = self._make_request(f"v1/clans/{formatted_tag}")
            return Clan.from_dict(data)
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    def get_clan_members(self, clan_tag: str) -> List[ClanMember]:
        """
        Get clan members by clan tag.
        
        Args:
            clan_tag: Clan tag (e.g., "#2PP" or "2PP")
            
        Returns:
            List of ClanMember objects
        """
        formatted_tag = self._format_tag(clan_tag)
        
        try:
            data = self._make_request(f"v1/clans/{formatted_tag}/members")
            return [ClanMember.from_dict(member) for member in data.get('items', [])]
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    def get_clan_war(self, clan_tag: str) -> War:
        """
        Get current war information for a clan.
        
        Args:
            clan_tag: Clan tag (e.g., "#2PP" or "2PP")
            
        Returns:
            War object with current war information
        """
        formatted_tag = self._format_tag(clan_tag)
        
        try:
            data = self._make_request(f"v1/clans/{formatted_tag}/currentwar")
            return War.from_dict(data)
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    def get_clan_warlog(self, clan_tag: str, limit: Optional[int] = None) -> List[War]:
        """
        Get clan war log.
        
        Args:
            clan_tag: Clan tag (e.g., "#2PP" or "2PP")
            limit: Maximum number of wars to return
            
        Returns:
            List of War objects from war log
        """
        formatted_tag = self._format_tag(clan_tag)
        endpoint = f"v1/clans/{formatted_tag}/warlog"
        
        if limit:
            endpoint += f"?limit={limit}"
        
        try:
            data = self._make_request(endpoint)
            return [War.from_dict(war) for war in data.get('items', [])]
        except APIError as e:
            if e.status_code == 404:
                raise ClanNotFound(clan_tag)
            raise
    
    # Search Methods
    def search_clans(self, 
                    name: Optional[str] = None,
                    war_frequency: Optional[str] = None,
                    location_id: Optional[int] = None,
                    min_members: Optional[int] = None,
                    max_members: Optional[int] = None,
                    min_clan_points: Optional[int] = None,
                    min_clan_level: Optional[int] = None,
                    limit: Optional[int] = None) -> List[Clan]:
        """
        Search for clans.
        
        Args:
            name: Clan name to search for
            war_frequency: War frequency filter
            location_id: Location ID filter
            min_members: Minimum number of members
            max_members: Maximum number of members
            min_clan_points: Minimum clan points
            min_clan_level: Minimum clan level
            limit: Maximum number of results
            
        Returns:
            List of Clan objects matching the search criteria
        """
        params = []
        
        if name:
            params.append(f"name={quote(name)}")
        if war_frequency:
            params.append(f"warFrequency={war_frequency}")
        if location_id:
            params.append(f"locationId={location_id}")
        if min_members:
            params.append(f"minMembers={min_members}")
        if max_members:
            params.append(f"maxMembers={max_members}")
        if min_clan_points:
            params.append(f"minClanPoints={min_clan_points}")
        if min_clan_level:
            params.append(f"minClanLevel={min_clan_level}")
        if limit:
            params.append(f"limit={limit}")
        
        endpoint = "v1/clans"
        if params:
            endpoint += "?" + "&".join(params)
        
        data = self._make_request(endpoint)
        return [Clan.from_dict(clan) for clan in data.get('items', [])]
    
    # League Methods
    def get_leagues(self) -> List[League]:
        """
        Get all leagues.
        
        Returns:
            List of League objects
        """
        data = self._make_request("v1/leagues")
        return [League.from_dict(league) for league in data.get('items', [])]
    
    def get_league_seasons(self, league_id: int) -> List[Dict[str, Any]]:
        """
        Get league seasons for a specific league.
        
        Args:
            league_id: League ID
            
        Returns:
            List of season information
        """
        data = self._make_request(f"v1/leagues/{league_id}/seasons")
        return data.get('items', [])
    
    def get_league_season_rankings(self, league_id: int, season_id: str, limit: Optional[int] = None) -> List[Player]:
        """
        Get player rankings for a league season.
        
        Args:
            league_id: League ID
            season_id: Season ID
            limit: Maximum number of results
            
        Returns:
            List of Player objects with ranking information
        """
        endpoint = f"v1/leagues/{league_id}/seasons/{season_id}"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Player.from_dict(player) for player in data.get('items', [])]
    
    # Location Methods
    def get_locations(self) -> List[Location]:
        """
        Get all locations.
        
        Returns:
            List of Location objects
        """
        data = self._make_request("v1/locations")
        return [Location.from_dict(location) for location in data.get('items', [])]
    
    def get_location_clan_rankings(self, location_id: int, limit: Optional[int] = None) -> List[Clan]:
        """
        Get clan rankings for a location.
        
        Args:
            location_id: Location ID
            limit: Maximum number of results
            
        Returns:
            List of Clan objects with ranking information
        """
        endpoint = f"v1/locations/{location_id}/rankings/clans"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Clan.from_dict(clan) for clan in data.get('items', [])]
    
    def get_location_player_rankings(self, location_id: int, limit: Optional[int] = None) -> List[Player]:
        """
        Get player rankings for a location.
        
        Args:
            location_id: Location ID
            limit: Maximum number of results
            
        Returns:
            List of Player objects with ranking information
        """
        endpoint = f"v1/locations/{location_id}/rankings/players"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Player.from_dict(player) for player in data.get('items', [])]
    
    # Global Rankings
    def get_global_player_rankings(self, limit: Optional[int] = None) -> List[Player]:
        """
        Get global player rankings.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of Player objects with global ranking information
        """
        endpoint = "v1/locations/global/rankings/players"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Player.from_dict(player) for player in data.get('items', [])]
    
    def get_global_clan_rankings(self, limit: Optional[int] = None) -> List[Clan]:
        """
        Get global clan rankings.
        
        Args:
            limit: Maximum number of results
            
        Returns:
            List of Clan objects with global ranking information
        """
        endpoint = "v1/locations/global/rankings/clans"
        if limit:
            endpoint += f"?limit={limit}"
        
        data = self._make_request(endpoint)
        return [Clan.from_dict(clan) for clan in data.get('items', [])]