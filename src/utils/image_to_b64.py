import os
import requests
from base64 import b64encode


def toB64(path_or_url: str):
    """
    Converts an image from a local file or a URL to a base64 string.

    Parameters:
    path_or_url (str): The path to a local file or a URL of an image.

    Returns:
    str: The base64 string of the image.
    """
    if os.path.isfile(path_or_url):
        # It's a local file path
        with open(path_or_url, "rb") as f:
            return b64encode(f.read()).decode()
    else:
        # It's a URL
        return b64encode(requests.get(path_or_url).content).decode()
