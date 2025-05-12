# log_utils.py

import win32evtlog
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
import chromadb

# Setup ChromaDB client and collection
client = chromadb.Client()
collection = client.get_or_create_collection("windows_logs", embedding_function=SentenceTransformerEmbeddingFunction())

def embed_and_store_log(log_text):
    collection.add(documents=[log_text], ids=[str(hash(log_text))])

def fetch_windows_logs(log_type="System", max_events=50):
    server = 'localhost'
    logs = []
    try:
        handle = win32evtlog.OpenEventLog(server, log_type)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        events = win32evtlog.ReadEventLog(handle, flags, 0)
        for i, event in enumerate(events):
            if i >= max_events:
                break
            msg = f"[{event.SourceName}] {event.TimeGenerated}: {' | '.join(event.StringInserts or [])}"
            logs.append(msg)
    except Exception as e:
        print(f"Error reading logs: {e}")
    return logs

def ingest_windows_logs():
    logs = fetch_windows_logs("System", max_events=30)
    for log in logs:
        embed_and_store_log(log)
