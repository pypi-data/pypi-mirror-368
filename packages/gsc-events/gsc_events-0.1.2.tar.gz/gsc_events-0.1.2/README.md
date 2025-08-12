# GSC Events for Plutonium T6

A GSC script and Python library for capturing and handling game events in Plutonium T6 (Call of Duty: Black Ops 2).

## Features

- Captures various in-game events and saves them to JSONL files
- Python library to read and process these events in real-time
- Supports the following events:
  - Player Connected/Disconnected
  - Player Spawned/Death
  - Player Killed (with killer and weapon information)
  - Player Chat Messages
  - Killcam Start/End

## Installation

### Option 1: From GitHub Repository
#### 1. Clone the repository:
```bash
git clone https://github.com/Yallamaztar/gsc-events.git
```

### Option 2: Direct Installation
#### 1. Copy `gsc-events.gsc` to your Plutonium T6 scripts folder:
```
%localappdata%\Plutonium\storage\t6\scripts\
```

#### 2. Install the Python package:
```bash
pip install gsc-events
```

## Event Format

Events are stored in JSONL format (one JSON object per line) in separate files for each event type. For example:

```jsonl
{ "event": "player_connected", "args": ["PlayerName"] }
{ "event": "player_say", "args": ["PlayerName", "message"] }
{ "event": "player_killed", "args": ["VictimName", "KillerName", "WeaponName"] }
```

## Python Usage

```python
from gsc_events import GSCClient

client = GSCClient()

@client.on("player_connected")
def on_connected(player: str) -> None:
    print(f"{player} Connected")

@client.on("player_spawned")
def on_spawned(player: str) -> None:
    print(f"{player} Spawned")

@client.on("player_death")
def on_death(player: str) -> None:
    print(f"{player} Died")

@client.on("player_killed")
def on_killed(player: str, attacker: str, reason: str) -> None:
    print(f"{player} was killed by {attacker} with {reason}")

@client.on("player_disconnect")
def on_disconnect() -> None:
    print(f"player Disconnected")

@client.on("player_say")
def on_say(player: str, message: str) -> None:
    print(f"{player} said {message}")

@client.on("killcam")
def on_killcam() -> None:
    print(f"Killcam started")

@client.on("killcam_end")
def on_killcam_end() -> None:
    print(f"Killcam ended")

client.run()
```

## Events Reference

| Event Name | Arguments | Description |
|------------|-----------|-------------|
| player_connected | player_name | Triggered when a player connects |
| player_disconnected | none | Triggered when a player disconnects |
| player_spawned | player_name | Triggered when a player spawns |
| player_death | player_name | Triggered when a player dies |
| player_killed | victim_name, killer_name, weapon | Triggered when a player is killed by another player |
| player_say | player_name, message | Triggered when a player sends a chat message |
| killcam | none | Triggered when final killcam starts |
| killcam_end | none | Triggered when final killcam ends |

----
