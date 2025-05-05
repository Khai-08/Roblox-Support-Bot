# Roblox Support Bot
A support bot designed for **Roblox Game Communities** inspired by Davy Jones Bot (Fisch Support Server). This bot helps Discord servers handle **Reports** and **Appeals** form. Ideal for Roblox developers who want to offer support inside their game’s Discord server—without coding a custom bot from scratch.

## Key Features
- Easy setup for linking support forms to specific channels
- Lightweight and easy to integrate into any Roblox game's Discord

## Commands
- `/setup` or `!setup`  
  Opens an admin-only interactive UI to set which channel handles Reports or Appeals.

## Installation
1. Clone the repo
2. Create a `.env` file:
```bash
DISCORD_TOKEN=your_bot_token
API_BASE_URL="https://apis.roblox.com/"
API_KEY="your-api-key"
```
3. To get your own API Key, follow these steps:
  1. Log in to [Roblox Developer Dashboard](https://create.roblox.com/dashboard/credentials?activeTab=ApiKeysTab)
  2. Navigate to the API Keys under Open Cloud
  3. Create a new API Key.
4. Install requirements:
```bash
pip install -r requirements.txt
```
5. Start the bot:
```bash
python main.py
```