import requests
from typing import Dict, Union

class LongAI:
    def __init__(self):
        self.base_url = "https://api.long-time.ru/v1/chat/completions"
        self.default_model = "deepseek-v3-250324"
        self.system_message = "Ты полезный ассистент"

    def system(self, prompt: str) -> 'LongAI':
        """Установка кастомного system prompt"""
        self.system_message = prompt
        return self

    def body(self, message: str) -> str:
        """
        Отправка запроса и возврат текста ответа
        Возвращает:
            str: текст ответа ассистента
        Исключения:
            requests.HTTPError: при ошибке запроса
            KeyError: при неожиданной структуре ответа
        """
        payload = {
            "model": self.default_model,
            "messages": [
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message}
            ]
        }

        response = requests.post(self.base_url, json=payload)
        response.raise_for_status()
        return self._extract_response(response.json())

    def _extract_response(self, json_data: Dict) -> str:
        """Извлекает текст ответа из JSON структуры"""
        try:
            return json_data['choices'][0]['message']['content']
        except (KeyError, IndexError) as e:
            raise ValueError("Неожиданный формат ответа API") from e

    def raw_request(self, message: str) -> Dict:
        """Отправка запроса с возвратом полного JSON ответа"""
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