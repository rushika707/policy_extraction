import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()




class RegoGenerator:

    def __init__(self, model=None, client=None):
        self.model = model or os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

        self.client = client or Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.prompt_path = Path(
            "prompts/rego_generation.txt"
        )

    def load_prompt(self):
        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt not found: {self.prompt_path}"
            )

        return self.prompt_path.read_text(
            encoding="utf-8"
        )

    def generate(self, policy_data):
        if not policy_data:
            raise ValueError(
                "Policy JSON cannot be empty."
            )

        prompt_template = self.load_prompt()

        policy_json = json.dumps(
            policy_data,
            indent=2,
            ensure_ascii=False
        )

        prompt = prompt_template.replace(
            "{{POLICY_JSON}}",
            policy_json
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_completion_tokens=8192,
            reasoning_effort="low",
            include_reasoning=False
        )

        content = (
            response
            .choices[0]
            .message
            .content
        )

        if not content:
            raise ValueError(
                "Groq returned an empty Rego response."
            )

        return self._clean_rego(content)

    def _clean_rego(self, content):
        """
        Remove accidental Markdown fences if the model
        returns them despite the prompt.
        """

        content = content.strip()

        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        if not content:
            raise ValueError(
                "Generated Rego is empty."
            )

        return content

    def generate_from_file(
        self,
        policy_path,
        output_path
    ):
        policy_path = Path(policy_path)
        output_path = Path(output_path)

        if not policy_path.exists():
            raise FileNotFoundError(
                f"Policy JSON not found: {policy_path}"
            )

        with open(
            policy_path,
            "r",
            encoding="utf-8"
        ) as file:
            policy_data = json.load(file)

        rego = self.generate(policy_data)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        output_path.write_text(
            rego,
            encoding="utf-8"
        )

        return rego