# %%
import os
import certifi
from google.genai.types import GoogleSearch,  Tool, Content
from dotenv import load_dotenv
from lib.model import ask_model
from lib.slack import send_slack_message

# omajinai
os.environ["SSL_CERT_FILE"] = certifi.where()

# .env読み込み
load_dotenv("../.env")
# API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
# Google検索
search_tool = Tool(google_search = GoogleSearch())


# 会話履歴
history: list[Content] = []

# レースに関する情報
race_name: str = "府中牝馬ステークス"
race_year: int = 2025


if __name__ == "__main__":
    res = ask_model(api_key=GOOGLE_API_KEY,
                    user_prompt=f"{race_name}について過去のレース傾向をまとめます。また、{race_year}との差異など留意すべき点があれば指摘します。ただし、それぞれを項目ごとに箇条書きでまとめます。",
                    history=history,
                    tools=[search_tool])
    print(res)
    send_slack_message(text=res,
                       token=SLACK_API_TOKEN,
                       channel=SLACK_CHANNEL_ID)
    res = ask_model(api_key=GOOGLE_API_KEY,
                    user_prompt=f"枠順やオッズを踏まえて現時点での{race_year}年の{race_name}の有力馬をリスト形式であげます。",
                    history=history,
                    tools=[search_tool])
    print(res)
    send_slack_message(text=res,
                       token=SLACK_API_TOKEN,
                       channel=SLACK_CHANNEL_ID)
