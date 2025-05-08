from chat_client import ChatClient
import streamlit as st


def main():
    if "chat" not in st.session_state:
        st.session_state.chat = ChatClient()

    chat = st.session_state.chat

    header = st.container()

    _, col2, col3 = header.columns([0.05, 0.8, 0.15])

    with col2:
        st.title("DatabaseChat")
    with col3:
        st.write("")
        st.write("")
        if st.button("Clear"):
            chat.clear_history()

    for message in chat.history.get_history():
        if message["role"] != 'system':
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Ask me something:")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            responce_placeholder = st.empty()

            full_response = ""
            for chunk in chat.ask_gpt(prompt=prompt):
                full_response += chunk
                responce_placeholder.markdown(full_response)



if __name__ == "__main__":
    main()