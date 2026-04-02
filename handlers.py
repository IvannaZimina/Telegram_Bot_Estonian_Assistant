"""
Основная логика Telegram-бота.

Здесь находятся обработчики /start, выбора языка, ввода текста,
показа примеров, словоформ и кнопки рестарта. Этот файл связывает
состояния пользователя, промпты OpenAI и ответы в Telegram.
"""

import json
import logging
import re
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import build_language_menu, build_main_menu
from prompts import make_examples_prompt, make_forms_prompt, make_translation_prompt
from services import ask_ai
from state import LearnFlow

router = Router()
logger = logging.getLogger(__name__)


def clean_examples_text(text: str) -> str:
    text = text.replace("<ol>", "").replace("</ol>", "")
    text = text.replace("<li>", "\n").replace("</li>", "\n")
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(r"</?b>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"<[^>]+>", "", text)

    lines = [line.strip() for line in text.splitlines()]
    lines = [line for line in lines if line]

    examples = []
    current_sentence = None
    current_translation = None

    for line in lines:
        numbered_match = re.match(r"^(\d+)[.)]\s*(.+)$", line)
        if numbered_match:
            if current_sentence:
                examples.append((current_sentence, current_translation or ""))
            current_sentence = numbered_match.group(2).strip()
            current_translation = ""
            continue

        if current_sentence is None:
            current_sentence = line
            current_translation = ""
            continue

        if not current_translation:
            current_translation = line
        else:
            current_translation = f"{current_translation} {line}".strip()

    if current_sentence:
        examples.append((current_sentence, current_translation or ""))

    if len(examples) >= 3:
        formatted = []
        for index, (sentence, translation) in enumerate(examples[:3], start=1):
            formatted.append(f"{index}. {sentence}")
            if translation:
                formatted.append(f"   {translation}")
        return "\n".join(formatted).strip()

    return "\n".join(lines).strip()


def parse_translation_result(text: str, fallback_input: str) -> tuple[bool, str, str]:
    cleaned = text.strip()
    cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()
    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(0)

    try:
        data = json.loads(cleaned)
        is_estonian = bool(data.get("is_estonian", False))
        estonian = str(data.get("estonian", "")).strip() or fallback_input
        russian = str(data.get("russian", "")).strip()
        return is_estonian, estonian, russian
    except Exception:
        logger.warning("Failed to parse translation JSON, falling back to raw text")
        return False, cleaned or fallback_input, ""


def normalize_forms_result(text: str) -> str:
    cleaned = text.strip()

    if re.search(r"<b>Часть речи:</b>\s*tegusõna", cleaned, flags=re.IGNORECASE):
        cleaned = re.sub(
            r"\n?<b>Словоформы:</b>.*$",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )
    else:
        cleaned = re.sub(
            r"\n?<b>Глагольные формы:</b>.*$",
            "",
            cleaned,
            flags=re.IGNORECASE | re.DOTALL,
        )

    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


async def send_menu(message: types.Message, lang: str, show_forms: bool) -> None:
    hint = "После просмотра просто введите новое слово." if lang == "ru" else "After reading the result, just type a new word."
    await message.answer(hint, reply_markup=build_main_menu(lang, show_forms))


@router.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "<b>Выберите язык / Choose language:</b>",
        reply_markup=build_language_menu(),
        parse_mode="HTML",
    )
    await state.set_state(LearnFlow.choosing_language)


@router.callback_query(F.data.startswith("lang_"))
async def select_language(call: types.CallbackQuery, state: FSMContext):
    lang = call.data.split("_")[1]
    await state.update_data(language=lang)

    msgs = {
        "ru": "Введите слово или фразу на русском или английском — я переведу на эстонский 🇪🇪",
        "en": "Enter a word or phrase in Russian or English — I will translate it into Estonian 🇪🇪",
    }

    await call.answer()
    await call.message.answer(f"<b>{msgs[lang]}</b>", parse_mode="HTML")


@router.message()
async def process_text(message: types.Message, state: FSMContext):
    data = await state.get_data()

    if not message.text:
        return await message.answer("<b>Пожалуйста, отправьте текстовое сообщение.</b>", parse_mode="HTML")

    if "language" not in data:
        return await message.answer(
            "<b>Пожалуйста, выберите язык / Please choose a language (/start)</b>",
            parse_mode="HTML",
        )

    lang = data["language"]
    user_text = message.text.strip()
    if not user_text:
        return await message.answer("<b>Пожалуйста, отправьте непустой текст.</b>", parse_mode="HTML")

    logger.info("Text received: lang=%s text=%r", lang, user_text)

    await state.update_data(last_word=user_text)

    translation_result = await ask_ai(make_translation_prompt(user_text))
    is_estonian, estonian_text, russian_text = parse_translation_result(translation_result, user_text)
    await state.update_data(last_estonian=estonian_text)
    logger.info("Translation generated: estonian=%r is_estonian=%s", estonian_text, is_estonian)

    show_forms = len(user_text.split()) == 1
    if is_estonian:
        reply = (
            f'Слово "{user_text}" уже на эстонском.\nПеревод на русский: {russian_text or "—"}'
            if lang == "ru"
            else f'The word "{user_text}" is already in Estonian.\nTranslation to Russian: {russian_text or "—"}'
        )
    else:
        reply = (
            f"Перевод на эстонский:\n{estonian_text}"
            if lang == "ru"
            else f"Translation to Estonian:\n{estonian_text}"
        )

    await message.answer(reply)
    await send_menu(message, lang, show_forms)


@router.callback_query(F.data == "examples")
async def examples(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    est_word = data.get("last_estonian", "")
    lang = data.get("language")

    if not est_word or not lang:
        return await call.message.answer("<b>Сначала введите слово или фразу.</b>", parse_mode="HTML")

    text = await ask_ai(make_examples_prompt(est_word, lang))
    logger.info("Examples generated for word=%r", est_word)

    show_forms = len(data.get("last_word", "").split()) == 1
    examples_text = clean_examples_text(text)
    await call.message.answer(f"Примеры:\n{examples_text}")
    await send_menu(call.message, lang, show_forms)


@router.callback_query(F.data == "forms")
async def forms(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    est = data.get("last_estonian", "")
    lang = data.get("language")
    original = data.get("last_word", "")

    if not est or not original or not lang:
        return await call.message.answer("<b>Сначала введите слово или фразу.</b>", parse_mode="HTML")

    if len(original.split()) != 1:
        return await call.message.answer("<b>Формы слова доступны только для одного слова.</b>", parse_mode="HTML")

    result = await ask_ai(make_forms_prompt(est))
    logger.info("Forms generated for word=%r", est)

    await call.message.answer(normalize_forms_result(result), parse_mode="HTML")
    await send_menu(call.message, lang, True)


@router.callback_query(F.data == "restart_bot")
async def restart_btn(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await start(call.message, state)
