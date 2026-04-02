from aiogram.fsm.state import State, StatesGroup


class LearnFlow(StatesGroup):
    choosing_language = State()
    last_word = State()
    last_estonian = State()
    language = State()
