"""Заметки — «Запиши: купить хлеб»."""
import json
from datetime import datetime
from pathlib import Path
from loguru import logger

from plugins.base import Plugin


NOTES_FILE = Path(__file__).resolve().parent.parent / "notes.json"


class NotesPlugin(Plugin):
    name = "notes"
    display_name = "Заметки"
    description = "«Запиши: купить хлеб» / «Что в заметках» / «Очисти заметки»"
    version = "1.0.0"
    author = "felix"

    def _load(self) -> list[dict]:
        if NOTES_FILE.exists():
            try:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save(self, notes: list[dict]) -> None:
        with open(NOTES_FILE, "w", encoding="utf-8") as f:
            json.dump(notes, f, ensure_ascii=False, indent=2)

    def try_handle(self, text: str) -> str | None:
        t = text.lower().strip()

        # очистить
        if any(w in t for w in ["очисти заметки", "удали все заметки", "стереть заметки"]):
            self._save([])
            return "Заметки очищены"

        # прочитать
        if any(w in t for w in ["что в заметках", "прочитай заметки",
                                "мои заметки", "покажи заметки"]):
            notes = self._load()
            if not notes:
                return "Заметок нет"
            preview = "; ".join(n["text"] for n in notes[-5:])
            return f"У тебя {len(notes)} заметок. Последние: {preview}"

        # записать
        for prefix in ["запиши:", "запиши ", "заметка:", "заметка ",
                       "запомни:", "запомни ", "добавь заметку "]:
            if t.startswith(prefix):
                note_text = text[len(prefix):].strip()
                if not note_text:
                    return "Что записать?"
                notes = self._load()
                notes.append({
                    "text": note_text,
                    "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                })
                self._save(notes)
                return f"Записал: {note_text}"

        return None