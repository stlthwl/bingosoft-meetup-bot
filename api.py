import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv


load_dotenv()


async def send_post(payload):
    headers = {
        "x-api-key": str(os.getenv("API_KEY")),
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(str(os.getenv("API_URL")), json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)


class User:
    def __init__(self):
        self.response = None
        self.user_data = None

    async def register_user(self, data: dict):
        payload = {
            "action": "register_user",
            "data": data
        }

        self.response = await send_post(payload)
        return self.response

    async def get_user_by_telegram_id(self, telegram_id: int):
        payload = {
            "action": "get_user_by_telegram_id",
            "data": {
                "telegram_id": telegram_id
            }
        }
        print(payload)
        self.response = await send_post(payload)
        return self.response
