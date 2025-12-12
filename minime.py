#!/usr/bin/env python3
"""
MiniMe - Complete AI Agent Pipeline
Wake → Listen → Transcribe → LLM → TTS → Speak
"""

import os
import sys
import traceback

# Force unbuffered output for real-time visibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(line_buffering=True)
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(line_buffering=True)

# Import modules
from agent.llm import generate_response, reset_conversation
from agent.sleep_handler import get_sleep_message, is_sleep_command
from agent.wake_detector import WakeWordDetector
from audio.recorder import record_until_silence
from audio.transcriber import transcribe_audio
from audio.tts import speak_text
from config import validate_config

# Import WebSocket server
try:
    from backend.ws_server import start_server_thread, send_to_ui, stop_server
    WS_AVAILABLE = True
except ImportError:
    print("⚠️  WebSocket server not available. Install: pip install websockets", flush=True)
    WS_AVAILABLE = False
    send_to_ui = None


def main():
    """Main agent loop."""
    print("=" * 60, flush=True)
    print("🤖 MiniMe Agent - Starting...", flush=True)
    print("=" * 60, flush=True)
    
    # Validate configuration
    try:
        validate_config()
        print("✅ Configuration validated", flush=True)
    except ValueError as e:
        print(f"❌ Configuration error: {e}", flush=True)
        sys.exit(1)
    
    print("\nSay 'Hey MiniMe' to activate!", flush=True)
    print("Press Ctrl+C to exit\n", flush=True)
    
    # Start WebSocket server for frontend communication
    if WS_AVAILABLE:
        try:
            start_server_thread()
            print("✅ WebSocket server started on ws://localhost:8081", flush=True)
        except Exception as e:
            print(f"⚠️  Could not start WebSocket server: {e}", flush=True)
            print("⚠️  Continuing without frontend connection...\n", flush=True)
    
    detector = None
    audio_data = None
    
    try:
        # Initialize wake word detector
        print("[INIT] Initializing wake word detector...", flush=True)
        detector = WakeWordDetector()
        print("[INIT] Wake word detector ready!\n", flush=True)
        
        # Main loop
        while True:
            try:
                # Step 1: Wait for wake word
                print("👂 Listening for wake word...", flush=True)
                if send_to_ui:
                    send_to_ui({"event": "listening"})
                
                if not detector.listen_for_wake_word():
                    print("[EXIT] Wake word listener stopped.", flush=True)
                    break
                
                print("🔔 Wake word detected! Hey MiniMe!\n", flush=True)
                print("💬 Starting continuous conversation mode...\n", flush=True)
                
                if send_to_ui:
                    send_to_ui({"event": "wake"})
                
                # Reset conversation when wake word is detected (new conversation session)
                reset_conversation()
                
                # Continuous conversation loop until sleep command
                conversation_active = True
                turn_count = 0
                while conversation_active:
                    turn_count += 1
                    # Step 2: Record audio
                    if turn_count == 1:
                        print("[STEP 2] Starting audio recording...", flush=True)
                    else:
                        print(f"[TURN {turn_count}] Recording your response...", flush=True)
                    audio_data = record_until_silence()
                    print(f"[STEP 2] Recording complete\n", flush=True)
                    
                    # Step 3: Transcribe
                    print("[STEP 3] Starting transcription...", flush=True)
                    if send_to_ui:
                        send_to_ui({"event": "thinking"})
                    user_text = transcribe_audio(audio_data)
                    print(f"[STEP 3] Transcription: '{user_text}'\n", flush=True)
                    
                    # Close audio data buffer
                    if audio_data:
                        audio_data.close()
                        audio_data = None
                    
                    if not user_text:
                        print("⚠️  No speech detected. Listening again...\n", flush=True)
                        continue
                    
                    # Check for sleep command
                    if is_sleep_command(user_text):
                        print("😴 Sleep command detected!", flush=True)
                        sleep_msg = get_sleep_message()
                        print("🔊 MiniMe saying goodnight...\n", flush=True)
                        if send_to_ui:
                            send_to_ui({"event": "sleep"})
                        try:
                            speak_text(sleep_msg)
                        except Exception:
                            pass  # Continue even if TTS fails
                        reset_conversation()  # Reset conversation for next session
                        conversation_active = False
                        if send_to_ui:
                            send_to_ui({"event": "idle"})
                        print("-" * 60, flush=True)
                        print("MiniMe is sleeping. Say 'Hey MiniMe' to wake me up again!\n", flush=True)
                        break
                    
                    # Step 4: Generate MiniMe response
                    print("[STEP 4] Generating MiniMe response...", flush=True)
                    mini_response = generate_response(user_text)
                    print(f"[STEP 4] Response generated\n", flush=True)
                    
                    # Step 5: Speak response
                    print("🔊 MiniMe speaking...\n", flush=True)
                    try:
                        speak_text(mini_response)
                        print("[STEP 5] TTS playback complete!\n", flush=True)
                    except Exception as tts_error:
                        print(f"⚠️  TTS Error: {tts_error}", flush=True)
                        print("⚠️  MiniMe response generated but could not be spoken.", flush=True)
                        print("⚠️  Response was: " + mini_response[:100] + "...\n", flush=True)
                    
                    # Continue conversation - wait for next input
                    print("💬 Conversation continues... (speak now, or say 'ok bye'/'goodbye' to end)\n", flush=True)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  Interrupted by user. Shutting down...", flush=True)
                break
            except Exception as e:
                print(f"\n❌ Error in main loop: {e}", flush=True)
                print("Full traceback:", flush=True)
                traceback.print_exc()
                print("", flush=True)
                if audio_data:
                    audio_data.close()
                    audio_data = None
                # Continue listening after error
                continue
    
    finally:
        # Cleanup
        if detector:
            detector.cleanup()
        if audio_data:
            audio_data.close()
        if WS_AVAILABLE:
            try:
                stop_server()
            except Exception:
                pass
        print("\n👋 MiniMe shutting down. Goodbye!", flush=True)


if __name__ == '__main__':
    main()
