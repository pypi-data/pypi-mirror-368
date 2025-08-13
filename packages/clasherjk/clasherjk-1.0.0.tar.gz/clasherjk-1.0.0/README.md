# ClasherJK Python Library

[![PyPI version](https://badge.fury.io/py/clasherjk.svg)](https://badge.fury.io/py/clasherjk)
[![Python Versions](https://img.shields.io/pypi/pyversions/clasherjk.svg)](https://pypi.org/project/clasherjk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple and easy-to-use Python wrapper for the Clash of Clans API using a secure proxy server. 

**No API token required!** All requests are handled through our secure proxy server, making it incredibly easy to get started with Clash of Clans data.

## Installation

```bash
pip install clasherjk
```

## Quick Start

```python
from clasherjk import ClasherJK

# Create client (no authentication needed!)
client = ClasherJK()

# Get player information
player = client.get_player("#YCQ2PJGCJ")
print(f"Player: {player.name}")
print(f"Level: {player.exp_level}")
print(f"Trophies: {player.trophies}")
print(f"Town Hall: {player.town_hall_level}")

# Get clan information
clan = client.get_clan("#2PP")
print(f"Clan: {clan.name}")
print(f"Members: {clan.members}")
print(f"Clan Level: {clan.clan_level}")

# Close the client
client.close()
```

## Usage Examples

### Player Information

```python
from clasherjk import ClasherJK

with ClasherJK() as client:
    player = client.get_player("#YCQ2PJGCJ")
    
    print(f"Player: {player.name}")
    print(f"Level: {player.exp_level}")
    print(f"Trophies: {player.trophies}")
    print(f"Town Hall Level: {player.town_hall_level}")
    
    # League information
    if player.league:
        print(f"League: {player.league.name}")
    
    # Troops information
    for troop in player.troops[:5]:  # Show first 5 troops
        print(f"{troop.name}: Level {troop.level}")
```

### Clan Information

```python
from clasherjk import ClasherJK

with ClasherJK() as client:
    clan = client.get_clan("#2PP")
    
    print(f"Clan: {clan.name}")
    print(f"Level: {clan.clan_level}")
    print(f"Members: {clan.members}/50")
    print(f"War Wins: {clan.war_wins}")
    
    # Get clan members
    for member in clan.member_list[:5]:  # Show first 5 members
        print(f"{member.name}: {member.trophies} trophies ({member.role})")
```

### Search and Rankings

```python
from clasherjk import ClasherJK

with ClasherJK() as client:
    # Search for clans
    clans = client.search_clans(name="dragons", min_members=40, limit=3)
    for clan in clans:
        print(f"{clan.name}: {clan.members} members")
    
    # Global rankings
    top_players = client.get_global_player_rankings(limit=5)
    for i, player in enumerate(top_players, 1):
        print(f"#{i} {player.name}: {player.trophies:,} trophies")
```

## Requirements

- Python 3.7+
- httpx >= 0.24.0 (automatically installed)

## API Reference

### Main Client

- `ClasherJK()` - Initialize client
- `get_player(tag)` - Get player by tag
- `get_clan(tag)` - Get clan by tag
- `search_clans(**filters)` - Search for clans
- `get_global_player_rankings(limit=None)` - Global player rankings
- `get_global_clan_rankings(limit=None)` - Global clan rankings

### Data Models

- **Player** - Complete player information
- **Clan** - Complete clan information  
- **ClanMember** - Individual clan member
- **League** - League information
- **War** - War information

### Exception Handling

```python
from clasherjk import ClasherJK, PlayerNotFound, ClanNotFound

with ClasherJK() as client:
    try:
        player = client.get_player("#INVALID")
    except PlayerNotFound:
        print("Player not found!")
    except Exception as e:
        print(f"API Error: {e}")
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Issues and pull requests are welcome on GitHub.

---

**Made for the Clash of Clans community** ⚔️