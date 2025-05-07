from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()
openai_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_key)

def ask_gpt(prompt):
    """
    Ask gpt model given question and receive answer.
    """
    response = client.chat.completions.create(
        model='gpt-4.1-mini',
        messages=[
            {'role': 'user', 'content': prompt}
        ]
    )

    return response.choices[0].message.content