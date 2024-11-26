from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Explanation')],
    [KeyboardButton(text='Illustration + Explanation')]
],       
                            resize_keyboard=True, 
                            input_field_placeholder='What exactly are you interested in?')
cancel= ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Cancel')]],
                            resize_keyboard=True)