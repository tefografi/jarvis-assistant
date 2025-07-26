Jarvis Personal Assistant
========================

This repository contains `jarvis.py`, a simple personal assistant for Windows
that you can control with your voice or via Telegram.  It is intended as a
starting point for your own "Jarvis" and illustrates how to combine
speech recognition, text‑to‑speech, and remote control.

> **Note:** This project is provided for educational purposes.  It does not
> support every possible feature and should be customised to your own needs.

Features
--------

* **Offline text‑to‑speech** using `pyttsx3`.  The library is cross‑platform
  and works offline because it uses the built‑in SAPI5 voices on Windows or
  eSpeak on Linux【933519646353299†L63-L73】.
* **Voice recognition** with `SpeechRecognition`.  The default recogniser
  sends audio to Google’s free API, but you can switch to an offline engine if
  you prefer【933519646353299†L78-L83】.
* **Command handling** for basic tasks such as telling the time or date,
  opening Notepad, launching web sites, and reading short Wikipedia
  summaries【933519646353299†L144-L189】.
* **Optional Telegram integration**.  By creating a bot via @BotFather and
  supplying its token and a chat ID, you can send commands to your PC from
  your phone.  The article *Remote control your Windows computer using
  Telegram* notes that the `python‑telegram‑bot` library provides an
  easy interface to the Telegram Bot API【164073357343213†L15-L18】, and you can
  obtain a token and chat ID by following the steps in that article【164073357343213†L31-L54】.

Prerequisites
-------------

Ensure you have Python 3.9 or newer installed on your Windows machine.  Then
install the required packages.  From a command prompt:

```sh
pip install pyttsx3 SpeechRecognition wikipedia python‑telegram‑bot==20.0
```

You may also need to install PyAudio for the microphone interface.  On
Windows you can download a wheel file (e.g., `PyAudio‑0.2.11‑cp39‑cp39‑win_amd64.whl`) and install it with `pip install <wheel_file>`.

Setting up Telegram (optional)
-----------------------------

1. Open Telegram and start a chat with `@BotFather`.
2. Send `/newbot` to create a new bot and follow the prompts to choose a
   name and username.  BotFather will return an API token.  Keep it safe.
3. To obtain your chat ID, talk to `@RawDataBot` and send `/start`.
   The bot will reply with your chat information; make note of the `id` field【164073357343213†L31-L54】.
4. Export these values as environment variables so the script can use them:

   ```sh
   set TELEGRAM_TOKEN=123456:ABCDEF...    # your bot token
   set TELEGRAM_CHAT_ID=987654321         # your chat ID
   ```

Usage
-----

Run the assistant from a command prompt:

```sh
python jarvis.py
```

Jarvis will greet you and then begin listening for voice commands.  Try
saying "what is the time", "open notepad", "open example.com" or "search
wikipedia Albert Einstein".  To stop the assistant say "exit" or "bye".

If you have configured a Telegram bot, start a chat with your bot on your
phone and send text commands like `time` or `open notepad`.  Jarvis will
respond in the chat and perform the action on your PC.

Extending the assistant
-----------------------

This script is intentionally simple.  You can extend it by adding new
commands to the `handle_command()` method.  For example, you might add
functions to play music, send emails, or control smart home devices.

Please note that some features (like controlling hardware or performing
sensitive actions) may require extra permissions.  Always consider the
security implications of exposing your computer to remote commands.