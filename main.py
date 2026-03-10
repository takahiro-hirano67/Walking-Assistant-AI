import keyboard # キー入力用（ボタン入力）
import time
import re
import threading # バックグラウンド処理用
import subprocess
import pygame # 再生用(SE/音声)
import config
from datetime import datetime
from picamera2 import Picamera2 # カメラ
from google import genai # Gemini API
from google.genai import types
from src.gemini_api import gemini_main_func # テキスト生成関数
# from src.battery_func import battery_check  # バッテリー状況確認

# ==========================================
# 定数・設定（キー設定 / フラグ / 音声ミキサー / Open-JTalk）
# ==========================================

# キー設定
KEY_SIMPLE_MODE = '5'  # キーボードの「1」キー（簡易モード）
KEY_DETAIL_MODE = '4'  # キーボードの「2」キー（詳細モード）
KEY_BATTERY_CHK = '3'  # キーボードの「3」キー（バッテリー残量確認）

# 連打防止用のフラグ
is_processing = False

# 音声再生を中断するためのフラグ
stop_speech_flag = False

# pygameのミキサー初期化（音質設定）
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

## Open JTalkで使用するパス ##
# 辞書のパス (aptでインストールした場合の標準パス)
dic_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
# 音声データのパス 
# voice_path = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice" # 標準の男性ロボットボイス
voice_path = "/usr/share/hts-voice/mei/mei_normal.htsvoice" # 女性ボイス（メイ）

# ==========================================
# プロンプト（システムプロンプト / 簡易モードプロンプト / 詳細モードプロンプト）
# ==========================================

system_prompt = """
あなたは視覚障がいを持つ方の歩行補助を行うAIアシスタントです。あなたに与えられる写真は、白杖から撮影されたものです。
指示に従い、視覚に頼らず状況がわかるように説明をしてください。
""".strip()

simple_mode_prompt = """
視覚障がいを持つ方に向けて、この写真に写っているものや状況を教えてください。
生成された説明文はその場で読み上げられるため、2～3文程度で記述してください。
""".strip()

# 仮
detail_mode_prompt = """
視覚障がいを持つ方に向けて、この写真に写っているものや状況を教えてください。
生成された説明文はその場で読み上げられます。自然に音声が聞き取れるよう、箇条書きや見出し、その他不要な記号は含めないでください。
""".strip()

# ==========================================
# 補助関数（現在時刻 / 音声停止 / スレッド管理）
# ==========================================

def get_now():
    "現在時刻を文字列にして返す関数（ファイル名用）"
    td = datetime.now()
    formatted_now = td.strftime('%Y-%m-%d-%H-%M-%S')
    return formatted_now

def stop_speaking():
    """音声再生を強制停止するための関数"""
    global stop_speech_flag
    stop_speech_flag = True
    
    # 読み上げを停止
    pygame.mixer.stop()

def start_thread(target_func, *args):
    """
    指定した関数を別スレッドで実行するヘルパー関数
    これにより、キーボード入力がブロックされずに次の入力を受け付けられる
    """
    # 既に別スレッドが走っているかどうかのチェックは target_func 内で行う
    thread = threading.Thread(target=target_func, args=args)
    thread.daemon = True # メインプログラム終了時に道連れで終了させる
    thread.start()

# ==========================================
# 主要関数（効果音 / 音声 / 撮影）
# ==========================================

def play_se(file_path):
    "効果音を再生する関数 (pygame使用)"
    try:
        # 効果音の読み込みと再生

        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop() # 前の音が鳴っていたら止める
        pygame.mixer.music.load(file_path)
        # 音量調整
        pygame.mixer.music.set_volume(0.5)
        # 再生
        pygame.mixer.music.play()
        
    except Exception as e:
        print(f"SE再生エラー: {e}")


