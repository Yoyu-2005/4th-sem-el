# main.py

import time
import threading
import gradio as gr
import requests
from log_utils import ingest_windows_logs, collection

# Optional: Use ngrok for public sharing
from pyngrok import ngrok

# Add your ngrok authentication token
ngrok.set_auth_token("2vMfgK6Hp95o62hSnMnR1U6WhC5_5APzwqpTpGdyi6ZsDKE4K")
public_url = ngrok.connect(7860)
print(f"Gradio running on: {public_url}")

# Background task: refresh logs every 60 seconds
def start_log_monitor(interval=60):
    while True:
        ingest_windows_logs()
        print("[+] Ingested system logs!")
        time.sleep(interval)

# Start in background
threading.Thread(target=start_log_monitor, daemon=True).start()

# LLM query function using OpenRouter (or switch to local llama-cpp if needed)
def ask_logs(query):
    results = collection.query(query_texts=[query], n_results=3)
    context = "\n".join(results["documents"][0])

    # Simple OpenRouter call (replace YOUR_API_KEY)
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": "Bearer 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"},
        json={
            "model": "mistralai/mistral-7b-instruct",
            "messages": [
                {"role": "system", "content": "You are a helpful log analysis assistant."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {query}"}
            ]
        }
    )
    return response.json()["choices"][0]["message"]["content"]

# Gradio Interface
iface = gr.Interface(fn=ask_logs, inputs="text", outputs="text", title="LogLLM: Windows Log Analyzer")
iface.launch(server_name="0.0.0.0", server_port=7860)
