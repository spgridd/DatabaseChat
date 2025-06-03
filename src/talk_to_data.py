import streamlit as st
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine
import pandas as pd
from google.genai import types
from architecture.chat_client import ChatClient
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)


def main():
    try:
        if "contents" not in st.session_state:
            st.session_state.contents = []
        
        contents = st.session_state.contents
        schema = st.session_state.ddl_schema
        chat = st.session_state.chat

        prompt = st.chat_input("Ask me something about data...")

        for message in chat.history.get_history():
            if message["role"] != 'system':
                with st.chat_message(message["role"]):
                    if type(message["content"]) == str:
                        if message["content"].startswith("outputs/"):
                            st.image(message["content"])
                        else:
                            st.markdown(message["content"])
                    else:
                        st.code(message['content'][0], language='sql')
                        st.dataframe(message['content'][1])

        if prompt:
            with st.chat_message("user"):
                # contents.append(types.Content(parts=[types.Part(text=prompt)], role='user'))
                st.markdown(prompt)

            with st.chat_message('assistant'):
                response = chat.talk_with_data(user_query=prompt, ddl_schema=schema, contents=contents)

                if len(response) == 2:
                    path, contents = response
                    print(f"\nPATH:{path}\n")
                    st.image(path)

                else:
                    query, df, contents = response

                    st.code(query, language='sql')
                    st.dataframe(df)
    
    except AttributeError as e:
        st.error("You have to provide DDL schema first.")
        logging.info(e)
    
    except Exception as e:
        st.error("Some error occured. Try again.")
        logging.info(e)