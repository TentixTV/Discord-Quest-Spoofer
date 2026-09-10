"""
Preset Database of Known Discord Quest Games
Contains mappings of Application IDs, Executable Names, and Window Titles.
"""

QUEST_GAMES_DATABASE = {
    # Current Active Quests (Verified with Discord API & Detectable database)
    "1205090671527071784": {
        "name": "Helldivers 2",
        "exe": "bin/helldivers2.exe",
        "title": "HELLDIVERS™ 2",
        "category": "Shooter / Co-op"
    },
    "1437509662303059998": {
        "name": "Where Winds Meet",
        "exe": "where winds meet.exe",
        "title": "Where Winds Meet",
        "category": "Open World RPG"
    },
    "1461154307171811401": {
        "name": "Arknights: Endfield",
        "exe": "Endfield.exe",
        "title": "Arknights: Endfield",
        "category": "Action RPG"
    },
    "1512292746889662576": {
        "name": "Onimusha: Way of the Sword (Demo)",
        "exe": "onimushawots_demo.exe",
        "title": "Onimusha: Way of the Sword (Demo)",
        "category": "Action / Adventure"
    },
    "363445589247131668": {
        "name": "Iron Soul: Dungeon on Roblox",
        "exe": "RobloxPlayerBeta.exe",
        "title": "Roblox",
        "category": "Roblox"
    },
    "1456485028350656512": {
        "name": "CAPCOM TGS Deals",
        "exe": "capcom.exe",
        "title": "CAPCOM TGS Deals",
        "category": "Capcom Video"
    },
    # Backwards compatibility fallback IDs
    "1539692903037796422": {
        "name": "Onimusha: Way of the Sword (Demo)",
        "exe": "onimushawots_demo.exe",
        "title": "Onimusha: Way of the Sword (Demo)",
        "category": "Action / Adventure"
    },
    "1545079125243600947": {
        "name": "Iron Soul: Dungeon on Roblox",
        "exe": "RobloxPlayerBeta.exe",
        "title": "Roblox",
        "category": "Roblox"
    },
    
    # Popular Quest Games
    "868779904245645352": {
        "name": "Genshin Impact",
        "exe": "GenshinImpact.exe",
        "title": "Genshin Impact",
        "category": "Action RPG"
    },
    "1096001429871579176": {
        "name": "Honkai: Star Rail",
        "exe": "StarRail.exe",
        "title": "Honkai: Star Rail",
        "category": "Turn-based RPG"
    },
    "1257976823908958228": {
        "name": "Zenless Zone Zero",
        "exe": "ZenlessZoneZero.exe",
        "title": "Zenless Zone Zero",
        "category": "Action RPG"
    },
    "1231872101683953714": {
        "name": "Wuthering Waves",
        "exe": "Client-Win64-Shipping.exe",
        "title": "Wuthering Waves",
        "category": "Action RPG"
    },
    "432980957394370572": {
        "name": "Fortnite",
        "exe": "FortniteClient-Win64-Shipping.exe",
        "title": "Fortnite",
        "category": "Battle Royale"
    },
    "356860303649570817": {
        "name": "League of Legends",
        "exe": "LeagueClientUx.exe",
        "title": "League of Legends",
        "category": "MOBA"
    },
    "700143411477741648": {
        "name": "VALORANT",
        "exe": "VALORANT-Win64-Shipping.exe",
        "title": "VALORANT",
        "category": "Shooter"
    },
    "373249071537258496": {
        "name": "Warframe",
        "exe": "Warframe.x64.exe",
        "title": "Warframe",
        "category": "Co-op Action"
    },
    "545809756184182784": {
        "name": "Apex Legends",
        "exe": "r5apex.exe",
        "title": "Apex Legends",
        "category": "Battle Royale"
    },
    "356875221077622784": {
        "name": "World of Warcraft",
        "exe": "Wow.exe",
        "title": "World of Warcraft",
        "category": "MMORPG"
    },
    "1247940251768819772": {
        "name": "The First Descendant",
        "exe": "M1-Win64-Shipping.exe",
        "title": "The First Descendant",
        "category": "Looter Shooter"
    }
}

def resolve_game_info(app_id: str, fallback_name: str = "") -> dict:
    """Returns executable name and window title for an app_id, with smart fallback."""
    if app_id in QUEST_GAMES_DATABASE:
        return QUEST_GAMES_DATABASE[app_id]
    
    # Fallback based on name keywords
    clean_name = fallback_name.lower()
    exe = "Game.exe"
    if "roblox" in clean_name:
        exe = "RobloxPlayerBeta.exe"
    elif "helldivers" in clean_name:
        exe = "bin/helldivers2.exe"
    elif "genshin" in clean_name:
        exe = "GenshinImpact.exe"
    elif "star rail" in clean_name:
        exe = "StarRail.exe"
    elif "zenless" in clean_name:
        exe = "ZenlessZoneZero.exe"
    elif "endfield" in clean_name or "arknights" in clean_name:
        exe = "Endfield.exe"
    elif "winds meet" in clean_name:
        exe = "where winds meet.exe"
    elif "onimusha" in clean_name:
        exe = "onimushawots_demo.exe"
    else:
        # Create a plausible executable name from title
        sanitized = "".join(c for c in fallback_name if c.isalnum() or c in ("_", "-"))
        exe = f"{sanitized}.exe" if sanitized else "Game.exe"

    return {
        "name": fallback_name or "Unbekanntes Spiel",
        "exe": exe,
        "title": fallback_name or "Game Simulation",
        "category": "Custom Game"
    }
