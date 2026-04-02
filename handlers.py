import logging
from aiogram import F, Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from keyboards import build_language_menu, build_main_menu
from prompts import make_examples_prompt, make_forms_prompt, make_translation_prompt
from services import ask_ai, escape_html
from state import LearnFlow

router = Router()
logger = logging.getLogger(__name__)


async def send_menu(message: types.Message, lang: str, show_forms: bool) -> None:
    await message.answer(
        "<b>Выберите действие:</b>" if lang == "ru" else "<b>Choose an action:</b>",
        reply_markup=build_main_menu(lang, show_forms),
        parse_mode="HTML",
    )


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

    est = await ask_ai(make_translation_prompt(user_text))
    await state.update_data(last_estonian=est)
    logger.info("Translation generated: %r", est)

    show_forms = len(user_text.split()) == 1
    header = "Перевод на эстонский" if lang == "ru" else "Translation to Estonian"
    await message.answer(
        f"<b>{header}:</b>\n<b>{escape_html(est)}</b>",
        parse_mode="HTML",
    )
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
    await call.message.answer(f"<b>{escape_html(text)}</b>", parse_mode="HTML")
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

    await call.message.answer(result, parse_mode="HTML")
    await send_menu(call.message, lang, True)


@router.callback_query(F.data == "restart_bot")
async def restart_btn(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await start(call.message, state)
