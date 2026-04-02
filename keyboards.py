"""
Keyboards and inline menus.

This module defines language selection buttons and the main action menu
shown after translation: examples, word forms, and restart.
"""

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def build_main_menu(lang: str, show_forms: bool) -> InlineKeyboardMarkup:
    labels = {
        "ru": ["📘 Примеры", "📝 Формы слова", "🔄 Рестарт"],
        "en": ["📘 Examples", "📝 Word forms", "🔄 Restart"],
    }
    b = labels[lang]

    kb = InlineKeyboardBuilder()
    kb.button(text=b[0], callback_data="examples")
    if show_forms:
        kb.button(text=b[1], callback_data="forms")
    kb.button(text=b[2], callback_data="restart_bot")
    kb.adjust(1)
    return kb.as_markup()


def build_language_menu() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 Русский", callback_data="lang_ru")
    kb.button(text="🇬🇧 English", callback_data="lang_en")
    kb.adjust(1)
    return kb.as_markup()
