import requests

from youtube_summarizer.prompts import PROMPTS

api_base_url = "http://127.0.0.1:5000"


def summarize(model: str, transcription_text: str):
    check_ollama_running()
    prompt_text = PROMPTS.replace("{transcription_text}", transcription_text)
    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "keep_alive": "5s",
    }
    request_url = api_base_url + "/api/generate"
    response = requests.post(request_url, json=payload)
    return response


def check_ollama_running():
    api_response = requests.get(api_base_url, timeout=5)
    if api_response.status_code == 200 and api_response.text == "Ollama is running":
        print("API endpoint is running.")
    else:
        raise OllamaConnectionError()


class OllamaConnectionError(Exception):
    pass
