from google.genai import types
from dotenv import load_dotenv
import logging
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import traceback
import uuid
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from architecture.chat_history import Instructions

load_dotenv()


def generate_plot(client, user_query, ddl_schema, df, error, contents):
    prompt = f"Generate python plot code for this setup.\nDDL schema: {ddl_schema}.\nUser query: {user_query}.\nDataframe: {df}"
    if error != 'first_run':
        prompt += f"\nPreviously your code generated those errors: {error}. Fix them."

    contents.append(types.Content(parts=[types.Part(text=prompt)], role='user'))
    system_instruction = Instructions().get_plot_config()
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.0
        )
    )

    response_text = response.candidates[0].content.parts[0].text

    if response_text.startswith("```python"):
        response_text = response_text[len("```python"):].strip()
    if response_text.endswith("```"):
        response_text = response_text[:-3].strip()

    plot_variables = {"df": df, "pd": pd, "sns": sns}

    try:
        plt.clf()

        exec(response_text, {}, plot_variables)

        os.makedirs("outputs/generated_plots", exist_ok=True)
        plot_path = f"outputs/generated_plots/{uuid.uuid4().hex[:8]}.png"
        plt.savefig(plot_path)

        return plot_path, None, contents

    except Exception as e:
        logging.error(f"Error: {e}")
        return None, e, contents