def speak(text, file_name="system_voice"):
    """音声を再生する関数"""
    global stop_speech_flag
    stop_speech_flag = False # フラグをリセット
    
    outfile = f"assets/audio/voice/{file_name}.wav"

    # 1. テキストの前処理（改行を「。」に置換し、余計な空白を削除）
    text = text.replace('\n', '。')

    # 2. 「。」で文章を分割してリストにする
    sentences = re.split(r'(?<=。)', text)
    sentences = [s for s in sentences if s.strip()]

    for sentence in sentences:
        # ループの先頭でチェック（ここは既存の通り）
        if stop_speech_flag:
            print("再生を中断しました")
            break

        # 短すぎるテキストはスキップ
        if len(sentence) < 2:
            continue

        # WAV生成
        cmd = [
            'open_jtalk',
            '-x', dic_path,
            '-m', voice_path,
            '-ow', outfile,
            '-g', '10', # 音量
        ]
        
        try:
            # Open JTalkを実行
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(input=sentence.encode('utf-8'))

            # 読み込み
            voice_sound = pygame.mixer.Sound(outfile)
            # 再生開始（既に別の音が鳴っていたら混ざって再生される）
            channel = voice_sound.play()
            
            # channelが存在し、かつ再生中であれば待機
            while channel and channel.get_busy():
                if stop_speech_flag: # 停止フラグが立ったら即座に抜ける
                    channel.stop()
                    break
                time.sleep(0.05)
                
        except Exception as e:
            print(f"音声再生エラー: {e}")
    

def take_picture(file_name="temp_img"):
    """撮影を実行する関数"""

    try:
        # 写真を撮って保存
        picam2.capture_file(f"assets/images/{file_name}.jpg")

        print(f"撮影完了: {file_name}.jpg")

        with open(f'assets/images/{file_name}.jpg', 'rb') as f:
            image_bytes = f.read()
    except Exception as e:
        print(f"撮影エラー: {e}")
        return None
    
    return image_bytes

# ==========================================
# 各機能のハンドラ（簡易モード / 詳細モード / バッテリー残量確認）
# ==========================================

def run_ai_support(mode):
    """指定されたモードで撮影&AI解説を行う"""
    global is_processing

    # 処理中なら「停止命令」を出してリターン（＝連打でストップ機能）
    if is_processing:
        stop_speaking()
        play_se("assets/audio/sfx/chattering.wav")
        print("処理を中断しました")
        return

    # 処理開始
    is_processing = True # 処理開始フラグ
    stop_speaking() # 念のため前の音声を消す

    try:
        # 1. 現在の日時取得（ファイル名用）
        file_name = get_now() # 

        # 2. 撮影
        image_bytes = take_picture(file_name)
        if image_bytes is None:
            raise Exception("撮影に失敗")

        # 3. 画像指定
        contents = [
            types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg',
            ),
        ]

        # 4. モード分岐-テキスト生成
        if mode == "simple":
            print(f"【簡易モード】")
            play_se("assets/audio/sfx/start_simple.wav")

            contents.append(simple_mode_prompt) # プロンプト指定
            
            # テキスト生成
            output_text = gemini_main_func.generate_text(
                contents,
                thinking_budget=0,  # 思考プロセスなし
                temperature=0.7,    # 確実性重視
                system_instruction=system_prompt,
            )

        elif mode == "detail":
            print(f"【詳細モード】")
            contents.append(detail_mode_prompt) # プロンプト指定
            play_se("assets/audio/sfx/start_detail.wav")

            speak("生成しています。") # 詳細生成は思考プロセスが入る分、レスポンスが遅くなるため。待機が発生するが短いため許容範囲
            
            # テキスト生成
            output_text = gemini_main_func.generate_text(
                contents,
                thinking_budget=-1, # 動的思考
                temperature=1.0,    # 創造性重視
                system_instruction=system_prompt,
            )

        else:
            raise ValueError(f"不明なモード: {mode}")
        
        # 5. 生成テキスト読み上げ
        speak(output_text, "main_voice")

    except Exception as e:
        play_se("assets/audio/sfx/error.wav")
        print(f"エラー: {e}")
        speak("エラーが発生しました")
    finally:
        is_processing = False # 処理終了フラグ

