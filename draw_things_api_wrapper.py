import hashlib
import diskcache as dc
from templater import ParamsTemplate
import json
import requests
import logging

class DrawThingApiWrapper:
    def __init__(self, txt2img_endpoint, prompt_generator, templater):
        self.prompt_generator = prompt_generator
        self.logger = logging.getLogger(__name__)
        self.params_template = templater
        self.txt2img_endpoint = txt2img_endpoint
        self.cache = dc.Cache(directory='cache_directory')  # Replace 'cache_directory' with your cache directory path

    def _get_cache_key(self, message):
        # Create a hash key from the prompt and negative prompt
        return hashlib.md5(message.encode('utf-8')).hexdigest()

    def send_request(self, payload):
        cache_key = self._get_cache_key(json.dumps(payload))
        cached_response = self.cache.get(cache_key)
        if cached_response is not None:
            return cached_response  # Return cached response if available

        try:
            response = requests.post(self.txt2img_endpoint, json=payload)
            response.raise_for_status()
        except requests.RequestException as e:
            self.logger.error(f"Failed to send request: {e}")
            return None

        images = response.json().get('images', [None])
        self.cache.set(cache_key, images)  # Cache the response
        return images

    def parse_params(self, params):
        """Parse parameters, converting to int/float where possible."""
        for key, value in params.items():
            try:
                params[key] = int(value)
            except ValueError:
                try:
                    params[key] = float(value)
                except ValueError:
                    pass  # keep as string if it's not a number
        return params

    def optimize_prompts(self, params, batch_count):
        """Generate and return multiple optimized prompts."""
        prompt_prefix = params.get("prompt_prefix", '')
        base_prompt = prompt_prefix + " " + params['prompt']

        # Check if prompt_generator is set
        if hasattr(self, 'prompt_generator') and self.prompt_generator:
            generated_texts = self.prompt_generator.generate_text(
                base_prompt, num_return_sequences=batch_count
            )
        else:
            # If prompt_generator is not set, return base_prompt repeated batch_count times
            generated_texts = [base_prompt] * batch_count

        sanitized_texts = [self.sanitize_text(text) for text in generated_texts]
        self.logger.info(f"Generated enhanced prompts from {base_prompt}: {sanitized_texts}")
        return sanitized_texts

    def sanitize_text(self, text):
        """Remove unwanted characters from the text."""
        return text.replace('"', '')

    def get_generation_request_json(self, message_text):
        """Generate the request payload(s) based on provided message_text."""
        params = self.params_template.parse_generation_message(message_text)
        params = self.parse_params(params)

        if "prompt" not in params:
            params['prompt'] = message_text

        batch_count = params.get("batch_count", 1)
        generate_separately = params.get("generate_separately", False)
        optimize_prompt = params.get("optimize_prompt", False)

        # Case 1: Optimize prompt & generate separately
        if optimize_prompt and generate_separately:
            return self.generate_separate_optimized_payloads(params, batch_count)

        # Case 2: Optimize prompt only
        if optimize_prompt:
            optimized_prompt = self.optimize_prompts(params, 1)[0]  # Get single optimized prompt
            return [self.params_template.render_api_params({**params, "prompt": optimized_prompt})]

        # Case 3: Generate separately only
        if generate_separately:
            return self.generate_separate_payloads(params, batch_count)

        # Default case: No optimization and no separate generation
        return [self.params_template.render_api_params(params)]

    def generate_separate_optimized_payloads(self, params, batch_count):
        optimized_prompts = self.optimize_prompts(params, batch_count)
        # Create separate payloads for each optimized prompt with batch_count set to 1
        return [self.params_template.render_api_params({**params, "prompt": prompt, "batch_count": 1}) for prompt in
                optimized_prompts]

    def generate_separate_payloads(self, params, batch_count):
        # Create separate payloads with the same prompt with batch_count set to 1
        return [self.params_template.render_api_params({**params, "batch_count": 1}) for _ in range(batch_count)]