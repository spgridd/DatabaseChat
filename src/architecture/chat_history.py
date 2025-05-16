import json


with open("src/data/ddl_schema.sql") as f:
    ddl_schema = f.read()

with open("src/data/example_responses.json") as f:
    example_responses = json.load(f)


class Instructions():
    def __init__(self):
        self.config = ""


    def get_generate_config(self, ddl):
        self.generate_config = f"""
            You are an AI assistant that analyzes this database schema: {ddl} and user questions to produce structured data.
            Always respond in **valid JSON format** with this structure:

            {{
            "data": {{
                "<table_name_1>": [<rows_as_dicts>],
                "<table_name_2>": [<rows_as_dicts>],
                ...
            }}
            }}

            - The table names must match the actual table names in the current schema.
            - Each table should be returned as a list of dictionaries (like JSON records).
            - Return only valid JSON, without markdown code blocks or extra formatting.
            - Do not use triple backticks (```) or language identifiers like ```json.
            - Escape all backslashes and quotes properly according to JSON rules.
            - Ensure the JSON parses correctly with `json.loads()` in Python.
        """
        return self.generate_config
    

    def get_edit_config(self, dataframes):
        self.edit_config = f"""
            You are an AI assistant that analyzes this json dataframes: {dataframes} and user questions to APPLY CHANGES FOR EXISTING structured data.
                        Always respond in **valid JSON format** with this structure:

            {{
            "data": {{
                "<table_name_1>": [<rows_as_dicts>],
                "<table_name_2>": [<rows_as_dicts>],
                ...
            }}
            }}

            - The table names must match the actual table names in the current schema.
            - Each table should be returned as a list of dictionaries (like JSON records).
            - You MUST preserve all tables and their existing data, even if no changes are made to them.
            - Only apply the required changes to the relevant table(s); all others should remain exactly as in the input.
            - Return only valid JSON, without markdown code blocks or extra formatting.
            - Do not use triple backticks (```) or language identifiers like ```json.
            - Escape all backslashes and quotes properly according to JSON rules.
            - Ensure the JSON parses correctly with `json.loads()` in Python.
        """
        return self.edit_config


class ChatHistory():
    def __init__(self):
        self.instructions = Instructions()
        self.history = [
            {
                'role': 'system',
                'content': self.instructions.system_config
            }
        ]

    def add_message(self, role, content):
        """
        Add message to the existing conversation.
        """
        self.history.append({'role': role, 'content': content})

    def clear_history(self):
        """
        Clear the history of the conversation.
        """
        self.history = []

    def get_history(self):
        """
        Return the history of the conversation.
        """
        return self.history