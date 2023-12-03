import os

from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()


class GPT3Chat:
    def __init__(self, model: str = "gpt-3.5-turbo", set_context: str = ""):
        if set_context == "":
            self.history = [
                {"role": "system", "content": "You are a helpful assistant."},
            ]
        else:
            self.history = [
                {"role": "system", "content": set_context},
            ]
        self.model = model

    def get_response(self, message: str):
        """
        Example of how messages argument should be
        history = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {
                "role": "assistant",
                "content": "The Los Angeles Dodgers won the World Series in 2020.",
            },
            {"role": "user", "content": "Where was it played?"},
        ]
        """
        self.history.append({"role": "user", "content": message})

        response = client.chat.completions.create(
            model=self.model,
            messages=self.history,
        )

        # Append the assistant's response to the history
        self.history.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )

        return response.choices[0].message.content


if __name__ == "__main__":
    message = """
    Below is the English translation of my first three verse of hindi rap track, "Karna kya hai tujhe?"
    I want to create a rap video for the same. Story board the verse so I can create a rap video out of it.
    
    Go to club and play the music or
    Let's Eat and enjoy or
    Let's smoke and chill in my Pjs
    My friend asked me what I want to do

    What to do? What to do? What to do?
    My friend asked me what I want to do
    What to do? What to do? What to do?
    My friend asked me what I want to do

    Go to club and play the music or
    Let's Eat and enjoy or
    Let's smoke and chill in my Pjs
    My friend asked me what I want to do
    """
    print(get_gpt_3_5_resp(message))
