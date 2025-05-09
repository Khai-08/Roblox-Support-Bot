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
  DISCORD_TOKEN="your_bot_token"
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
3. To import the database tables into MySQL:
    - Open your MySQL client (e.g., phpMyAdmin or MySQL CLI).
    - Create a database with a name of your choice.
    - Import the file located at config/database.sql.
4. Inside `config/`, update the settings.development.json or settings.production.json file with the correct database credentials. The default settings are:
    ```json
    {
      "database": {
          "host": "localhost",
          "user": "root",
          "password": "",
          "database": "your-database-name"
      },
      "reports": {},
      "appeals": {}
    }
    ```