class ChatHistory():
    def __init__(self):
        self.history = []

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