import requests

class LongAI:
    def __init__(self):
        self.base_url = "https://api.long-time.ru/v1/chat/completions"
        self.default_model = "deepseek-v3-250324"
        self.system_message = "Ты полезный ассистент"  # Значение по умолчанию

    def system(self, prompt):
        """Установка кастомного system prompt"""
        self.system_message = prompt
        return self  # Для возможности чейнинга

    def body(self, message):
        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message}
            ]
        }

        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()
        return response.json()