import os
from dotenv import load_dotenv

load_dotenv()


class DotDict(dict):
    """A dictionary that allows access to keys as attributes."""

    def __getattr__(self, key):
        if key in self:
            return self[key]
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value


def load_config():
    config = DotDict()

    config.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    return config


config = load_config()
os.environ["OPENAI_API_KEY"] = config.OPENAI_API_KEY
