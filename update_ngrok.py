import json
import os
import re
import requests

SETTINGS_PATH = os.path.join('ecommerce', 'settings.py')  # adjust if needed

def get_ngrok_url():
    try:
        response = requests.get('http://127.0.0.1:4040/api/tunnels')
        tunnels = response.json()['tunnels']
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                return tunnel['public_url'].replace('https://', '')
    except Exception as e:
        print(f"Failed to get ngrok URL: {e}")
        return None

def update_settings(ngrok_host):
    with open(SETTINGS_PATH, 'r') as f:
        content = f.read()

    # Update ALLOWED_HOSTS
    content = re.sub(
        r"ALLOWED_HOSTS\s*=\s*\[([^\]]*)\]",
        lambda m: f"ALLOWED_HOSTS = [{m.group(1).strip()}, '{ngrok_host}']"
            if f"'{ngrok_host}'" not in m.group(1) else m.group(0),
        content
    )

    # Update CSRF_TRUSTED_ORIGINS
    csrf_origin = f"https://{ngrok_host}"
    content = re.sub(
        r"CSRF_TRUSTED_ORIGINS\s*=\s*\[([^\]]*)\]",
        lambda m: f"CSRF_TRUSTED_ORIGINS = [{m.group(1).strip()}, '{csrf_origin}']"
            if f"'{csrf_origin}'" not in m.group(1) else m.group(0),
        content
    )

    with open(SETTINGS_PATH, 'w') as f:
        f.write(content)

    print(f"✅ settings.py updated with: {ngrok_host}")

if __name__ == '__main__':
    url = get_ngrok_url()
    if url:
        update_settings(url)
    else:
        print("❌ Could not fetch Ngrok public URL.")
