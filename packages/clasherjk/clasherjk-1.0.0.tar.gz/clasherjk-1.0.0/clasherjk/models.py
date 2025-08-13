"""Data models for Clash of Clans entities."""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime


@dataclass
class League:
    """Represents a player's league information."""
    id: int
    name: str
    icon_urls: Dict[str, str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'League':
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            icon_urls=data.get('iconUrls', {})
        )


@dataclass
class Achievement:
    """Represents a player achievement."""
    name: str
    stars: int
    value: int
    target: int
    info: str
    completion_info: Optional[str]
    village: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        return cls(
            name=data.get('name', ''),
            stars=data.get('stars', 0),
            value=data.get('value', 0),
            target=data.get('target', 0),
            info=data.get('info', ''),
            completion_info=data.get('completionInfo'),
            village=data.get('village', '')
        )


@dataclass
class Troop:
    """Represents a troop (army unit)."""
    name: str
    level: int
    max_level: int
    village: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Troop':
        return cls(
            name=data.get('name', ''),
            level=data.get('level', 0),
            max_level=data.get('maxLevel', 0),
            village=data.get('village', '')
        )


@dataclass
class Hero:
    """Represents a hero unit."""
    name: str
    level: int
    max_level: int
    village: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Hero':
        return cls(
            name=data.get('name', ''),
            level=data.get('level', 0),
            max_level=data.get('maxLevel', 0),
            village=data.get('village', '')
        )


@dataclass
class Spell:
    """Represents a spell."""
    name: str
    level: int
    max_level: int
    village: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Spell':
        return cls(
            name=data.get('name', ''),
            level=data.get('level', 0),
            max_level=data.get('maxLevel', 0),
            village=data.get('village', '')
        )


@dataclass
class Player:
    """Represents a Clash of Clans player."""
    tag: str
    name: str
    town_hall_level: int
    town_hall_weapon_level: Optional[int]
    exp_level: int
    trophies: int
    best_trophies: int
    war_stars: int
    attack_wins: int
    defense_wins: int
    builder_hall_level: Optional[int]
    builder_base_trophies: Optional[int]
    best_builder_base_trophies: Optional[int]
    role: Optional[str]
    clan_capital_contributions: Optional[int]
    clan: Optional[Dict[str, Any]]
    league: Optional[League]
    achievements: List[Achievement]
    versus_trophies: Optional[int]
    versus_battle_wins: Optional[int]
    clan_tag: Optional[str]
    troops: List[Troop]
    heroes: List[Hero]
    spells: List[Spell]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Create a Player instance from API response data."""
        return cls(
            tag=data.get('tag', ''),
            name=data.get('name', ''),
            town_hall_level=data.get('townHallLevel', 0),
            town_hall_weapon_level=data.get('townHallWeaponLevel'),
            exp_level=data.get('expLevel', 0),
            trophies=data.get('trophies', 0),
            best_trophies=data.get('bestTrophies', 0),
            war_stars=data.get('warStars', 0),
            attack_wins=data.get('attackWins', 0),
            defense_wins=data.get('defenseWins', 0),
            builder_hall_level=data.get('builderHallLevel'),
            builder_base_trophies=data.get('builderBaseTrophies'),
            best_builder_base_trophies=data.get('bestBuilderBaseTrophies'),
            role=data.get('role'),
            clan_capital_contributions=data.get('clanCapitalContributions'),
            clan=data.get('clan'),
            league=League.from_dict(data['league']) if data.get('league') else None,
            achievements=[Achievement.from_dict(a) for a in data.get('achievements', [])],
            versus_trophies=data.get('versusTrophies'),
            versus_battle_wins=data.get('versusBattleWins'),
            clan_tag=data.get('clan', {}).get('tag') if data.get('clan') else None,
            troops=[Troop.from_dict(t) for t in data.get('troops', [])],
            heroes=[Hero.from_dict(h) for h in data.get('heroes', [])],
            spells=[Spell.from_dict(s) for s in data.get('spells', [])]
        )


@dataclass
class ClanMember:
    """Represents a clan member."""
    tag: str
    name: str
    role: str
    exp_level: int
    league: Optional[League]
    trophies: int
    versus_trophies: Optional[int]
    clan_rank: int
    previous_clan_rank: int
    donations: int
    donations_received: int

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClanMember':
        return cls(
            tag=data.get('tag', ''),
            name=data.get('name', ''),
            role=data.get('role', ''),
            exp_level=data.get('expLevel', 0),
            league=League.from_dict(data['league']) if data.get('league') else None,
            trophies=data.get('trophies', 0),
            versus_trophies=data.get('versusTrophies'),
            clan_rank=data.get('clanRank', 0),
            previous_clan_rank=data.get('previousClanRank', 0),
            donations=data.get('donations', 0),
            donations_received=data.get('donationsReceived', 0)
        )


@dataclass
class Clan:
    """Represents a Clash of Clans clan."""
    tag: str
    name: str
    type: str
    description: str
    location: Optional[Dict[str, Any]]
    badge_urls: Dict[str, str]
    clan_level: int
    clan_points: int
    clan_versus_points: int
    clan_capital_points: int
    required_trophies: int
    war_frequency: str
    war_win_streak: int
    war_wins: int
    war_ties: Optional[int]
    war_losses: Optional[int]
    is_war_log_public: bool
    war_league: Optional[Dict[str, Any]]
    members: int
    member_list: List[ClanMember]
    labels: List[Dict[str, Any]]
    capital_league: Optional[Dict[str, Any]]
    chat_language: Optional[Dict[str, Any]]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Clan':
        """Create a Clan instance from API response data."""
        return cls(
            tag=data.get('tag', ''),
            name=data.get('name', ''),
            type=data.get('type', ''),
            description=data.get('description', ''),
            location=data.get('location'),
            badge_urls=data.get('badgeUrls', {}),
            clan_level=data.get('clanLevel', 0),
            clan_points=data.get('clanPoints', 0),
            clan_versus_points=data.get('clanVersusPoints', 0),
            clan_capital_points=data.get('clanCapitalPoints', 0),
            required_trophies=data.get('requiredTrophies', 0),
            war_frequency=data.get('warFrequency', ''),
            war_win_streak=data.get('warWinStreak', 0),
            war_wins=data.get('warWins', 0),
            war_ties=data.get('warTies'),
            war_losses=data.get('warLosses'),
            is_war_log_public=data.get('isWarLogPublic', False),
            war_league=data.get('warLeague'),
            members=data.get('members', 0),
            member_list=[ClanMember.from_dict(m) for m in data.get('memberList', [])],
            labels=data.get('labels', []),
            capital_league=data.get('capitalLeague'),
            chat_language=data.get('chatLanguage')
        )


@dataclass
class War:
    """Represents a clan war."""
    state: str
    team_size: int
    preparation_start_time: str
    start_time: str
    end_time: str
    clan: Dict[str, Any]
    opponent: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'War':
        return cls(
            state=data.get('state', ''),
            team_size=data.get('teamSize', 0),
            preparation_start_time=data.get('preparationStartTime', ''),
            start_time=data.get('startTime', ''),
            end_time=data.get('endTime', ''),
            clan=data.get('clan', {}),
            opponent=data.get('opponent', {})
        )


@dataclass
class Location:
    """Represents a location/country."""
    id: int
    name: str
    is_country: bool
    country_code: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        return cls(
            id=data.get('id', 0),
            name=data.get('name', ''),
            is_country=data.get('isCountry', False),
            country_code=data.get('countryCode')
        )