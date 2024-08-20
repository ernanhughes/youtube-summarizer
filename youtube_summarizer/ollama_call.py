import ollama


def get_model(name: str = "llama3.1"):
    ollama.pull(name)


def chat_with_model(model: str, messages):
    response = ollama.chat(model, messages)
    print(response)
    return response
