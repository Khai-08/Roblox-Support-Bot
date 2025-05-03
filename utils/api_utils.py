import os, aiohttp
from dotenv import load_dotenv

load_dotenv()

BASE_URL, API_KEY = os.getenv("API_BASE_URL"), os.getenv("API_KEY")

async def fetch_user_data(user_id: int, endpoint: str) -> dict:
    async with aiohttp.ClientSession(headers={"x-api-key": API_KEY}) as session:
        async with session.get(f"{BASE_URL}/cloud/v2/users/{user_id}{endpoint}") as resp:
            return await resp.json()

async def fetch_user_info(user_id: int) -> dict:
    data = await fetch_user_data(user_id, "")
    return {"id": data["id"], "name": data["name"], "displayName": data["displayName"]}

async def fetch_user_thumbnail(user_id: int) -> str:
    data = await fetch_user_data(user_id, ":generateThumbnail")
    return data.get("response", {}).get("imageUri", "")