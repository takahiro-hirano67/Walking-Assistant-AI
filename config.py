import os
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()

# os.getenv()を使って環境変数の値を取得する
HF_TOKEN = os.getenv("HF_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
