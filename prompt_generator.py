import requests
import json


class PromptGenerator:
    def __init__(self, api_url):
        self.api_url = api_url

    def generate_text(self, prompt, temperature=0.9, top_k=80, max_length=80,
                      repetition_penalty=1.2, num_return_sequences=5):
        """
        Generate text based on the input prompt and other parameters.

        Parameters:
            prompt (str): The input prompt.
            temperature (float, optional): Controls diversity. Defaults to 0.9.
            top_k (int, optional): Number of tokens to sample from at each step. Defaults to 80.
            max_length (int, optional): Max output length. Defaults to 80.
            repetition_penalty (float, optional): Penalty for repeated tokens. Defaults to 1.2.
            num_return_sequences (int, optional): Number of results to generate. Defaults to 5.

        Returns:
            List[str]: Generated text sequences.
        """
    # Check for request count required given the num_return_sequences
        request_count = (num_return_sequences + 4) // 5
        results = []

        payload_base = {
            'prompt': prompt,
            'temperature': temperature,
            'top_k': top_k,
            'max_length': max_length,
            'repetition_penalty': repetition_penalty
        }

        def _fetch_sequences(count):
            payload = {**payload_base, 'num_return_sequences': count}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.api_url, headers=headers, data=json.dumps(payload))

            # Check for request failure
            if response.status_code != 200:
                raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

            return response.json()

        for i in range(request_count):
            # Check if this is the last iteration and set sequences to the remainder
            sequences = 5 if i < request_count - 1 else num_return_sequences % 5 or 5
            results.extend(_fetch_sequences(sequences))

        return results
