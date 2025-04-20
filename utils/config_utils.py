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