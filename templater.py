from jinja2 import Environment, FileSystemLoader
import re
import json
import logging

class ParamsTemplate:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.env = Environment(loader=FileSystemLoader('.'))

    def render_help(self):
        result = self.__render_template({}, './resource/tg_templates/help.j2')
        self.logger.debug(f"Rendering help: {result}")
        return result

    def render_api_params(self, params):
        jsonstr = self.__render_template(params, './resource/generation_template.j2')
        self.logger.debug(f"Produced json: {jsonstr}")
        return json.loads(jsonstr)

    def __render_template(self, params, template_name):
        template = self.env.get_template(template_name)
        rendered_str = template.render(params)
        return rendered_str

    @staticmethod
    def parse_generation_message(message):
        """
        Parses a message string and returns a dictionary of key-value pairs.

        Args:
        - message (str): A string containing key-value pairs in the format "key: value".

        Returns:
        dict: A dictionary where the keys are the keys from the message, and the values are the values from the message.
        """
        # Regular expression to extract "key: value" pairs
        pattern = re.compile(r"(\w+):\s*([^:]*)(?=\s+\w+:|$)")

        # Find all matches in the message
        matches = pattern.findall(message)

        # Convert matches to a dictionary and return
        return {key: value.strip() for key, value in matches}