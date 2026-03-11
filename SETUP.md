# セットアップ方法 （メモ）

## セットアップ

### 必要環境

- Raspberry Pi 5 (推奨: 16GB RAM)
- Raspberry Pi Camera Module 3
- Raspberry Pi OS (Debian Bookworm以降)
- Python 3.11以上

### 依存パッケージのインストール

```bash
# システムパッケージ
sudo apt update
sudo apt install -y \
    open-jtalk \
    open-jtalk-mecab-naist-jdic \
    hts-voice-nitech-jp-atr503-m001 \
    libsdl2-mixer-2.0-0 \
    libsdl2-2.0-0

# 女性ボイス（メイ）のインストール（オプション）
sudo apt install -y hts-voice-mei-jp

# Python仮想環境の作成
python3 -m venv myvenv
source myvenv/bin/activate

# Pythonパッケージ
pip install -r requirements.txt
```

### 環境変数の設定

```bash
# .envファイルを作成
cp .env.example .env

# Gemini APIキーを設定
nano .env
```

`.env`ファイルに以下を記述：

```
GEMINI_API_KEY=your_api_key_here
```

---

## 📖 使い方

### 起動

```bash
# システム権限が必要（キーボード入力のため）
sudo -E ./myvenv/bin/python main.py
```

### 操作方法

| ボタン               | 機能                             |
| -------------------- | -------------------------------- |
| **ボタン1（上）**    | 簡易モード（2〜3文の簡潔な説明） |
| **ボタン2（下）**    | 詳細モード（詳細な状況説明）     |
| **処理中に再度押す** | 音声中断                         |
| **Ctrl + C**         | システム終了                     |

### 音声フィードバック

各操作時に効果音と音声で状態を通知：

- 起動完了: 「システムを起動しました」
- 簡易モード開始: 特定の効果音
- 詳細モード開始: 「生成しています」という音声 + 効果音
- エラー発生: エラー音 + 「エラーが発生しました」
- 終了: 「システムを終了します」
