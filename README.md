# **ChatGPT Voice Assistant with Persistent Memory & Math Execution**
🚀 **A smart AI voice assistant** that listens for a wake word ("Hey GPT"), responds using OpenAI's GPT-4o-mini, remembers past conversations using FAISS, and executes math calculations locally.  

## ✨ **Features**
✅ **Wake Word Activation** - Uses `Porcupine` for always-on listening  
✅ **Contextual Memory** - Remembers past conversations with **FAISS**  
✅ **Persistent Chat History** - Stores FAISS & chat data to disk for recall after restarts  
✅ **Math Execution** - Evaluates mathematical expressions locally  
✅ **Extended Speech Handling** - Allows longer questions without cut-off  
✅ **Optional Whisper Integration** - More accurate transcription than Google Speech API  

---

## 📥 **Installation**
### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/yourusername/chatgpt-voice-assistant.git
cd chatgpt-voice-assistant
```
### 2️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```
### 3️⃣ **Set Up API Keys**
Create a `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
ACCESS_KEY=your_porcupine_access_key
PPN_FILE=Hey-Gee-Pee-Tee_en_mac_v3_0_0.ppn
```

---

## 🚀 **Usage**
### **Run the assistant**
```bash
python chatgpt_assistant.py
```
1. Say **"Hey ChatGPT"** to activate.
2. Ask a question **(Supports follow-ups with memory!)**  
3. Listen to ChatGPT’s response.  
4. **Ask a math question** (e.g., "What is 12 * 9?") for instant calculation.  
5. Restart anytime — **chat history is saved!**  

---

## 🛠 **Configuration**
| Feature | Description |
|---------|-------------|
| **Wake Word** | Uses Porcupine (`hey_chatgpt.ppn`) |
| **Chat Memory** | Stored using FAISS (`faiss_index.bin`) |
| **Long Questions** | Supports **15-sec voice input** |
| **Math Handling** | Uses Python `eval()` safely |
| **Whisper API (Optional)** | Replace Google STT with Whisper |

---

## 🔥 **Upcoming Features**
- **Home Automation** (Control IoT devices)  
- **GUI Interface** (For non-voice input)  
- **Multi-User Profiles** (Separate memory for each user)  

---

## 🤝 **Contributing**
Feel free to fork, submit PRs, and improve the assistant!  

---

### 🎉 **Now, Say "Hey ChatGPT" & Enjoy Your Personal AI Assistant!** 🚀
