from chat_client import ChatClient
import streamlit as st

# def main():
#     chat = ChatClient()

#     print("Welcome!\n"
#           "Type 'exit' to quit and 'clear' to reset history.\n")
    
#     while True:
#         prompt = input("User: ")
#         if prompt.lower() == 'exit':
#             break

#         elif prompt.lower() == 'clear':
#             chat.clear_history()
#             print("\nChat history cleared!\n")
#             continue

#         reply = chat.ask_gpt(prompt=prompt)
#         print(f"Assistant: {reply}")
    
#     print("\nExited successfully!\n")


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

        reply = chat.ask_gpt(prompt=prompt)

        with st.chat_message("assistant"):
            st.markdown(reply)



if __name__ == "__main__":
    main()