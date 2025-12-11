import pyttsx3
import time

try:
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)
    
    test_text = "音声テストです。聞こえますか。"
    print(f"Playing: {test_text}")
    
    engine.say(test_text)
    engine.runAndWait()
    print("Playback finished.")

except Exception as e:
    print(f"An error occurred: {e}")

