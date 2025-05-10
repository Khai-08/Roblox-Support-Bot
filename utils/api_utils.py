import os, aiohttp
from dotenv import load_dotenv

load_dotenv()

BASE_URL, API_KEY = os.getenv("API_BASE_URL"), os.getenv("API_KEY")

#####################
# Documentation API #
#####################

async def fetch_user_data_v2(user_id: int, endpoint: str) -> dict:
    async with aiohttp.ClientSession(headers={"x-api-key": API_KEY}) as session:
        async with session.get(f"{BASE_URL}/cloud/v2/users/{user_id}{endpoint}") as resp:
            return await resp.json()

async def fetch_user_info_v2(user_id: int) -> dict:
    try: 
        data = await fetch_user_data_v2(user_id, "")
        return { "id": data["id"], "name": data["name"], "displayName": data["displayName"]}
    except KeyError: return None

async def fetch_user_thumbnail_v2(user_id: int) -> str:
    try: 
        data = await fetch_user_data_v2(user_id, ":generateThumbnail")
        return data.get("response", {}).get("imageUri", "")
    except KeyError: return None

#####################
# PUBLIC API'S #
#####################

async def fetch_user_info_v1(user_id: int) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://users.roblox.com/v1/users/{user_id}") as resp:
            data = await resp.json()
            return { "id": data["id"], "name": data["name"], "displayName": data["displayName"]}
        
async def fetch_user_thumbnail_v1(user_id: int) -> str: 
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=420x420&format=Png&isCircular=true") as resp:
            data = await resp.json()
            return data.get('data', [{}])[0].get('imageUrl', "")