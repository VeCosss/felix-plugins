"""Таймер — «Таймер на 5 минут» с бипом."""
import re
import threading
import time
import winsound
from loguru import logger

from plugins.base import Plugin


class TimerPlugin(Plugin):
    name = "timer"
    display_name = "Таймер"
    description = "«Таймер на 5 минут» — напомнит звуком"
    version = "1.0.0"
    author = "felix"

    TRIGGERS = ["таймер", "напомни через", "обратный отсчёт"]

    def get_settings_schema(self) -> list[dict]:
        return [
            {
                "key": "sound_enabled",
                "type": "checkbox",
                "label": "Звуковой сигнал",
                "default": True,
            },
            {
                "key": "beep_frequency",
                "type": "slider",
                "label": "Частота сигнала (Гц)",
                "min": 200,
                "max": 3000,
                "default": 1000,
                "step": 100,
            },
            {
                "key": "beep_duration",
                "type": "slider",
                "label": "Длительность сигнала (мс)",
                "min": 100,
                "max": 3000,
                "default": 500,
                "step": 100,
            },
            {
                "key": "beep_count",
                "type": "number",
                "label": "Сколько раз пикнуть",
                "min": 1,
                "max": 10,
                "default": 3,
                "step": 1,
            },
        ]

    def try_handle(self, text: str) -> str | None:
        t = text.lower().strip()
        if not any(trig in t for trig in self.TRIGGERS):
            return None

        match = re.search(r'(\d+)\s*(минут|мин|секунд|сек|час|ч)', t)
        if not match:
            return "На сколько? Скажи 'таймер на 5 минут'"

        value = int(match.group(1))
        unit = match.group(2)

        if unit.startswith("сек"):
            seconds = value
            human = f"{value} секунд"
        elif unit.startswith("мин"):
            seconds = value * 60
            human = f"{value} минут"
        elif unit.startswith("час") or unit == "ч":
            seconds = value * 3600
            human = f"{value} час"
        else:
            seconds = value * 60
            human = f"{value} минут"

        beep = {
            "enabled": self.config.get("sound_enabled", True),
            "freq": int(self.config.get("beep_frequency", 1000)),
            "dur": int(self.config.get("beep_duration", 500)),
            "count": int(self.config.get("beep_count", 3)),
        }

        def _worker():
            time.sleep(seconds)
            logger.info(f"[timer] сработал на {seconds} сек")
            if beep["enabled"]:
                for _ in range(beep["count"]):
                    winsound.Beep(beep["freq"], beep["dur"])
                    time.sleep(0.2)

        threading.Thread(target=_worker, daemon=True).start()
        return f"Таймер на {human} запущен"