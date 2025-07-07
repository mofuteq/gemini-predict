import os
import certifi
import datetime
import pandas as pd
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
SLACK_OTHER_ID = os.getenv("SLACK_OTHER_ID")
SLACK_WIN5_ID = os.getenv("SLACK_WIN5_ID")
SLACK_TOKYO_ID = os.getenv("SLACK_TOKYO_ID")
SLACK_HANSHIN_ID = os.getenv("SLACK_HANSHIN_ID")
SLACK_HAKODATE_ID = os.getenv("SLACK_HAKODATE_ID")
SLACK_FUKUSHIMA_ID = os.getenv("SLACK_FUKUSHIMA_ID")
SLACK_KOKURA_ID = os.getenv("SLACK_KOKURA_ID")
slack_dict = {
    "東京": SLACK_TOKYO_ID,
    "阪神": SLACK_HANSHIN_ID,
    "函館": SLACK_HAKODATE_ID,
    "福島": SLACK_FUKUSHIMA_ID,
    "小倉": SLACK_KOKURA_ID,
    "other": SLACK_OTHER_ID,
    "win5": SLACK_WIN5_ID
}

app = FastAPI()


@app.get('/', status_code=302)
async def root():
    return RedirectResponse('/docs')


@app.get("/prediction")
async def predict(place: str,
                  number: int,
                  name: str
                  ):
    dt = datetime.datetime.today()
    today = f"{dt.year}年{dt.month}月{dt.day}日(JST)"
    race_info = f"{place}競馬場{number}R {name}"
    channel = slack_dict[f"{place}"] if place in slack_dict.keys(
    ) else slack_dict["other"]
    gp = GeminiPredict(api_key=GOOGLE_API_KEY,
                       token=SLACK_API_TOKEN,
                       channel=channel)
    # レース傾向まとめ
    trends_prompt = f"""\
    {race_info}について購入する馬券を決めるために出走する馬やトラックバイアスの研究をします。
    まずは、{today}から最も開催日時が近い{race_info}について情報を取得し、トラックバイアスや当日の天気、統計的に有利な枠や過去のレース傾向をまとめてください。
    """
    trends = gp.ask_model(trends_prompt,
                          simplify=True)
    # 有力馬・危険な馬・穴馬まとめ
    contenders_prompt = f"""\
    {race_info}について、馬券戦略を考える前にすべての出走馬について分析を行います。
    過去の出走成績からメンバーレベルを加味して印をつけてください。
    ただし、少しでも可能性がある馬は残してください。
    """
    contenders = gp.ask_model(contenders_prompt,
                              simplify=True)
    # レース傾向予測
    forcasts_prompt = f"""\
    {race_info}の出走馬について、個別データ（過去5走ラップ、位置取り指数、調教タイムなど）を深掘りします。
    個別データを加味して印を再検討してください。
    """
    forcasts = gp.ask_model(forcasts_prompt,
                            simplify=True)
    # レース傾向予測
    forcasts_prompt = f"""\
    {race_info}について、ラップモデリングによる展開予測をします。
    同時に展開がスローになるかハイになるか、理由とともに考えてください。
    """
    forcasts = gp.ask_model(forcasts_prompt,
                            model="gemini-2.5-flash",
                            simplify=True)
    # 馬券
    recommendation_prompt = f"""\
    {race_info}について、展開別シナリオでの券種戦略へ進めてください。
    安全寄りと穴狙い寄り両方を考えます。回答には軸馬と紐を含めます。
    """
    recommendation = gp.ask_model(recommendation_prompt,
                                  model="gemini-2.5-flash",
                                  simplify=True)
    # for debug
    df = pd.DataFrame(data={
        "date": today,
        "race": race_info,
        "trends_prompt": trends_prompt,
        "trends": trends,
        "contenders_prompt": contenders_prompt,
        "contenders": contenders,
        "forcasts_prompt": forcasts_prompt,
        "forcasts": forcasts,
        "recommendation_prompt": recommendation_prompt,
        "recommendation": recommendation,
        "model": gp.model,
        "temperature": gp.temperature,
        "top_k": gp.top_k,
        "top_p": gp.top_p,
        "tool": f"{gp.tool_list}",
        "thinking_config": f"{gp.thinking_config}"
    },
        index=[0]
    )
    try:
        df.to_csv("./log/data.csv", mode="x", index=False)
    except FileExistsError:
        df.to_csv("./log/data.csv", mode="a", header=None, index=False)
    # for storing history
    if os.path.exists("./log/history.pkl"):
        past_history_df = pd.read_pickle("./log/history.pkl",
                                         compression="tar")
    else:
        past_history_df = pd.DataFrame()
    history_df = pd.DataFrame(data={
        "date": today,
        "race": race_info,
        "history": [gp.history_list]
    },
        index=[0]
    )
    history_df = pd.concat([past_history_df, history_df])
    history_df.to_pickle("./log/history.pkl",
                         compression="tar")
    return {
        "trends": trends,
        "contenders": contenders,
        "forcasts": forcasts,
        "recommendation": recommendation
    }


@app.get("/win5")
async def win5():
    today = datetime.datetime.today().date()
    date_delta = 6 - today.weekday()
    next_sunday = today + datetime.timedelta(days=date_delta)
    channel = slack_dict["win5"]
    gp = GeminiPredict(api_key=GOOGLE_API_KEY,
                       token=SLACK_API_TOKEN,
                       channel=channel)
    # 馬券
    recommendation = gp.ask_model(f"""\
    まず、{next_sunday}に開催されるWIN5の対象となる5つのレースに関する情報を取得します。
    各レースの情報を取得し、WIN5的中に寄与する可能性が高い馬を穴馬を含めてそれぞれのレースで最低1頭、最大2頭まで抽出します。
    ただし、以下のフォーマットとします。
    *🐎 結論馬券*
    • *レース1*  
     (馬番) 馬名
    • *レース2*  
     (馬番) 馬名
    • *その他*  
     上記以外の補足事項
    """)
    return {
        "recommendation": recommendation
    }
