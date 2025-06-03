from google.genai import types
from dotenv import load_dotenv
import logging
import os
import pandas as pd
from sqlalchemy import text, create_engine
from sqlalchemy.exc import SQLAlchemyError
from architecture.chat_history import Instructions

load_dotenv()


def generate_query(client, user_query, ddl_schema, error, contents, for_plot):
        if error == 'first_run':
            prompt = (
                f"Generate a valid PostgreSQL SQL query.\n"
                f"User request: {user_query}\n"
                f"DDL schema: {ddl_schema}"
            )
        else:
            prompt = (
                f"The previous query resulted in this error:\n{error}\n"
                f"Please regenerate a valid, fixed SQL query based on the original request:\n"
                f"{user_query}\n"
            )

        contents.append(types.Content(parts=[types.Part(text=prompt)], role='user'))

        if for_plot:
            system_instruction = Instructions().get_sql_config(for_plot=for_plot)
        else:
            system_instruction = Instructions().get_sql_config(for_plot=for_plot)

        response = client.models.generate_content(
            model="gemini-2.5-flash-preview-05-20",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.0
            )
        )

        user = os.getenv("POSTGRESQL_USER")
        password = os.getenv("POSTGRESQL_PASSWORD")
        db = os.getenv("POSTGRESQL_DB")
        engine = create_engine(f"postgresql+psycopg2://{user}:{password}@localhost:5432/{db}")

        response_text = response.candidates[0].content.parts[0].text

        contents.append(types.Content(parts=[types.Part(text=response_text)], role='model'))

        if response_text.startswith("```sql"):
            response_text = response_text[len("```sql"):].strip()
        if response_text.startswith("```postgresql"):
            response_text = response_text[len("```sql"):].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()
        
        try:
            with engine.connect() as connection:
                logging.info("\nCONNECTED SQL\n")
                try:
                    df = pd.read_sql(text(response_text), connection)
                    return response_text, df, None, contents
                except Exception as e:
                    logging.info(f"\nSOME ERROR: {e}")
                    return None, None, str(e), contents
        except SQLAlchemyError as e:
            return None, None, str(e), contents