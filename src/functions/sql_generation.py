from google.genai import types
from dotenv import load_dotenv
import logging
import os
import pandas as pd
from sqlalchemy import text, create_engine
from architecture.chat_history import Instructions

load_dotenv()


def generate_query(client, user_query, ddl_schema):
        contents = [types.Content(parts=[types.Part(text=f"Generate SQL query for this setup.\nDDL schema: {ddl_schema}.\nUser query: {user_query}")], role='user')]
        system_instruction = Instructions().get_sql_config()

        response = client.models.generate_content(
            model="gemini-2.0-flash",
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

        if response_text.startswith("```sql"):
            response_text = response_text[len("```sql"):].strip()
        if response_text.endswith("```"):
            response_text = response_text[:-3].strip()
        

        with engine.connect() as connection:
            df = pd.read_sql(text(response_text), connection)

        return response_text, df