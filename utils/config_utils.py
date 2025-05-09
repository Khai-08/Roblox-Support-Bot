import json

class ConfigurationUtils:
    def __init__(self, bot):
        self.bot = bot
    
    def load_config(filename, mode='r', is_json=True):
        with open(filename, mode) as file:
            if is_json:
                return json.load(file)
            else:
                return file.read()

    def save_config(filename, data, is_json=True):
        with open(filename, 'w') as file:
            if is_json:
                json.dump(data, file, indent=4)
            else:
                file.write(data)

    @staticmethod
    def default_settings(file_path):
        default_settings = {
            "database": {
                "host": "localhost",
                "user": "root",
                "password": "",
                "database": "your-database-name"
            },
            "reports": {},
            "appeals": {}
        }
        
        with open(file_path, 'w') as f:
            json.dump(default_settings, f, indent=4)
        print(f"Default settings file created at {file_path}.")