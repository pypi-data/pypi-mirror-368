from talkcode.core.config import get_ai_config
from talkcode.chat.prompts import SYSTEM_PROMPT, format_user_prompt

from openai import AzureOpenAI, OpenAI
from anthropic import Anthropic
import google.generativeai as genai


class MultiProviderAI:
    def __init__(self):
        try:
            config = get_ai_config()
            self.provider = config.get("provider", "azure").lower()
            self.api_key = config["api_key"]

            # Remove unsupported keys like 'proxies'
            config = {k: v for k, v in config.items() if k != "proxies"}

            if self.provider == "azure":
                self.client = AzureOpenAI(
                    api_key=self.api_key,
                    azure_endpoint=config["endpoint"],
                    api_version=config["api_version"]
                )
                self.model = config["deployment"]

            elif self.provider == "openai":
                self.client = OpenAI(api_key=self.api_key)  # Don't pass proxies
                self.model = config.get("deployment", "gpt-3.5-turbo")

            elif self.provider == "anthropic":
                self.client = Anthropic(api_key=self.api_key)
                self.model = config.get("model", "claude-3-opus-20240229")

            elif self.provider == "gemini":
                genai.configure(api_key=self.api_key)
                self.model = config.get("model", "gemini-pro")
                self.client = genai.GenerativeModel(self.model)

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            raise RuntimeError(f"AI config error: {e}")

    def ask(self, question: str, context: str = "") -> str:
        prompt = format_user_prompt(question, context)

        if self.provider in ["azure", "openai"]:
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT.strip()},
                {"role": "user", "content": prompt.strip()}
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content

        elif self.provider == "anthropic":
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt.strip()}
                ],
                system=SYSTEM_PROMPT.strip()
            )
            return response.content[0].text

        elif self.provider == "gemini":
            full_prompt = f"{SYSTEM_PROMPT.strip()}\n\n{prompt.strip()}"
            response = self.client.generate_content(full_prompt)
            return response.text

        else:
            raise RuntimeError(f"Unsupported provider: {self.provider}")
