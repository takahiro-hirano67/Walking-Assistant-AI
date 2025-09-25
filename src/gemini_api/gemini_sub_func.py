# ストリーミング生成関数（チャンクごとの処理）
def stream(response_stream):
    thoughts = ""
    answer = ""
    for chunk in response_stream:

        for part in chunk.candidates[0].content.parts:
          if not part.text:
            continue
          elif part.thought:
            if not thoughts:
              print("="*10, "思考の要約", "="*10)
            print(part.text.strip(), "\n")
            thoughts += part.text
          else:
            if not answer:
              print("="*12, "回答", "="*12)
            print(part.text, end="")
            answer += part.text

        if chunk.usage_metadata: # メタデータの取得
            final_usage_metadata = chunk.usage_metadata

    return answer, final_usage_metadata

# 利用トークン数の表示
def print_usage_metadata(usage_metadata):
    print("\n" + "="*30)
    print(f"prompt_tokens : {usage_metadata.prompt_token_count}")
    print(f"thought_tokens: {usage_metadata.thoughts_token_count}")
    print(f"answer_tokens : {usage_metadata.candidates_token_count}")
    print(f"total_tokens  : {usage_metadata.total_token_count}")