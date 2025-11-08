from openai import OpenAI
from dotenv import load_dotenv
import json

load_dotenv()

class LLMInteraction:
    def __init__(self):
        self.client = OpenAI()
        self.system_prompt = (
            "You are a network traffic analyzer. "
            "You receive logs, packets, or event patterns. "
            "Your task is to analyze and describe what is happening clearly and concisely. "
            "Detect possible anomalies, attacks, or unusual behavior. "
            "Return only factual analysis without small talk, your response will be transformed to JSON."
            "MUST Respond in JSON format with keys: 'alert_title', 'alert_description', 'severity_level' and 'recommended'."
            "MUST alert-title gives a brief summary of the alert, 2-5 words. alert-description gives a detailed description of the alert, 10-20 words. severity-level is one of: low, medium, high. recommended gives recommended actions to take, 10-20 words."
        )

    def str_to_json(self, string: str) -> dict:
        """Convert string to JSON and validate required alert format.
        Returns None if JSON is invalid or missing required fields."""
        try:
            data = json.loads(string)
            # required keys exist
            required_keys = {'alert_title', 'alert_description', 'severity_level', 'recommended'}
            if not all(key in data for key in required_keys):
                return None
            
            # severity level is valid
            if data['severity_level'] not in {'low', 'medium', 'high'}:
                return None

            # return only the required fields
            return {
                'alert_title': data['alert_title'],
                'alert_description': data['alert_description'],
                'severity_level': data['severity_level'],
                'recommended': data['recommended']
            }
        except json.JSONDecodeError:
            return None

    def ask_llm(self, pattern: str):
        """Send a prompt to the LLM and return the response as a JSON object.
        Returns None if the response cannot be parsed as JSON."""
        response = self.client.responses.create(
            model="gpt-5",
            input=[
                {
                    "role": "system",
                    "content": [{"type": "input_text", "text": self.system_prompt}]
                },
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": pattern}]
                }
            ]
        )
        return self.str_to_json(response.output_text)
