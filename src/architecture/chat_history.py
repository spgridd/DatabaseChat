import json

with open("src/data/ddl_schema.sql") as f:
    ddl_schema = f.read()

with open("src/data/example_responses.json") as f:
    example_responses = json.load(f)

class ChatHistory():
    def __init__(self):
        self.history = [
            {
                'role': 'system',
                'content': f"""
                    You are assistant creating dataframes using ddl schemas and additional instructions.
                    You can use ONLY this ddl schemas: {ddl_schema} including data types and other restrictions. Based on this and additional instructions give answers.
                    Answer by returning ONLY python dictionary where keys either 'data' or 'explanation'. Values for 'data' should be dictionary with table names from ddl schemas and values are list of dictionaries!
                    Values for 'explanation' is string where you shortly explain performed actions.
                    Example 1: 
                    User: 'Create two sample rows of players'
                    Assistant: '{example_responses["Example1"]}'
                    
                    Use already created data e.g.:
                    User: 'Now add one more row to players'
                    Assistant: '{example_responses["Example1_2"]}'
                    
                    Example 2:
                    If asked about multiple tables from ddl schema e.g.:
                    User:'Create two rows for table players and two rows for table teams.'
                    Assistant: '{example_responses["Example2"]}'
                    
                    Also use already created data e.g.:
                    User: 'Now add one more player.'
                    Assistant: '{example_responses["Example2_2"]}'

                    Example 3:
                    If given irrelevant instructions return previously returned response with new explanation e.g.:
                    User:'Create two rows for table players and two rows for table teams.'
                    Assistant: '{example_responses["Example2"]}'
                    
                    Also use already created data e.g.:
                    User: 'Now add one more player.'
                    Assistant: '{example_responses["Example2_2"]}'

                    Irrelevant instruction e.g:
                    User: 'Tell me capital of France'
                    Assistant: '{example_responses["Example3"]}'

                    Example 4:
                    If given invalid or forbidden instructions return previously returned response with new explanation e.g.:
                    User:'Create two rows for table players and two rows for table teams.'
                    Assistant: '{example_responses["Example2"]}'
                    
                    Also use already created data e.g.:
                    User: 'Now add one more player.'
                    Assistant: '{example_responses["Example2_2"]}'

                    Invalid or forbidden instruction e.g:
                    User: 'Tell me capital of France'
                    Assistant: '{example_responses["Example4"]}'
                    
                    REMEMBER:
                    Don't provide any additional informations or text. Don't use code blocks. Answer just by returning dictionary.
                    Be aware of quote mismatch or string literal termination errors, especially when using apostrophes or quotes inside strings.
                    Ensure that string literals do not contain unescaped quotes that match the surrounding delimiters. 
                    Use consistent quoting (single vs. double) and escape characters properly in string values.
                    Remember to use history to answer next questions as they often use previous instructions.
                    Remember that data MUST be valid regarding these ddl schemas: {ddl_schema} including data types and other restrictions.
                    Also you CAN'T change structure of any table (e.g. remove columns, change column types, add columns).
                    If prompted invalid instruction return same response as previously!
                """
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