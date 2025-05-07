from chat import ChatClient

def main():
    chat = ChatClient()

    print("Welcome!\n"
          "Type 'exit' to quit and 'clear' to reset history.")
    
    while True:
        prompt = input("User: ")
        if prompt.lower() == 'exit':
            break

        elif prompt.lower() == 'clear':
            chat.clear_history()
            print("\nChat history cleared!\n")
            continue

        reply = chat.ask_gpt(prompt=prompt)
        print(f"Assistant: {reply}")
    
    print("\nExited successfully!\n")



if __name__ == "__main__":
    main()