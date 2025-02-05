import openai
import pvporcupine
import pyaudio
import struct
import speech_recognition as sr
import os
import dotenv
import faiss
import numpy as np
import json  # For storing text history
import re  # Math expression detection

dotenv.load_dotenv()

# File Paths for Persistent Storage
FAISS_INDEX_FILE = "faiss_index.bin"
CHAT_MEMORY_FILE = "chat_memory.json"

# API Keys
MODEL_ID = "gpt-4o-mini"
openai.api_key = os.getenv("OPENAI_API_KEY")
ACCESS_KEY = os.getenv("ACCESS_KEY")
PPN_FILE = os.getenv("PPN_FILE")

# Initialize OpenAI client
client = openai.OpenAI()
pa = pyaudio.PyAudio()
recognizer = sr.Recognizer()

# FAISS Vector Dimensions
VECTOR_DIMENSION = 1536  # OpenAI embedding size
conversation_memory = []  # Stores text data


def record_voice():
    """Record user voice and handle longer speech without cutoff."""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎤 Listening... Speak now.")

        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=15)  # Increased timeout
            print("✅ Captured audio. Processing...")
            return recognizer.recognize_google(audio)  # Convert speech to text

        except sr.WaitTimeoutError:
            print("⚠️ No speech detected.")
            return None
        except sr.UnknownValueError:
            print("⚠️ Could not understand audio.")
            return None


def get_embedding(text):
    """Convert text to an embedding vector using OpenAI's text-embedding model."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text]
    )
    return np.array(response.data[0].embedding, dtype=np.float32)


def save_faiss_index():
    """Save FAISS index & chat memory to disk."""
    faiss.write_index(index, FAISS_INDEX_FILE)
    with open(CHAT_MEMORY_FILE, "w") as f:
        json.dump(conversation_memory, f)


def load_faiss_index():
    """Load FAISS index & chat memory from disk."""
    global index, conversation_memory
    if os.path.exists(FAISS_INDEX_FILE):
        index = faiss.read_index(FAISS_INDEX_FILE)
        print("✅ FAISS index loaded from disk.")
    else:
        index = faiss.IndexFlatL2(VECTOR_DIMENSION)
        print("⚠️ No FAISS index found, starting fresh.")

    if os.path.exists(CHAT_MEMORY_FILE):
        with open(CHAT_MEMORY_FILE, "r") as f:
            conversation_memory = json.load(f)
        print("✅ Chat history loaded from disk.")
    else:
        conversation_memory = []
        print("⚠️ No chat history found, starting fresh.")


def retrieve_relevant_memory(user_input, top_k=5):
    """Find relevant past messages based on vector similarity."""
    if len(conversation_memory) == 0:
        return []

    user_vector = get_embedding(user_input).reshape(1, -1)
    _, indices = index.search(user_vector, top_k)

    retrieved_messages = [conversation_memory[i] for i in indices[0] if i < len(conversation_memory)]
    return retrieved_messages


def store_message(text, role):
    """Store user/assistant messages in FAISS and the conversation list."""
    vector = get_embedding(text)
    index.add(vector.reshape(1, -1))  # Store vector in FAISS
    conversation_memory.append({"role": role, "content": text})
    save_faiss_index()  # Persist data after each message


def speak_text(text):
    """Speak the text using macOS 'say' command."""
    os.system(f'say "{text}"')


def initialize_porcupine():
    """Reinitialize Porcupine wake-word detection."""
    return pvporcupine.create(
        access_key=ACCESS_KEY,
        keyword_paths=[PPN_FILE]
    )


def open_audio_stream(porcupine):
    """Open a fresh audio stream after each loop."""
    return pa.open(
        rate=porcupine.sample_rate,
        channels=1,
        format=pyaudio.paInt16,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )


def is_math_expression(text):
    """Detect if a text input is a math expression using regex."""
    return bool(re.search(r'[\d\+\-\*/\^%]', text))


def evaluate_math_expression(expression):
    """Safely evaluate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": None}, {})  # Safe eval
        return f"The result is {result}"
    except Exception as e:
        return f"Error in calculation: {e}"


# Load FAISS & Chat Memory on Startup
load_faiss_index()

print("🎤 Listening for 'Hey ChatGPT'...")

# 🔄 Continuous Loop to Keep Listening
while True:
    print("\n✅ Waiting for Wake Word... (Say 'Hey ChatGPT')")

    porcupine = initialize_porcupine()
    audio_stream = open_audio_stream(porcupine)

    # Listen for Wake Word
    while True:
        pcm = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        if porcupine.process(pcm) >= 0:
            print("🔊 Wake word detected! Listening for a question...")
            break  # Exit wake-word loop and start recording voice

    porcupine = initialize_porcupine()  # Reinitialize Porcupine
    audio_stream = open_audio_stream(porcupine)  # Open a fresh stream

    # Record Voice
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    # Convert Speech to Text
    try:
        user_input = record_voice()
        print(f"🗣️ You said: {user_input}")

        # Check if the input is a mathematical expression
        if is_math_expression(user_input):
            math_result = evaluate_math_expression(user_input)
            print(f"🧮 Math Result: {math_result}")
            speak_text(math_result)
            continue  # Skip ChatGPT API for math

        # Retrieve relevant memory for context
        past_conversations = retrieve_relevant_memory(user_input)

        # Construct chat history
        messages = [{"role": "system", "content": "You are a helpful voice assistant. Keep responses concise."}]
        messages.extend(past_conversations)  # Add relevant past interactions
        messages.append({"role": "user", "content": user_input})  # Add new user input

        # Send conversation history to ChatGPT
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=messages
        )

        chatgpt_response = response.choices[0].message.content
        print(f"🤖 ChatGPT: {chatgpt_response}")

        # Store conversation in FAISS
        store_message(user_input, "user")
        store_message(chatgpt_response, "assistant")

        # Speak Response
        speak_text(chatgpt_response)

    except sr.UnknownValueError:
        print("⚠️ Sorry, I couldn't understand.")
