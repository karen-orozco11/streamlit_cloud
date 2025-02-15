import openai
import os
import json

class SkillExtractor:
    def __init__(self):
        self.prompt_template = self.load_prompt_template()

    def load_prompt_template(self):
        with open('llm_extract_skills_data_scientist.txt', 'r') as file:
            return file.read()

    def extract_skills(self, resume):
        prompt = self.compose_prompt(resume)
        return self.query_chatgpt(prompt)

    def compose_prompt(self, resume):
        return self.prompt_template.format(resume=resume)

    def query_chatgpt(self, prompt):
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=1000  # Increased to accommodate JSON response
        )
        return self.parse_response(response.choices[0].text)

    def parse_response(self, response_text):
        try:
            # Parse the JSON response
            skills_data = json.loads(response_text)
            return skills_data.get("skills", [])
        except json.JSONDecodeError:
            # Handle parsing errors
            return []
