# Roblox Support Bot
A support bot designed for **Roblox Game Communities** inspired by Davy Jones Bot (Fisch Support Server). This bot helps Discord servers handle **Reports** and **Appeals** form. Ideal for Roblox developers who want to offer support inside their game’s Discord server—without coding a custom bot from scratch.

## Key Features
- Easy setup for linking support forms to specific channels
- Lightweight and easy to integrate into any Roblox game's Discord

## Commands
- `/setup`: Configures the channels that handle Reports and Appeals forms.

## Installation
1. Clone the repository
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

## Configuration
1. Inside the project root, create a folder named `config`.
2. Inside `config/`, create a file named `bot_config.json` with the following content:
  ```json
  {
      "bot_stat": {
          "presence": "Playing", // or Watching / Listening / Competing / Streaming
          "status": "Enter your custom status here"
      },
      "footer_text": "Enter footer text (e.g., your Discord link)",
      "environment": "development", // or "production"
      "owner_id": 775966789950505002,
      "prefix": "Enter your bot prefix (e.g., . or !)"
  }
  ```
3. In the same `config/` folder, create two separate files with same contents:
  
    The bot uses two environment modes:  
    - **development** → Reads config from `config/settings.development.json`  
    - **production** → Reads config from `config/settings.production.json`

    **settings.development.json** & **settings.production.json**
    ```json
    {
        "reports": {
            "form_channel": "Enter the channel ID for report form submissions",
            "pending_reports_channel": "Enter the channel ID to queue pending reports"
        },
        "appeals": {
            "public_appeals_channel": "Enter the channel ID to post public appeals",
            "form_appeals_channel": "Enter the channel ID for appeal form submissions",
            "pending_appeals_channel": "Enter the channel ID to queue pending appeals"
        }
    }
    ```