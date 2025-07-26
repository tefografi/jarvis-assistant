"""
Jarvis Personal Assistant for Windows
====================================

This script implements a simple personal assistant reminiscent of “Jarvis”.
It combines offline voice recognition and text‑to‑speech on the local
machine with optional remote control via Telegram.  The goal is to provide
basic functionality that can be extended to suit your needs.

Key features
------------

* **Voice output** – Uses the `pyttsx3` library to convert text to speech.
  This library is platform‑independent and works offline【933519646353299†L63-L73】.
* **Voice input** – Uses the `SpeechRecognition` library to convert your
  spoken commands into text【933519646353299†L78-L83】.
* **Command handling** – Supports simple commands such as telling the time
  or date, opening Notepad or a web site, and searching Wikipedia for
  summaries【933519646353299†L144-L189】.
* **Remote control via Telegram** – If you supply a Telegram bot token and
  chat ID, Jarvis can process commands sent from your phone.  The
  `python‑telegram‑bot` library provides a friendly interface to the
  Telegram Bot API【164073357343213†L15-L18】.  You can obtain a token by
  chatting with `@BotFather` and a chat ID from `@RawDataBot`【164073357343213†L31-L54】.

To keep this example self‑contained, the script refrains from using any
online API keys.  You can expand it by adding your own functions (for
example, checking the weather or controlling smart devices) and calling
them from `handle_command()`.
"""

import datetime
import os
import subprocess
import webbrowser

try:
    import pyttsx3  # For text‑to‑speech
    import speech_recognition as sr  # For speech recognition
    import wikipedia  # For Wikipedia summaries
except ImportError as e:
    print("A required module is missing: {}".format(e))
    print("Please install the required packages listed in README.md before running.")
    raise

# Telegram libraries are imported conditionally so that the voice assistant
# still works even if the user does not configure a bot.  If you plan to
# use the Telegram features, install python‑telegram‑bot (version 20 or
# newer).
try:
    from telegram.ext import (
        ApplicationBuilder,
        CommandHandler,
        MessageHandler,
        filters,
    )
except ImportError:
    ApplicationBuilder = None  # type: ignore


