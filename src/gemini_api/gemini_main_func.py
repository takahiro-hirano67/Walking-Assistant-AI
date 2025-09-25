from google.genai import types
from . import gemini_sub_func

client = None

# 認証情報をセット（このモジュール内でAPI認証を実行しなくていいようにするため。）
def set_client(c):
    global client
    client = c

# テキスト生成関数（引数でオプションを指定）
def generate_text_gemini(
        contents,                # プロンプト
        system_instruction=None, # システム指示 (None=なし, 文字列=システム指示を設定)
        thinking_budget=-1,      # 思考プロセスで使用するトークンの上限 (公式初期値: -1, 範囲: 0～24576, 0=なし, -1=動的思考 ※思考で利用したトークンもAPI利用コストに上乗せ)
        include_thoughts=True,   # 思考の要約を表示 (デバッグ用)
        temperature=0.7,         # 生成のランダム性 (公式初期値: 1.0, 範囲: 0.0～2.0)
        topP=0.95,               # モデルが考慮するトークン。上位から順に確率の合計が設定した値になるまで選択（公式初期値: 0.95, 範囲: 0.0～1.0）
        topK=64,                 # 次のトークンを選択するために、上位64個のトークンを考慮（公式初期値: 64, 範囲: 固定）
        frequencyPenalty=0.0,    # 頻度ペナルティ: 正の値→ 重複したトークンの生成を抑制する（公式初期値: 0.0, 範囲: -2.0～2.0 ※負の値は繰り返しを助長）
        presencePenalty=0.0,     # 存在ペナルティ: 正の値→ 新しいトークンの生成を促す（公式初期値: 0.0, 範囲: -2.0～2.0 ※負の値は繰り返しを助長）
        maxOutputTokens=65535,   # 最大出力トークン (公式初期値: 65535, 上限: 65535)
        candidateCount=1,        # 生成の候補 (公式初期値: 1 ※増やすと消費トークン数が増加)
        stopSequences=None,      # 停止シーケンス (None=なし, リスト=指定された文字列で生成停止)
        responseMimeType="text/plain",  # レスポンス形式 ("text/plain" or "application/json")
        ):


    global client
    if client is None:
        raise ValueError("clientがセットされていません。set_client()でセットしてください。")

    # 1. 設定オブジェクトを作成
    generation_config = types.GenerateContentConfig(
        # 思考プロセスの設定
        thinking_config=types.ThinkingConfig(
            thinking_budget=thinking_budget,
            include_thoughts=include_thoughts
            ),
        # システムプロンプトとツール
        system_instruction=system_instruction,
        # サンプリングパラメータ等
        temperature=temperature,
        topP=topP,
        topK=topK,
        frequencyPenalty=frequencyPenalty,
        presencePenalty=presencePenalty,
        maxOutputTokens=maxOutputTokens,
        candidateCount=candidateCount,
        stop_sequences=stopSequences,
        responseMimeType=responseMimeType,
    )

    # 2. ストリーミングリクエストを送信
    response_stream = client.models.generate_content_stream(
        model="gemini-2.5-flash",
        contents=contents,
        config=generation_config
    )
    output_text, usage_metadata = gemini_sub_func.stream(response_stream)

    if usage_metadata:
        gemini_sub_func.print_usage_metadata(usage_metadata) # トークン利用状況表示
    
    return output_text
