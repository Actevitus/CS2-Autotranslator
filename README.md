# CS2 Chat Translator

A Python script that watches your Counter-Strike 2 (CS2) console log for in-game chat (all-chat and team-chat), translates each message to a target language, and forwards translations to a Discord webhook.

---

## Features

* Tail `console.log` in real time without injecting into the game process (VAC-safe).
* Detects both legacy (`say`/`say_team`) and new console formats (`[ALL]`, `[CT]`, `[T]`, etc.).
* Automatically translates via Google Translator (Deep-Translator).
* Posts translated chat to a Discord channel via webhook with `[ALL]`/`[CT]` tags.

---

## Requirements

* Python 3.7+
* Windows (tested on Windows 10/11)
* Access rights to read CS2’s `console.log` (may require Administrator).

### Python Packages

Install dependencies with pip:

```bash
pip install requests deep-translator
```

---

## Steam Launch Options

To enable verbose console logging in CS2, add the following to your game’s launch options in Steam:

1. Open Steam → Library → Right-click **Counter-Strike 2** → **Properties...**
2. In **General → Launch Options**, enter:

   ```text
   -console -condebug -conclearlog
   ```

* `-console`       → opens the developer console on start.
* `-condebug`      → writes all console output to `console.log`.
* `-conclearlog`   → clears previous logs on each launch.

---

## Locating `console.log`

After launching CS2 with the above options, the engine creates/updates:

```
C:\Program Files (x86)\Steam\steamapps\common\Counter-Strike 2\game\csgo\console.log
```

> **Tip:** If you prefer a different path, you can copy or symlink the file to a location you control (e.g., your Documents folder) and point the script there.

---

## Configuration

Create a `config.json` in the same folder as `cs2_chat_translator.py`:

```json
{
  "log_path": "C:/path/to/console.log",
  "target_language": "en",
  "discord_webhook_url": "https://discord.com/api/webhooks/your_webhook_id/your_token"
}
```

* **log\_path**: Full Windows path to `console.log`.
* **target\_language**: Two-letter ISO code (e.g., `en`, `de`, `fr`).
* **discord\_webhook\_url**: Your Discord incoming webhook URL.

---

## Running the Translator

1. Open a terminal (PowerShell or CMD) as Administrator (to ensure read access).
2. Navigate to the script folder:

   ```powershell
   cd C:\Path\To\CS2-Autotranslator
   ```
3. Launch the script:

   ```bash
   python cs2_chat_translator.py
   ```

You should see verbose output:

```
Loading configuration from config.json...
Configuration: log_path=...\console.log, target_language=en, webhook=...
GoogleTranslator initialized for target language 'en'.
Opening log file: ...\console.log
Watching for new lines...
[RAW] 07/02 17:35:36  [CT] Player: message in foreign language
[CHAT] [CT] Player: message in foreign language
[TRANSLATED] translation='translated message'
Sending to Discord -> [CT] Player: translated message
Discord webhook sent successfully.
```

---

## Troubleshooting

* **No chat lines appearing?**

  * Verify launch options are set correctly (`-condebug`).
  * Manually append a test line:

    ```powershell
    Add-Content "C:\Path\To\console.log" '"Tester<1><ALL><CT>" say "hello"
    ```
  * Check script output for `[RAW]` entries.

* **Permission errors**

  * Run terminal as Administrator or copy `console.log` to a user-writable directory and update `config.json`.

* **Discord webhook failures**

  * Ensure `discord_webhook_url` is valid and not expired.
  * Check Discord channel permissions for webhooks.

---

## License

MIT License. Feel free to fork and customize!
