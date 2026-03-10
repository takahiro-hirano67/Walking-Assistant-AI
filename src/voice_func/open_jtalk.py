import subprocess

# --- Open JTalkの設定関数 ---
def jtalk(text):
    # 一時的な音声ファイルの保存先
    outfile = "voice/temp_voice.wav"
    
    # Open JTalkのコマンドオプション
    # 辞書のパス (aptでインストールした場合の標準パス)
    dic_path = "/var/lib/mecab/dic/open-jtalk/naist-jdic"
    # 音声データのパス (標準の男性ロボットボイス)
    # voice_path = "/usr/share/hts-voice/nitech-jp-atr503-m001/nitech_jp_atr503_m001.htsvoice"
    voice_path = "/usr/share/hts-voice/mei/mei_normal.htsvoice"
    
    # コマンドの組み立て
    # -x: 辞書, -m: 音声データ, -ow: 出力ファイル, -r: 読み上げ速度(1.0が標準)
    cmd = [
        'open_jtalk',
        '-x', dic_path,
        '-m', voice_path,
        '-ow', outfile,
        '-r', '1.2'  # 速度調整: 0.8ならゆっくり、1.2なら速く
    ]
    
    # プロセスを実行してテキストを渡す
    c = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    c.stdin.write(text.encode('utf-8'))
    c.stdin.close()
    c.wait()
    
    # 音声を再生する (aplayを使用)
    subprocess.run(['aplay', '-q', outfile])
    
    # 使い終わったファイルを削除（お好みで）
    # os.remove(outfile)