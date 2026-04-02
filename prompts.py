def make_translation_prompt(user_text: str) -> str:
    return f"""
Ты — словарь RU/EN → EST.
Переведи '{user_text}' на ЭСТОНСКИЙ ЯЗЫК.
Требования:
- Дай 1 точный перевод (слово или короткая фраза).
- Без примеров.
- Без пояснений.

Формат: только перевод.
"""


def make_examples_prompt(est_word: str, lang: str) -> str:
    translate_to = "русский" if lang == "ru" else "английский"
    return f"""
Создай 3 естественных предложения на ЭСТОНСКОМ со словом "{est_word}".
После каждого предложения ДАЙ перевод на {translate_to}.
Формат ответа (HTML):
<ol>
<li><b>Estonian sentence</b><br>Translation</li>
<li><b>Estonian sentence</b><br>Translation</li>
<li><b>Estonian sentence</b><br>Translation</li>
</ol>
"""


def make_forms_prompt(est_word: str) -> str:
    return f"""
Ты — эксперт по эстонской морфологии.
РАБОТАЙ ТОЛЬКО СО СЛОВОМ: '{est_word}'.
Это ЭСТОНСКОЕ слово. НЕ используй русский язык, НЕ склоняй русский ввод.

Твои задачи:

1) Точно определи часть речи слова:
   - nimisõna (существительное)
   - tegusõna (глагол)
   - omadussõna (прилагательное)
   - asesõna (местоимение)

2) Дай только правильные словоформы, существующие в современном эстонском языке.
   НИ В КОЕМ СЛУЧАЕ не придумывай форм.

3) Формат ответа (HTML):

<b>Слово:</b> {est_word}
<b>Часть речи:</b> asesõna/tegusõna/nimisõna/omadussõna

<b>Словоформы:</b>
- nimetav: ...
- omastav: ...
- osastav: ...

<b>Глагольные формы (если tegusõna):</b>
- ma-vorm: ...
- da-vorm: ...
- oleviku vorm (3. pööre): ...
- mineviku vorm: ...
- käskiv kõneviis: ...
- passiiv (если есть): ...

<b>Примечания:</b> не включай дополнительные пояснения, не используй сокращённые формы (например, 'ma' вместо 'mina'), используй только полные нормативные формы.
"""