class JarvisAssistant:
    """Encapsulates local and remote assistant behaviour."""

    def __init__(self, telegram_token: str | None = None, telegram_chat_id: str | None = None) -> None:
        # Initialize text‑to‑speech engine.  Sapi5 on Windows and eSpeak on
        # Linux are handled transparently by pyttsx3【933519646353299†L63-L73】.
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty("voices")
        # Use the first available voice (usually a male voice).  Users can
        # change the index here to select a different voice (e.g. voices[1]).
        self.engine.setProperty("voice", voices[0].id)
        # Set a moderate speech rate.
        self.engine.setProperty("rate", 150)

        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.telegram_app = None

    # ------------------------------------------------------------------
    # Text‑to‑speech and speech recognition helpers
    # ------------------------------------------------------------------
    def speak(self, text: str) -> None:
        """Convert text to speech and print it to the console."""
        print(f"Jarvis: {text}")
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self) -> str:
        """Listen for a spoken command using the microphone.

        Returns the recognised text in lower case, or an empty string if
        recognition fails.  The SpeechRecognition library uses
        Google's free API by default, so a network connection is
        required.  You can switch to offline engines if desired.
        """
        recogniser = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening…")
            audio = recogniser.listen(source)
        try:
            # Recognise speech in US English.  You can change the locale.
            command = recogniser.recognize_google(audio, language="en-US")
            print(f"User: {command}")
            return command.lower()
        except Exception as e:
            print(f"Error recognising speech: {e}")
            return ""

    # ------------------------------------------------------------------
    # Command processing
    # ------------------------------------------------------------------
    def handle_command(self, command: str) -> str:
        """Interpret a command and perform an action.

        Returns a textual response to send back via Telegram.  For voice
        interactions the response is already spoken aloud.
        """
        response = ""
        if not command:
            return response

        # Time and date queries
        if "time" in command:
            current = datetime.datetime.now().strftime("%H:%M")
            response = f"The time is {current}"
            self.speak(response)
        elif "date" in command:
            current = datetime.datetime.now().strftime("%d %B %Y")
            response = f"Today's date is {current}"
            self.speak(response)

        # Launch applications or open web sites
        elif command.startswith("open"):
            parts = command.split(maxsplit=1)
            if len(parts) >= 2:
                target = parts[1].strip()
                # Example: "open notepad" will launch Windows Notepad
                if target == "notepad":
                    try:
                        subprocess.Popen(["notepad.exe"])
                        response = "Opening Notepad"
                    except FileNotFoundError:
                        response = "Notepad is not available on this system."
                    self.speak(response)
                else:
                    # Assume it's a URL or domain; add protocol if missing
                    url = target
                    if not url.startswith("http"):
                        url = "http://" + url
                    webbrowser.open(url)
                    response = f"Opening {url}"
                    self.speak(response)

        # Wikipedia search
        elif "wikipedia" in command:
            # Remove the word 'wikipedia' and search the remainder
            query = command.replace("wikipedia", "").strip()
            if query:
                try:
                    summary = wikipedia.summary(query, sentences=2)
                    response = summary
                    self.speak("According to Wikipedia")
                    self.speak(summary)
                except Exception:
                    response = "Sorry, I couldn't find anything on Wikipedia."
                    self.speak(response)

        # Exit command
        elif "exit" in command or "bye" in command:
            response = "Goodbye!"
            self.speak(response)
            # Terminate the program gracefully.  os._exit() avoids
            # recursion issues in speech engines when used in threads.
            os._exit(0)

        # Unknown command
        else:
            response = "I didn't understand that command."
            self.speak(response)

        return response

    # ------------------------------------------------------------------
    # Telegram integration
    # ------------------------------------------------------------------
    async def telegram_start(self, update, context) -> None:
        """Handle the /start command sent to the Telegram bot."""
        if self.telegram_chat_id is None:
            # Capture the chat ID on first contact so that the assistant
            # knows where to reply.
            self.telegram_chat_id = str(update.effective_chat.id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Hello! I'm your Jarvis assistant. Send me a command.",
        )

    async def telegram_message(self, update, context) -> None:
        """Handle any text message sent to the Telegram bot."""
        text = update.message.text.lower()
        response = self.handle_command(text)
        # Only send a Telegram response if the command produced one.
        if response:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=response
            )

    def setup_telegram(self) -> None:
        """Set up the Telegram bot if a token has been provided."""
        if not self.telegram_token:
            return
        if ApplicationBuilder is None:
            raise ImportError(
                "python‑telegram‑bot is not installed. Install it to use the Telegram features."
            )
        # Build the asynchronous Telegram application
        self.telegram_app = ApplicationBuilder().token(self.telegram_token).build()
        # Register handlers for /start and plain text messages
        self.telegram_app.add_handler(CommandHandler("start", self.telegram_start))
        self.telegram_app.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), self.telegram_message)
        )

    def run_telegram(self) -> None:
        """Start polling Telegram updates."""
        if self.telegram_app:
            self.telegram_app.run_polling()

    def run_voice(self) -> None:
        """Start an infinite loop listening for voice commands."""
        while True:
            command = self.listen()
            # Process the command locally.  The method returns a string but
            # speaking is handled internally.
            self.handle_command(command)


def main() -> None:
    """Entry point for running the assistant.

    The Telegram token and chat ID can be supplied via environment
    variables (`TELEGRAM_TOKEN` and `TELEGRAM_CHAT_ID`) or by editing
    the placeholders below.  If no token is supplied the assistant
    still provides local voice interaction.
    """
    # Obtain configuration from environment variables if available
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")

    # Create an instance of the assistant
    assistant = JarvisAssistant(
        telegram_token=telegram_token, telegram_chat_id=telegram_chat_id
    )
    assistant.setup_telegram()

    # If Telegram is configured, run it in a separate thread so that
    # voice and Telegram can operate concurrently.
    if assistant.telegram_app:
        import threading

        telegram_thread = threading.Thread(target=assistant.run_telegram, daemon=True)
        telegram_thread.start()

    # Greet the user locally and enter the voice command loop.
    assistant.speak("Jarvis at your service. How can I help you?")
    assistant.run_voice()


if __name__ == "__main__":
    main()