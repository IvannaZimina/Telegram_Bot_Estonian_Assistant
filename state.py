"""
Bot FSM states.

States are used to store the current dialog step: language selection,
the last user input, and the last Estonian translation.
"""

from aiogram.fsm.state import State, StatesGroup


class LearnFlow(StatesGroup):
    choosing_language = State()
    last_word = State()
    last_estonian = State()
    language = State()
