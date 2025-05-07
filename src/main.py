from chat import ask_gpt

def main():
    print("Welcome! Type your question or type 'exit' to quit.")
    
    while True:
        prompt = input("User: ")
        if prompt.lower() == 'exit':
            break
        reply = ask_gpt(prompt=prompt)
        print(f"System: {reply}")


if __name__ == "__main__":
    main()