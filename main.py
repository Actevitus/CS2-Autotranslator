import json
import time
import re
import requests
import os
import sys
from deep_translator import GoogleTranslator

#Patterns for legacy and new CS2 chat formats
legacy_pattern = re.compile(
    r'^"(?P<player>.+?)<\d+><[^>]+><[^>]+>"\s+say(_team)?\s+"(?P<msg>.+)"$'
)
new_pattern = re.compile(
    r'^\d{2}/\d{2} \d{2}:\d{2}:\d{2}\s+\[(?P<scope>ALL|TEAM|A|T|CT)\]\s*'
    r'(?P<player>[^:]+):\s*(?P<msg>.+)$',
    re.IGNORECASE
)


def load_config(path='config.json'):
    print(f"Loading configuration from {path}...")
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(1)
    with open(path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    for key in ('log_path', 'target_language', 'discord_webhook_url'):
        if key not in config:
            print(f"Missing '{key}' in config.json")
            sys.exit(1)
    print(
        f"Configuration: log_path={config['log_path']}, "
        f"target_language={config['target_language']}, webhook={config['discord_webhook_url']}"
    )
    return config


def follow_file(path):
    print(f"Opening log file: {path}")
    try:
        f = open(path, 'r', encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"Error opening file: {e}")
        sys.exit(1)
    f.seek(0, 2)
    print("Watching for new lines...")
    while True:
        line = f.readline()
        if not line:
            time.sleep(0.1)
            continue
        yield line.rstrip("\n")


def parse_chat_line(line):
    #Legacy format: "Player<...>" say or say_team "msg"
    m = legacy_pattern.match(line)
    if m:
        player = m.group('player')
        msg = m.group('msg')
        raw_scope = 'TEAM' if '_team' in line else 'ALL'
        return raw_scope, player, msg

    #New format: "MM/DD HH:MM:SS  [SCOPE] player: msg"
    m = new_pattern.match(line)
    if m:
        raw_scope = m.group('scope').upper()
        player = m.group('player').strip()
        msg = m.group('msg').strip()
        return raw_scope, player, msg
    return None


def send_to_discord(webhook_url, raw_scope, player, translated_text):
    prefix = f"[{raw_scope}]"
    payload = {'content': f"{prefix} **{player}**: {translated_text}"}
    print(f"Sending to Discord -> {prefix} {player}: {translated_text}")
    try:
        resp = requests.post(webhook_url, json=payload)
        resp.raise_for_status()
        print("Discord webhook sent successfully.")
    except Exception as e:
        print(f"Discord send error: {e} | status: {getattr(resp, 'status_code', 'N/A')} | response: {getattr(resp, 'text', '')}")


def main():
    config      = load_config()
    log_path    = config['log_path']
    target_lang = config['target_language']
    webhook     = config['discord_webhook_url']

    #Initialize GoogleTranslator (Deep-Translator)
    translator = GoogleTranslator(source='auto', target=target_lang)
    print(f"GoogleTranslator initialized for target language '{target_lang}'.")

    for raw in follow_file(log_path):
        print(f"[RAW] {raw}")
        parsed = parse_chat_line(raw)
        if not parsed:
            continue
        raw_scope, player, msg = parsed
        print(f"[CHAT] [{raw_scope}] {player}: {msg}")

        try:
            translated = translator.translate(msg)
            print(f"[TRANSLATED] translation='{translated}'")
        except Exception as e:
            print(f"Translate error: {e}")
            continue

        send_to_discord(webhook, raw_scope, player, translated)

if __name__ == '__main__':
    main()
