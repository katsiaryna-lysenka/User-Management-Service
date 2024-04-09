import json
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RabbitMQManagement:
    def __init__(self, base_url):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        # Создаем сессию с настройками повторных попыток подключения
        self.session = requests.Session()
        retries = Retry(total=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def publish_reset_password_message(self, email):
        # Создаем сообщение для отправки в очередь RabbitMQ
        message = {
            "email": email,
            "subject": "Reset Your Password",
            "body": f"Click the link to reset your password: http://example.com/reset-password?email={email}",
            "publishing_datetime": datetime.now().isoformat()
        }
        # Отправляем сообщение в очередь reset-password-stream
        try:
            response = self.session.post(f"{self.base_url}/api/exchanges/%2F/amq.default/publish",
                                         headers=self.headers,
                                         json={
                                             "properties": {},
                                             "routing_key": "reset-password-stream",
                                             "payload": json.dumps(message),
                                             "payload_encoding": "string"
                                         })
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"An error occurred: {str(e)}")  # Выводим подробности об ошибке
            return False


rabbitmq_management = RabbitMQManagement(
    base_url="http://rabbitmq-container:15672"
)
