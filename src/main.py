from architecture.chat_client import ChatClient
import streamlit as st
import pandas as pd
import ast



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

            # Display message history
            # for message in chat.history.get_history():
            #     if message["role"] != 'system':
            #         with st.chat_message(message["role"]):
            #             st.markdown(message["content"])

            prompt = st.chat_input("Tell me what to do:")
            full_response = ""
            if prompt:
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.chat_message("assistant"):
                    # response_placeholder = st.empty()
                    # full_response = ""
                    # for chunk in chat.ask_gpt(prompt=prompt):
                    #     full_response += chunk
                    #     response_placeholder.markdown(full_response)
                    with st.spinner(text="Waiting for the response..."):
                        full_response = chat.ask_gpt(prompt=prompt)
                        print(full_response)
                    
                    if full_response:
                        decoded_response = ast.literal_eval(full_response)
                        data_response = decoded_response['data']
                        explanation_response = decoded_response['explanation']

                        players_response = data_response['players']
                        teams_response = data_response['teams']
                        league_response = data_response['leagues']

                        st.markdown(explanation_response)

        with col_left:
            if full_response:
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