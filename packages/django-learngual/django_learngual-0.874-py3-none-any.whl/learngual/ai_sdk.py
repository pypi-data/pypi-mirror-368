from logging import getLogger
from uuid import uuid4

import requests
from django.conf import settings

logger = getLogger(__file__)

api_key = settings.AI_SERVICE_API_KEY
base_url = settings.AI_SERVICE_DEMO_URL
headers = {"api-key": api_key}


class AIProcessing:
    """
    This class handles the AI processing for submissions

    For this to work, you must specify the AI_SERVICE_DEMO_URL
    and LEARNGUAL_AI_API_KEY in your settings.py file.
    """

    @staticmethod
    def analyze_audio(
        audio,
        reference_text,
        scripted: bool = False,
        prompt: str = None,
        language: str = None,
        correct_reference: bool = True,
        query_string: str = None,
    ):
        """
        this communicates with the AI model and returns the analysis results
        for the given audio
        """
        base_url = settings.AI_SERVICE_DEMO_URL
        if not str(base_url).endswith("/"):
            base_url += "/"

        uid = uuid4().hex
        files = {"audio_data": (f"{uid}-audio.mp3", audio)}
        payload = {
            "reference_text": reference_text,
            "scripted": scripted,
            "correct_reference": correct_reference,
        }

        if prompt:
            payload["prompt"] = prompt

        if language:
            payload["language"] = language

        if query_string:
            base_url += "?" + query_string

        response = requests.post(
            url=base_url, headers=headers, files=files, data=payload
        )
        if response.status_code == 200:
            return {"status": True, "response": response}

        else:
            return {"status": False, "response": response}

    @staticmethod
    def relevance(topic: str, essay: str, query_string: str = None):
        base_url = settings.AI_SERVICE_DEMO_URL

        if not str(base_url).endswith("/"):
            base_url += "/"

        base_url = base_url.rstrip("process/") + "/relevance/"

        if query_string:
            base_url += "?" + query_string

        response = requests.post(
            url=base_url,
            headers=headers,
            data={"topic": topic, "essay": essay},
        )

        if response.status_code == 200:
            return {"status": True, "response": response}

        else:
            return {"status": False, "response": response}

    def logic_evaluation(
        topic: str,
        essay: str,
        criteria: list[str] = None,
        query_string: str = None,
    ):
        """Evaluates the logical structure and reasoning of an essay in relation to a topic.

        Assesses the essay's logical flow, argument validity, and reasoning quality by sending
        it to an AI evaluation service. The evaluation can be customized with specific criteria.

        Args:
            topic: The topic or subject the essay should address.
            essay: The text content of the essay to be evaluated.
            criteria: List of evaluation criteria to assess. Defaults to:
                ["evidence", "coherence", "relevance", "critical_thinking"] if not provided.
                For pure logic evaluation, consider ["argument_structure", "fallacies", "reasoning"].

        Returns:
            dict: A dictionary containing:
                - status (bool): True if request was successful (HTTP 200), False otherwise
                - response (Union[requests.Response, dict]):
                    The full response object if successful, or error details if failed

        Raises:
            ConnectionError: If the request to the evaluation service fails.
            ValueError: If topic or essay is empty or None.
        """
        if not criteria:
            criteria = [
                "evidence",
                "coherence",
                "relevance",
                "critical_thinking",
            ]

        base_url = settings.AI_SERVICE_DEMO_URL

        if not str(base_url).endswith("/"):
            base_url += "/"

        base_url = base_url.removesuffix("/process/") + "/essay-evaluation/"

        if query_string:
            base_url += "?" + query_string

        try:
            response = requests.post(
                url=base_url,
                headers=headers,
                json={
                    "topic": topic,
                    "essay": essay,
                    "criteria": criteria,
                },
            )
        except ConnectionError:
            return {"status": False, "response": {"message": "connection error"}}
        if response.status_code == 200:
            return {"status": True, "response": response}
        else:
            return {"status": False, "response": response}

    def grammar(text_body: str, query_string: str = None):
        base_url: str = settings.AI_SERVICE_DEMO_URL

        if not str(base_url).endswith("/"):
            base_url += "/"

        base_url = base_url.removesuffix("/process/") + "/gammar/"
        if query_string:
            base_url += "?" + query_string

        response = requests.post(
            url=base_url,
            headers=headers,
            data={"speech": text_body},
        )

        if response.status_code == 200:
            return {"status": True, "response": response}

        else:
            return {"status": False, "response": response}
