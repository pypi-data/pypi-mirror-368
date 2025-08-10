import os


class ConfigLLM:
    USED_LLM: str | None = None


class ConfigGPT:
    MODEL_PRICE = {
        "gpt-3.5-turbo": {
            "input": 0.5 / 1000000,
            "output": 1.5 / 1000000,
        },
        "gpt-4o-mini": {
            "input": 0.15 / 1000000,
            "output": 0.60 / 1000000,
        },
    }
    """Price by one tokens from each model"""

    DEFAULT_MODEL_NAME = "gpt-4o-mini"
    """GPT model that will be used"""

    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    """OpenAI Api Key"""
