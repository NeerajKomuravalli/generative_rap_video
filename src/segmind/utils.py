import os
import random

from dotenv import load_dotenv

load_dotenv()


def choose_api_key():
    """
    Choose a random API key from the list of API keys.
    """
    # NOTE: TODO: Add a check if the API key is valid or not. Also check is free credits are available for the KEY
    return random.choice(os.environ["SEGMIND_API_KEYS"].split(","))
