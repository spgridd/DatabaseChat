from architecture.chat_client import ChatClient
import streamlit as st
import pandas as pd
import ast


df_temp = pd.DataFrame(
    [
        # {'name': 'Angel', 'surname': 'Rodado', 'number': 9},
        # {'name': 'James', 'surname': 'Igbekeme', 'number': 12},
        # {'name': 'Alan', 'surname': 'Uryga', 'number': 6}
    ]
)

def main():
    if "chat" not in st.session_state:
        st.session_state.chat = ChatClient()

    chat = st.session_state.chat

    # Maximize page width
    st.set_page_config(layout="wide")

    with st.container():
        col1, col2 = st.columns([6, 1])
        with col1:
            st.title("DatabaseChat")
        with col2:
            st.write("")
            st.write("")
            if st.button("Reset"):
                chat.clear_history()

    st.markdown("---")

    with st.container():
        col_left, col_middle, col_right = st.columns([3, 0.5, 3])

        with col_right:
            st.subheader("Chat")

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
                # decoded_response = ast.literal_eval(full_response)
                # players_response = decoded_response['players']
                # teams_response = decoded_response['teams']
                # league_response = decoded_response['leagues']

                players_df = pd.DataFrame(players_response)
                teams_df = pd.DataFrame(teams_response)
                league_df = pd.DataFrame(league_response)

                st.subheader("Players DataFrame")
                st.dataframe(players_df, use_container_width=True)
                st.subheader("Teams DataFrame")
                st.dataframe(teams_df, use_container_width=True)
                st.subheader("Leagues DataFrame")
                st.dataframe(league_df, use_container_width=True)
            else:
                current_df = df_temp
            # st.subheader("DataFrame")
            # st.dataframe(current_df, use_container_width=True)

if __name__ == "__main__":
    main()
