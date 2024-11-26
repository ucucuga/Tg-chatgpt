from aiogram.fsm.state import StatesGroup, State

class Chat(StatesGroup):
    text= State()
    wait =State()

class ImageGen(StatesGroup):
    text= State()
    wait =State()