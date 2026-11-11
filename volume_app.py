"""Управление громкостью отдельных приложений (Chrome, Spotify и т.д.)."""
from loguru import logger

from plugins.base import Plugin


class VolumeAppPlugin(Plugin):
    name = "volume_app"
    display_name = "Громкость приложений"
    description = "«Сделай тише Chrome» / «Громче Spotify»"
    version = "1.0.0"
    author = "felix"

    APP_ALIASES = {
        "chrome": "chrome.exe",
        "хром": "chrome.exe",
        "firefox": "firefox.exe",
        "файрфокс": "firefox.exe",
        "spotify": "spotify.exe",
        "спотифай": "spotify.exe",
        "discord": "discord.exe",
        "дискорд": "discord.exe",
        "steam": "steam.exe",
        "стим": "steam.exe",
        "телеграм": "telegram.exe",
        "telegram": "telegram.exe",
    }

    def try_handle(self, text: str) -> str | None:
        t = text.lower().strip()

        # ищем "громче X" / "тише X"
        action = None
        if "громче" in t:
            action = +0.1
        elif "тише" in t:
            action = -0.1
        else:
            return None

        app = None
        for alias, exe in self.APP_ALIASES.items():
            if alias in t:
                app = exe
                break

        if not app:
            return None

        try:
            from pycaw.pycaw import AudioUtilities
            sessions = AudioUtilities.GetAllSessions()
            changed = False
            for session in sessions:
                if session.Process and session.Process.name().lower() == app:
                    volume = session.SimpleAudioVolume
                    new_vol = max(0.0, min(1.0, volume.GetMasterVolume() + action))
                    volume.SetMasterVolume(new_vol, None)
                    changed = True
                    break

            if changed:
                word = "громче" if action > 0 else "тише"
                return f"Сделал {word} {app}"
            return f"Не нашёл {app} в запущенных"
        except Exception as e:
            logger.exception(f"[volume_app] error: {e}")
            return "Не смог изменить громкость"