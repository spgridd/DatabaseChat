from chat import ChatClient

def main():
    chat = ChatClient()

    print("Welcome! Type your question or type 'exit' to quit.")
    
    while True:
        prompt = input("User: ")
        if prompt.lower() == 'exit':
            break
        reply = chat.ask_gpt(prompt=prompt)
        print(f"System: {reply}")


if __name__ == "__main__":
    main()