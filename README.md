# MiniMe - Complete AI Agent

MiniMe is your desktop AI agent that activates when you say "Hey MiniMe", listens to your voice, processes it through your dual-personality system prompt, and responds through a cloned voice.

## Complete Pipeline

**Wake → Listen → Transcribe → LLM → TTS → MiniMe Speaks**

1. **Wake Word Detection** - Detects "Hey MiniMe" using Picovoice Porcupine
2. **Audio Recording** - Records your voice until silence is detected
3. **Transcription** - Converts speech to text using OpenAI Whisper
4. **LLM Processing** - Generates MiniMe response using GPT with your soul prompt
5. **Text-to-Speech** - Synthesizes response using ElevenLabs in your cloned voice
6. **Audio Playback** - Plays MiniMe's response through your speakers

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** On macOS, you may need to install PortAudio first:
```bash
brew install portaudio
```

### 2. Configure API Keys

Edit `keys.env` and add your API keys:

- **PICOVOICE_KEY** - Get from https://console.picovoice.ai/
- **ELEVEN_API_KEY** - Get from https://elevenlabs.io/
- **OPENAI_API_KEY** - Get from https://platform.openai.com/api-keys
- **ELEVEN_VOICE_ID** - Your cloned voice ID (already set)

### 3. Add Wake Word Model

Place your `minime.ppn` file in the `wakeword/` directory.

### 4. Add System Prompt

Paste your MiniMe system prompt into `agent/soul_prompt.txt`.

## Running

### Complete Agent (Full Pipeline)

```bash
python minime.py
```

This will:
- Listen continuously for "Hey MiniMe"
- When detected, record your voice
- Transcribe, process through LLM, and speak the response
- Return to listening mode

### Individual Components (Testing)

**Wake Word Detection:**
```bash
python wake_listener.py
```

**Test TTS:**
```bash
python test_tts.py
```

**Test Prompt Loader:**
```bash
python test_prompt_loader.py
```

## Project Structure

```
minime/
  ├── wakeword/
  │     └── minime.ppn           # Wake word model file
  ├── agent/
  │     ├── prompt_loader.py      # Loads system prompt
  │     ├── llm.py                # LLM integration
  │     ├── wake_detector.py      # Wake word detection module
  │     └── soul_prompt.txt       # Your MiniMe system prompt
  ├── audio/
  │     ├── tts.py                # ElevenLabs TTS module
  │     ├── recorder.py           # Audio recording module
  │     └── transcriber.py         # Whisper transcription module
  ├── keys.env                    # API keys configuration
  ├── minime.py                   # Main agent loop
  ├── wake_listener.py            # Standalone wake word test
  ├── requirements.txt            # Python dependencies
  └── README.md                   # This file
```

## Usage

1. Run `python minime.py`
2. Say **"Hey MiniMe"** to activate
3. Speak your message (it will record until you stop talking)
4. MiniMe will process and respond in your cloned voice
5. MiniMe goes back to sleep until you call again

Press `Ctrl+C` to exit.

## Features

- ✅ Wake word detection (Picovoice Porcupine)
- ✅ Voice recording with silence detection
- ✅ Speech-to-text transcription (OpenAI Whisper)
- ✅ Dual-personality LLM (Gremlin/Angel modes)
- ✅ Text-to-speech (ElevenLabs cloned voice)
- ✅ Complete pipeline integration
- ✅ Error handling and cleanup

## Notes

- Requires microphone access permissions
- Make sure your microphone is working before running
- The system automatically detects silence to end recording
- MiniMe switches between Gremlin and Angel modes based on your tone
