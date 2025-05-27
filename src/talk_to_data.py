import streamlit as st
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import pandas as pd
from architecture.chat_client import ChatClient

load_dotenv()


def main():
    schema = st.session_state.ddl_schema
    chat = st.session_state.chat

    prompt = st.chat_input("Ask me something about data...")

    for message in chat.history.get_history():
        if message["role"] != 'system':
            with st.chat_message(message["role"]):
                if type(message["content"]) == str:
                    st.markdown(message["content"])
                else:
                    st.markdown(message['content'][0])
                    st.dataframe(message['content'][1])

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message('assistant'):
            query, df = chat.sql_generation(user_query=prompt, ddl_schema=schema)

            st.markdown(query)

            st.dataframe(df)