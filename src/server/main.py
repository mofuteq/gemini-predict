import os
import certifi
import datetime
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from lib.gemini_predict import GeminiPredict
from lib.model import Race

# omajinai
os.environ["SSL_CERT_FILE"] = certifi.where()
# .env読み込み
load_dotenv("../../.env")
# API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")

app = FastAPI()

@app.get('/', status_code=302)
async def root():
    return RedirectResponse('/docs')

@app.post("/predict", status_code=201)
async def predict(race: Race):
    dt = datetime.datetime.today() 
    today = f"{dt.year}年{dt.month}月{dt.day}日"
    race_info = f"{race.place}競馬場第{race.number}Rの{race.name}"
    gp = GeminiPredict(api_key=GOOGLE_API_KEY,
                token=SLACK_API_TOKEN,
                channel=SLACK_CHANNEL_ID)
    trends = gp.ask_model(f"{race_info}について過去のレース傾向をまとめます。\nまた、{dt.year}との差異など留意すべき点があれば指摘します。\nただし、それぞれを項目ごとにSlackのmrkdwnフォーマットでまとめます。")
    contenders = gp.ask_model(f"枠や血統、騎手など{today}時点で得られる情報をもとに{race_info}の有力馬をリスト形式であげます。\nまた、人気馬の中で危険な馬がいる場合はその名前と根拠となるデータをもとに理由を述べます。\n不確定要素がある場合でも現時点で得られる情報から判断します。\nただし、Slackのmrkdwnフォーマットでまとめます。")
    recommendation = gp.ask_model(f"{race_info}において、軸となる馬とその馬を軸にした期待値の高い馬券をあげます。\nただし、Slackのmrkdwnフォーマットでまとめます。")
    return {
        "trends": trends,
        "contenders": contenders,
        "recommendation": recommendation
    }
