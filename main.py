from google import genai
from google.genai import types
from src.gemini_api import gemini_main_func
from picamera2 import Picamera2
import pyttsx3
import time
import config

# 機械音声
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # ややゆっくり

# Gemini-API
client = genai.Client(api_key=config.GEMINI_API_KEY) # APIキー認証
gemini_main_func.set_client(client)

# camera

# カメラの初期化
picam2 = Picamera2()

# カメラを起動して、画質調整のために2秒待つ
picam2.start()
time.sleep(2)

# 写真を撮って保存
picam2.capture_file("img/test.jpg")

# 終了
picam2.stop()
print("撮影完了: test.jpg")

with open('img/test.jpg', 'rb') as f:
    image_bytes = f.read()

system_instruction = """
あなたは視覚障がいを持つ方の歩行補助を行うAIアシスタントです。あなたに与えられる写真は、白杖から撮影されたものです。
指示に従い、視覚に頼らず状況がわかるように説明をしてください。
""".strip()

contents=[
    types.Part.from_bytes(
    data=image_bytes,
    mime_type='image/jpeg',
    ),
    '視覚障がいを持つ方に向けて、この写真に写っているものや状況を教えてください。生成された説明文はその場で読み上げられるため、2～3文程度で記述してください。'
]
# thinking_budgetで思考量を調整（多いほど生成に時間がかかる）
output_text = gemini_main_func.generate_text_gemini(contents, thinking_budget=0, system_instruction=system_instruction)

# 機械音声
engine.say(output_text)
engine.runAndWait()