# 認識しない場合があるため、プロトタイプではバッテリー認識機能はオフに
# def check_battery_voice():
#     """バッテリー残量を読み上げる"""
#     global is_processing
#     if is_processing: return # 処理中の場合は中断
#     is_processing = True

#     try:
#         play_se("assets/audio/sfx/check_battery.wav")
#         cap = battery_check.read_capacity()
#         text = f"バッテリー残量は、およそ{int(cap)}パーセントです。"
#         print(text)
#         speak(text) # 音声読み上げ
#     except Exception as e:
#         play_se("assets/audio/sfx/error.wav")
#         print(f"エラー: {e}")
#     finally:
#         is_processing = False # 処理終了フラグ


# ==========================================
# バックグラウンド処理（バッテリー残量定期監視）
# ==========================================

# def monitor_battery_background():
#     """バックグラウンドで電池残量を監視し、減りすぎたら警告する"""
#     while True:
#         try:
#             cap = battery_check.read_capacity()
#             if cap < 15.0:
#                 print("【警告】バッテリーが低下しています")
#                 speak("バッテリーが残りわずかです。充電してください。")
#                 time.sleep(300) # 警告後は5分黙る
#         except:
#             pass
#         time.sleep(60) # 1分ごとにチェック

# ==========================================
# メイン処理
# ==========================================

if __name__ == "__main__":
    # ====== Gemini-API ======
    print("API認証中...")
    client = genai.Client(api_key=config.GEMINI_API_KEY) # APIキー認証
    gemini_main_func.set_client(client) # モジュールにAPIキーを反映

    # ====== Camera ======
    print("カメラを初期化中...")
    picam2 = Picamera2()

    # 解像度の設定（AI用のため、軽くする設定）
    cam_config = picam2.create_still_configuration(main={"size": (1024, 768), "format": "RGB888"})
    picam2.configure(cam_config)

    # カメラ起動
    picam2.start()

    # 最初の1回だけ、画質が安定するのを待つ
    print("画質調整のため待機中...")
    time.sleep(2)

    # システム準備完了通知
    print("【システム準備完了。ボタン待機中】")
    speak("システムを起動しました。")
    play_se("assets/audio/sfx/setup.wav")

    # キー割り当ての設定
    # キーを押した瞬間に別スレッドが立ち上がり、キー監視スレッドは即座に解放される
    keyboard.add_hotkey(KEY_SIMPLE_MODE, lambda: start_thread(run_ai_support, "simple"))
    keyboard.add_hotkey(KEY_DETAIL_MODE, lambda: start_thread(run_ai_support, "detail"))
    # keyboard.add_hotkey(KEY_BATTERY_CHK, lambda: start_thread(check_battery_voice))

    # バッテリー監視スレッドの開始（メイン処理を止めないように別枠で動かす）
    # t = threading.Thread(target=monitor_battery_background, daemon=True)
    # t.start()

    try:
        # プログラムが終了しないように待機
        keyboard.wait() # Ctrl + C が押されると KeyboardInterrupt エラーが発生して except に飛ぶ

    except KeyboardInterrupt:
        # Ctrl + C で中断された時の処理
        print("\n【システム終了操作を検知しました】")
        stop_speaking() # 喋ってたら止める
        speak("システムを終了します。") 
        play_se("assets/audio/sfx/finish.wav")
        # 音声が読み上げ終わるのを少し待つ（即終了すると声が切れるため）
        time.sleep(2)

    finally:
        # 正常終了でもエラー終了でも、必ず最後に実行される処理
        print("カメラを停止しています...")
        picam2.stop()
        
        # キーボードのフックを解除（明示的に）
        keyboard.unhook_all()
        print("【システム終了完了】")

# 起動時はシステム権限が必要
# sudo -E ./myvenv/bin/python main.py

# スピーカー認識
# sudo -E env PULSE_SERVER=unix:/run/user/$(id -u)/pulse/native ./myvenv/bin/python main.py

# 外部2キーキーボードボタン対応操作:
# 簡易モード5-->上
# 詳細モード4-->下