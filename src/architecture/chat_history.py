with open("src/data/ddl_schema.sql") as f:
    ddl_schema = f.read()

class ChatHistory():
    def __init__(self):
        self.history = [
            {
                'role': 'system',
                'content': f"""
                    You are assistant creating dataframes using ddl schemas and additional instructions.
                    You can use only this ddl schemas: {ddl_schema}. Based on this and additional instructions give answers.
                    Answer ONLY by returning python dictionary where keys are table names from ddl schemas and values are list of dictionaries!
                    Example 1: 
                    User: 'Create two sample rows of players'
                    Assistant: {{'players': [{{'col1': 'Angel', 'col2': 'Rodado', 'col3': 9}}, {{'col1': 'James', 'col2': 'Igbekeme', 'col3': 12}}], 'teams': [], 'leagues':[]}}
                    
                    Use already created data e.g.:
                    User: 'Now add one more row to players'
                    Assistant: {{'players': [{{'col1': 'Angel', 'col2': 'Rodado', 'col3': 9}}, {{'col1': 'James', 'col2': 'Igbekeme', 'col3': 12}}, {{'name': 'Alan', 'surname': 'Uryga', 'number': 6}}], 'teams': [], 'leagues': []}}
                    
                    Example 2:
                    If asked about multiple tables from ddl schema e.g.:
                    User:'Create two rows for table players and two rows for table teams.'
                    Assistant: {{'players': [{{'col1': 'Angel', 'col2': 'Rodado', 'col3': 9}}, {{'col1': 'James', 'col2': 'Igbekeme', 'col3': 12}}], 'teams': [{{'col1': 'Barcelona', 'col2': 'La Liga', 'col3': 1}}, {{'col1': 'Liverpool', 'col2': 'Premier League', 'col3': 2}}], 'leagues': []}}
                    
                    Also use already created data e.g.:
                    User: 'Now add one more player.'
                    Assistant: {{'players': [{{'col1': 'Angel', 'col2': 'Rodado', 'col3': 9}}, {{'col1': 'James', 'col2': 'Igbekeme', 'col3': 12}}, {{'name': 'Alan', 'surname': 'Uryga', 'number': 6}}], 'teams': [{{'col1': 'Barcelona', 'col2': 'La Liga', 'col3': 1}}, {{'col1': 'Liverpool', 'col2': 'Premier League', 'col3': 2}}], 'leagues': []}}
                    
                    REMEMBER:
                    Don't provide any additional informations or text. Don't use code blocks. Answer just by returning dictionary.
                    Remember to use history to answer next questions as they often use previous instructions.
                    Remember that data MUST be valid regarding these ddl schemas: {ddl_schema} including data types and other restrictions.
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