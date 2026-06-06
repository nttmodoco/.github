import json

# 保存したいデータ（辞書型）
data = {
    "status": "テスト成功"
}

# jsonファイルとして保存
with open("test_result.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("GitTest.pyの実行が完了し、ファイルを保存しました！")