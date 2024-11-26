import asyncio
from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ChatAction
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from app.states import Chat, ImageGen
from app.generators import gpt_text, gpt_image, gpt_vision
import uuid
import os
router = Router()



@router.message(F.text == 'Cancel')
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(0.5)
    await message.answer('Welcome! I will help you understand slang words', reply_markup=kb.main)
    await state.clear()

@router.message(F.text == 'Explanation')
async def chatting(message: Message, state: FSMContext):
    await state.set_state(Chat.text)
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(0.5)    
    await message.answer('Enter your term', reply_markup=kb.cancel)

@router.message(Chat.text, F.photo)
async def chat_responce(message: Message, state: FSMContext):
    await state.set_state(Chat.wait)
    file = await message.bot.get_file(message.photo[-1].file_id)
    file_path = file.file_path
    file_name = uuid.uuid4()
    await message.bot.download_file(file_path, f'{file_name}.jpeg')
    response = await gpt_vision(message.caption, 'gpt-4o-mini', f'{file_name}.jpeg')
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(0.5)    
    await message.answer(response['response'])
    await state.set_state(Chat.test)
    os.remove(f'{file_name}.jpeg')

@router.message(Chat.text)
async def chat_responce(message: Message, state: FSMContext):
    await state.set_state(Chat.wait)
    response = await gpt_text(message.text, 'gpt-4o-mini')
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(0.5)    
    await message.answer(response)
    await state.set_state(Chat.text)


@router.message(ImageGen.wait)
@router.message(Chat.wait)
async def wait_wait(message: Message):  
    await message.answer('Please wait your request is being processed...')


@router.message(F.text == 'Illustration + Explanation')
async def chatting(message: Message, state: FSMContext):
    await state.set_state(ImageGen.text)
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(0.5)    
    await message.answer('Enter your term', reply_markup=kb.cancel)

@router.message(ImageGen.text)
async def chat_responce(message: Message, state: FSMContext):
    await state.set_state(ImageGen.wait)
    response = await gpt_text(message.text, 'gpt-4o-mini')
    image = await gpt_image(response)
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.UPLOAD_PHOTO)
    await asyncio.sleep(0.5)    
    try:
        await message.answer_photo(photo = image)
        await message.answer(response)
    except Exception as e:
        print (e)
    await state.set_state(ImageGen.text)



@router.message()
async def echo(message: Message):
    await message.bot.send_chat_action(chat_id=message.from_user.id,
                                       action=ChatAction.TYPING)
    await asyncio.sleep(0.5)    
    await message.answer('чё.')