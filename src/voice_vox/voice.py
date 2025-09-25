import requests
import simpleaudio as sa

# 音声合成を行う関数
def synthesize_voice(text, speaker=14, filename="output.wav"):
    # 1. テキストから音声合成のためのクエリを作成
    query_payload = {'text': text, 'speaker': speaker}
    query_response = requests.post(f'http://localhost:50021/audio_query', params=query_payload)

    if query_response.status_code != 200:
        print(f"Error in audio_query: {query_response.text}")
        return

    query = query_response.json()

    # 2. クエリを元に音声データを生成
    synthesis_payload = {'speaker': speaker}
    synthesis_response = requests.post(f'http://localhost:50021/synthesis', params=synthesis_payload, json=query)

    if synthesis_response.status_code == 200:
        # 音声ファイルとして保存
        file_path = r'wav\\' + filename
        with open(file_path, 'wb') as f:
            f.write(synthesis_response.content)
        print(f"音声が {filename} に保存されました。")
    else:
        print(f"Error in synthesis: {synthesis_response.text}")
    
    return file_path

def play_wav(file_path):
    # WAVファイルを読み込む
    wave_obj = sa.WaveObject.from_wave_file(file_path)

    # 再生を開始
    play_obj = wave_obj.play()

    # 再生が完了するまで待機
    play_obj.wait_done()

if __name__ == "__main__":
    # 読み上げたいテキスト
    text = "こんにちは、VOICEVOXでテキストを音声に変換していました。"

    # 音声合成の実行
    file_path = synthesize_voice(text, speaker=1, filename="output.wav")
    play_wav(file_path)