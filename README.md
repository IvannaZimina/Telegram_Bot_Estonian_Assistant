# TG Estonian Bot

TG Estonian Bot is a Telegram assistant for learning Estonian through short translations, examples, and basic morphology. A user can send a Russian, English, or already Estonian word/phrase, and the bot responds with the most useful next step instead of just producing a raw translation.

## What the bot does

The bot is designed as a small guided learning flow:

1. The user starts the bot with `/start`.
2. The bot asks the user to choose an interface language: Russian or English.
3. The user sends a word or phrase.
4. The bot checks whether the input is already Estonian.
5. If the text is not Estonian, the bot translates it into Estonian.
6. If the text is already Estonian, the bot says so and shows the Russian translation.
7. After the main answer, the bot shows buttons for examples, word forms, and restart only when the user entered a single word.
8. If the user entered a phrase, the word-forms button is hidden.
9. The user can then either press a button or simply type a new word immediately.

This means the bot is not a long chat. It works like a compact learning tool that remembers the latest input and gives follow-up actions based on it.

## User Journey

### 1. Start

When the user sends `/start`, the bot clears any previous conversation state and shows a language picker.

### 2. Choose interface language

The user selects either Russian or English. The choice only changes the interface text and the button labels. It does not change the language of the learning content itself.

### 3. Enter a word or phrase

After the language is selected, the user can type a word or a short phrase in Russian, English, or Estonian.

### 4. Main response

The bot sends the result in one of two ways:

- If the input is not Estonian, it returns the Estonian translation.
- If the input is already Estonian, it tells the user that the word is already in Estonian and gives the Russian translation.

At this point the bot also stores the latest input and the Estonian form of that input so the next actions can reuse it.

### 5. Follow-up actions

After the answer, the bot shows a minimal menu:

- Examples: generates three natural Estonian example sentences and translations.
- Word forms: shows morphology and forms, but only for a single word.
- Restart: sends the user back to the beginning.

The bot also tells the user that they can simply type a new word at any time. There is no mandatory command for continuing.

### 6. Examples

If the user presses Examples, the bot asks OpenAI for three example sentences in Estonian using the latest Estonian word. The response is cleaned and shown in a readable plain-text format.

### 7. Word forms

If the user presses Word forms, the bot asks OpenAI for the part of speech and the relevant forms. This option is only shown when the original input was a single word. Phrase inputs hide the section entirely.

### 8. Restart

If the user presses Restart, the bot resets the flow and returns to the language selection screen.

## Project Structure

- `bot.py` - application entry point. Creates the bot, dispatcher, and starts polling.
- `config.py` - loads environment variables and sets up logging.
- `handlers.py` - contains the Telegram conversation logic and all user actions.
- `keyboards.py` - builds the inline keyboards used by the bot.
- `prompts.py` - builds the OpenAI prompts for translation, examples, and forms.
- `services.py` - wraps OpenAI calls and HTML escaping helpers.
- `state.py` - defines FSM states used to keep track of the current flow.
- `requirements.txt` - project dependencies.
- `.env` - local secrets for Telegram and OpenAI.
- `.env.example` - template for the environment file.

## How the Logic Works Internally

The bot uses a small FSM-based flow to remember what the user has already done.

- `choosing_language` - the user is selecting the interface language.
- `language` - the selected interface language is stored in the state data.
- `last_word` - the last user input is saved here.
- `last_estonian` - the latest Estonian form or translation is saved here.

The main handler in `handlers.py` does most of the work:

1. It receives the user message.
2. It checks that the message is text.
3. It checks that the user already picked a language.
4. It sends the text to OpenAI through a translation prompt.
5. It parses the response and decides whether the input was already Estonian.
6. It saves the Estonian text for later actions.
7. It sends the main answer and shows the follow-up menu.

The examples and forms actions do not start from scratch. They reuse the latest Estonian word stored in the state.

## Implementation Notes

- The bot uses `aiogram` for Telegram integration.
- OpenAI requests are wrapped in `asyncio.to_thread()` so the bot stays responsive.
- The examples response is normalized to plain text to avoid Telegram HTML parsing issues.
- HTML is used only where it is safe and needed.
- Logging is enabled to make the runtime flow easier to debug.
- The word-forms button is controlled by the original input length, so phrases do not expose the morphology section.

## Setup

1. Install dependencies from `requirements.txt`.
2. Create a `.env` file based on `.env.example`.
3. Set `TELEGRAM_TOKEN` and `OPENAI_API_KEY`.
4. Run `bot.py`.

## Notes for Users

You do not need to memorize commands after the bot starts.

- After `/start`, choose the interface language once.
- Then just type a word or phrase.
- After each answer, you can press a button or type the next word immediately.

That is the intended flow: start once, type naturally, and keep learning step by step.

## Views
<img width="384" height="379" alt="image" src="https://github.com/user-attachments/assets/886356d6-499b-4951-9638-ec3e1b6fb916" />
<img width="375" height="955" alt="image" src="https://github.com/user-attachments/assets/52a461cf-1f95-48e2-917b-a1aa1ef08871" />

