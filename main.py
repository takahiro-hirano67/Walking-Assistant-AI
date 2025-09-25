from google import genai
from google.genai import types
from src.gemini_api import gemini_main_func
from src.voice_box import voice
import config
import pyttsx3

# 機械音声
engine = pyttsx3.init()

# 利用可能な音声を一覧表示
engine.setProperty('rate', 180)  # ややゆっくり

# Gemini-API
client = genai.Client(api_key=config.GEMINI_API_KEY) # APIキー認証
gemini_main_func.set_client(client)

with open('img\道路.jpeg', 'rb') as f:
    image_bytes = f.read()

system_instruction = """
あなたは視覚障がいを持つ方の歩行補助を行うAIアシスタントです。あなたに与えられる写真は、白杖から撮影されたものです。
指示に従い、視覚に頼らず状況がわかるように説明をしてください。
また、生成された説明文はその場で読み上げられるため、2～3文程度で記述してください。
""".strip()

contents=[
    types.Part.from_bytes(
    data=image_bytes,
    mime_type='image/jpeg',
    ),
    '視覚障がいを持つ方に向けて、この写真に写っているものや状況を教えてください。'
]

output_text = gemini_main_func.generate_text_gemini(contents, thinking_budget=-1, system_instruction=system_instruction)

# 機械音声
engine.say(output_text)
engine.runAndWait()

# Voice Vox(処理に時間がかかる)
# file_path = voice.synthesize_voice(output_text, speaker=14, filename="output.wav")
# voice.play_wav(file_path)