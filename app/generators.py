import os
import asyncio
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv

import base64
import aiohttp
import aiofiles

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv('AITOKEN'),
                     http_client=httpx.AsyncClient(proxies="http://dGGGECxS:qxDEjNn3@185.128.41.74:62912",
                                                   transport=httpx.HTTPTransport(local_address="0.0.0.0")))


async def slang_check(req, model='gpt-4o-mini'):
    slang = f"Is the word '{req}' considered slang? Respond with 'Yes' or 'No' without any further explanation."
    response = await client.chat.completions.create(
        messages=[{"role": "user", "content": slang}],
        model=model
    )
    check_result = response.choices[0].message.content.strip().lower()
    if 'yes' in check_result:
        return True
    else:
        return False


async def gpt_text(req, model):
    if await slang_check(req):
        explanation = f"Explain the slang term '{req}'."
        explanation_response = await client.chat.completions.create(
            messages=[{"role": "user", "content": explanation}],
            model=model
        )
        return  explanation_response.choices[0].message.content
    else:
        return  f"The word '{req}' is not recognized as slang."


async def gpt_image(req):
    if await slang_check(req):
        response = await client.images.generate(
            model='dall-e-3',
            prompt=f"'{req}'",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    else:
        return "https://avatars.mds.yandex.net/i?id=1c16a14d2fcc5ce4ef9455813f5aae266a4049ee-5283999-images-thumbs&n=13"


async def encode_image(image_path):
    async with aiofiles.open(image_path, "rb") as image_file:
        return base64.b64encode(await image_file.read()).decode('utf-8')


async def gpt_vision(req, model, file):
    base64_image = await encode_image(file)
    headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('AITOKEN')}"
        }

    payload = {
    "model": model,
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }
    if req is not None:
            payload["messages"][0]['content'].append({
                "type": "text",
                "text": req
            })

    async with aiohttp.ClientSession() as session:
            async with session.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload) as response:
                completion = await response.json()
    return {'response': completion['choices'][0]['message']['content']}

