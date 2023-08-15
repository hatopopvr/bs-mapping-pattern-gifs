from datetime import datetime
from dotenv import load_dotenv

# .envファイルから環境変数を読み込む
load_dotenv()

# 環境変数を取得する


def get_bsr_info(map_id, level="リンク"):
    import requests

    def fetch_beatmap_data(map_id):
        url = f"https://api.beatsaver.com/maps/id/{map_id}"
        response = requests.get(url)

        if response.status_code == 200:
            return response.json()
        else:
            return f"エラーが発生しました。ステータスコード: {response.status_code}"

    def extract_beatmap_details(beatmap_data):
        tags = ', '.join(beatmap_data.get("tags", [])) or "N/A"

        uploaded_date = beatmap_data.get("uploaded", None)
        if uploaded_date:
            uploaded_date = datetime.fromisoformat(
                uploaded_date.replace("Z", "+00:00"))
            formatted_uploaded_date = uploaded_date.strftime(
                "%Y-%m-%d %H:%M:%S")
        else:
            formatted_uploaded_date = "N/A"

        details = {
            "url": url,
            "BeatSaver曲名": beatmap_data.get("name", "N/A"),
            "曲名": beatmap_data["metadata"].get("songName", "N/A"),
            "Artist名": beatmap_data["metadata"].get("songAuthorName", "N/A"),
            "mapper名": beatmap_data["metadata"].get("levelAuthorName", "N/A"),
            "アップロードされた日付": formatted_uploaded_date,
            "タグ": tags,  # タグ情報をカンマ区切りの文字列に変換、存在しない場合は"N/A"
            "曲の長さ": beatmap_data["metadata"].get("duration", "N/A"),
            "BPM": beatmap_data["metadata"].get("bpm", "N/A"),
            "レーティング": beatmap_data["stats"].get("score", "N/A")
        }

        difficulties = []
        for version in beatmap_data.get("versions", []):
            for diff in version.get("diffs", []):
                difficulties.append({
                    "難易度名": diff.get("difficulty", "N/A"),
                    "難易度": diff.get("stars", "N/A"),
                    "Notes数": diff.get("notes", "N/A"),
                    "NJS": diff.get("njs", "N/A"),
                    "NPS": diff.get("nps", "N/A"),
                    "Bombs数": diff.get("bombs", "N/A"),
                    "Obstacles数": diff.get("obstacles", "N/A")
                })

        return details, difficulties

    second_gpt_prompt = [f"以下の形式で返してください",
                         f"# フォーマット",
                         f"[結果についてコメント]",
                         f"",
                         f"[出力結果]\n\n"]

    url = f"https://beatsaver.com/maps/{map_id}"

    beatmap_data = fetch_beatmap_data(map_id)

    result_dict = {
        'content': "",
        'second_gpt_setting': {
            'use': True,
            'model': None,
            'prompt': '\n'.join(second_gpt_prompt),
        },
        'data': {
            'urls': [],
            'images': [],
            'embed': [],
        }
    }

    if isinstance(beatmap_data, str):  # エラーが発生した場合の処理
        result_dict['content'] = beatmap_data
        return result_dict

    details, difficulties = extract_beatmap_details(beatmap_data)

    # formatted_result = extract_and_format_beatmap_details(beatmap_data)

    # 結果を返す
    return details
