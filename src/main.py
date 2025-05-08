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
    chat = ChatClient()

    st.title("DatabaseChat")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    prompt = st.chat_input("Ask me something:")

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({'role': 'user', 'content': prompt})

        reply = chat.ask_gpt(prompt=prompt)

        with st.chat_message("assistant"):
            st.markdown(reply)

        st.session_state.messages.append({"role": "assistant", "content": reply})



if __name__ == "__main__":
    main()