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

        # Retrying for 5 times if it fails
        for i in range(6):
            if i != 0:
                print(f"Retying for {i}th time")
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=self.history,
                )
                break
            except Exception as e:
                print(f"Attempt failed with error: {e}. Retrying...")

        else:
            raise Exception("All attempts failed.")

        # Append the assistant's response to the history
        self.history.append(
            {"role": "assistant", "content": response.choices[0].message.content}
        )

        return response.choices[0].message.content
