from architecture.chat_client import ChatClient
import streamlit as st
import pandas as pd
import json



def main():
    if "chat" not in st.session_state:
        st.session_state.chat = ChatClient()

    chat = st.session_state.chat

    # Maximize page width
    st.set_page_config(layout="wide")

    st.title("DatabaseChat")

    st.markdown("---")

    with st.container():
        col_left, col_middle, col_right = st.columns([3, 0.5, 3])

        with col_right:
            col1, col2 = st.columns([5, 1])
            with col1:
                st.subheader("Chat")
            with col2:
                st.write("")
                if st.button("Reset", use_container_width=True):
                    chat.clear_history()                

            prompt = st.chat_input("Tell me what to do:")
            raw_response = ""
            if prompt:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    with st.spinner(text="Waiting for the response..."):
                        raw_response = chat.ask_gemini(prompt=prompt)
                    
                    if raw_response:
                        raw_response = raw_response.strip()
                        if raw_response.startswith("```json"):
                            raw_response = raw_response[len("```json"):].strip()
                        if raw_response.endswith("```"):
                            raw_response = raw_response[:-3].strip()

                        decoded_response = json.loads(raw_response)
                        data_response = decoded_response['data']
                        explanation_response = decoded_response['explanation']

                        players_response = data_response['players']
                        teams_response = data_response['teams']
                        league_response = data_response['leagues']

                        st.markdown(explanation_response)

        with col_left:
            if raw_response:
                players_df = pd.DataFrame(players_response)
                teams_df = pd.DataFrame(teams_response)
                league_df = pd.DataFrame(league_response)

            else:
                players_df = pd.DataFrame([])
                teams_df = pd.DataFrame([])
                league_df = pd.DataFrame([])

            st.subheader("Players DataFrame")
            st.dataframe(players_df, use_container_width=True)
            st.subheader("Teams DataFrame")
            st.dataframe(teams_df, use_container_width=True)
            st.subheader("Leagues DataFrame")
            st.dataframe(league_df, use_container_width=True)



if __name__ == "__main__":
    main()