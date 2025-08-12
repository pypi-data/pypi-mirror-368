import requests


class TextDiffEngine:
    """
    A client for the Formamind Text Diff Engine API.
    The API compares two texts and highlights changes, including added, deleted, and moved blocks.
    """

    API_URL = "https://www.api.formamind.com/core/diffengine/compare/"

    def __init__(self, api_key):
        """
        Initialize the client with your Formamind API key.
        :param api_key: Your private API key (provided via email after obtaining a token)
        """
        self.api_key = api_key

    def compare(self, old_text, new_text, output_format="json"):
        """
        Compare two texts using the diff engine API.

        :param old_text: The original text.
        :param new_text: The updated text.
        :param output_format: The desired response format ("json" or "html").
        :return: The API response as a dict.
        """

        payload = {
            "old_text": old_text,
            "new_text": new_text,
            "output_format": output_format,
        }
        headers = {
            "X-DiffEngine-Secret": f"{self.api_key}",
            "Content-Type": "application/json",
        }

        response = requests.post(
            self.API_URL, json=payload, headers=headers, timeout=31
        )
        response.raise_for_status()

        return response.json()
