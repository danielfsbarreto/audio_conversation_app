import json
import os
from base64 import b64decode
from io import BytesIO
from time import sleep

import requests
from dotenv import load_dotenv

from src.models import Message

load_dotenv()


class CrewAiService:
    KICKOFF_ENDPOINT = "/kickoff"
    STATUS_ENDPOINT = "/status"

    def __init__(self):
        self.url = os.getenv("CREWAI_URL")
        self.token = os.getenv("CREWAI_TOKEN")

    @property
    def kickoff_url(self):
        return f"{self.url}{self.KICKOFF_ENDPOINT}"

    @property
    def status_url(self):
        return f"{self.url}{self.STATUS_ENDPOINT}/"

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def kickoff(self, id: str, message: Message):
        response = requests.post(
            self.kickoff_url,
            headers=self.headers,
            json={
                "inputs": {
                    "id": id,
                    "message": {"content_base64": message.content_base64},
                }
            },
        )
        response.raise_for_status()
        return response.json()

    def get_ai_message(self, kickoff_id: str):
        attempts = 0
        max_attempts = 240
        while attempts < max_attempts:
            response = requests.get(
                self.status_url + kickoff_id,
                headers=self.headers,
            )
            response.raise_for_status()
            response_json = response.json()
            if response_json["state"] == "SUCCESS":
                result_json = json.loads(response_json["result"])

                content_base64 = result_json["message"]["content_base64"]
                content_bytes = BytesIO(b64decode(content_base64))
                role = result_json["message"]["role"]
                return Message(
                    content_base64=content_base64,
                    content_bytes=content_bytes,
                    role=role,
                )
            elif response_json["state"] == "FAILED":
                raise Exception(f"Request failed with status: {response_json}")
            sleep(0.25)
            attempts += 1
        raise Exception(f"Request timed out after {max_attempts} attempts")
