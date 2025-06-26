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
    {race_info}について過去のレース傾向をまとめます。
    また、{dt.year}年との差異など留意すべき点があれば指摘します。
    ただし、以下のフォーマットとします。
    *🐎 {race_info} 過去レース傾向*
    • *コース*  
     本レースで使用されるコースの説明
    • *脚質*  
     有利な脚質の説明
    • *枠順*  
     有利な枠順の説明
    • *血統*  
     同レース条件で有利な血統をあげます
    • *騎手*  
     同レース条件で戦績の良い騎手をあげます
    • *馬場状態*  
     荒れる条件や有利な枠順の説明
    • *人気*  
     勝率などの説明
    • *当日の傾向*  
     当日の前レースまでの傾向
    • *その他*  
     上記以外の補足事項
    """
    trends = gp.ask_model(trends_prompt)
    # 有力馬・危険な馬・穴馬まとめ
    contenders_prompt = f"""\
    枠や血統、過去のレース傾向などをもとに{today}時点での{today} {race_info}の有力馬を過去データをもとにあげます。有力馬はオッズや騎手のみから判断しません。
    また、人気馬の中で危険な馬がいる場合は過去データをもとに理由を述べます。
    穴馬がいる場合も同様に過去データをもとに理由を述べます。
    ただし、以下のフォーマットとします。
    *🐎 有力馬*
    • *有力馬の名前*  
     有力馬として考えられる理由
    *🐎 危険な馬*
    • *危険な馬の名前*  
     危険な馬として考えられる理由
    *🐎 穴馬*
    • *穴馬の名前*  
     穴馬として考えられる理由
    • *その他*  
     上記以外の補足事項
    """
    contenders = gp.ask_model(contenders_prompt)
    # レース傾向予測
    forcasts_prompt = f"""\
    これまでの情報をもとにレース展開を予想します。
    ただし、以下のフォーマットとします。
    *🐎 脚質*
    • *逃げ*  
     逃げ馬の名前
    • *先行*  
     先行馬の名前
    • *差し*  
     差し馬の名前
    • *追い込み*  
     追い込み馬の名前
    *🐎 予想ペース*
    • *有力馬の名前*  
     有力馬として考えられる理由
    *🐎 予想される展開*
    • *スタート*  
     スタート時の各馬の動き
    • *前半*  
     前半の各馬の動き
    • *後半*  
     後半の各馬の動き
    • *ゴール*  
     ゴールまでの各馬の動き
    • *その他*  
     上記以外の補足事項
    """
    forcasts = gp.ask_model(forcasts_prompt)
    # 馬券
    recommendation_prompt = f"""\
    これまでを踏まえて、{race_info}において軸となる馬とその馬を軸にした期待値の高い馬券をあげます。
    穴馬がいる場合はしっかりと抑えてリターンが大きくなるようにします。連複馬券ではトリガミを恐れず積極的に的中を狙います。
    ただし、以下のフォーマットとします。
    *🐎 結論馬券*
    • *馬券種類1*  
     単勝や三連複などの馬券種類名と買い目、点数
    • *馬券種類2*  
     単勝や三連複などの馬券種類名と買い目、点数
    • *その他*  
     上記以外の補足事項
    """
    recommendation = gp.ask_model(recommendation_prompt)
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
    その後、各レースについての情報を取得します。
    最後に、WIN5的中に寄与する可能性が高い馬を穴馬を含めてそれぞれのレースで5頭まで抽出します。
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
