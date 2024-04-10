import logging
import requests


class TEXT2SPEECH:
    """
    Call through API
    """

    def __init__(self, url):
        self.URL = url
        logging.info("Success init text to speech inference!!!")

    def __call__(self, text):
        payload = {"text": text}
        files = []
        headers = {}

        response = requests.request(
            "POST", self.URL, headers=headers, data=payload, files=files
        )
        if response.status_code == 200:
            return response.content
        else:
            return None
