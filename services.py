"""
Supporting services.

This module initializes the OpenAI client, sends model requests,
and provides a small helper for escaping HTML before sending to Telegram.
"""

import asyncio
import html
import logging

from openai import OpenAI

from config import OPENAI_API_KEY

logger = logging.getLogger(__name__)
client = OpenAI(api_key=OPENAI_API_KEY)


async def ask_ai(prompt: str) -> str:
    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        content = response.choices[0].message.content or ""
        content = content.strip()
        return content or "⚠️ Bot temporarily unavailable. Try again later."
    except Exception as exc:
        logger.exception("OpenAI request failed: %s", exc)
        return "⚠️ Bot temporarily unavailable. Try again later."


def escape_html(text: str) -> str:
    return html.escape(text, quote=False)
