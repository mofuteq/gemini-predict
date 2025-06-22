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


@app.post("/predict", status_code=201)
async def predict(race: Race):
    dt = datetime.datetime.today() 
    today = f"{dt.year}年{dt.month}月{dt.day}日(JST)"
    race_info = f"{race.place}競馬場{race.number}R {race.name}"
    channel = slack_dict[f"{race.place}"] if race.place in slack_dict.keys() else slack_dict["other"]
    gp = GeminiPredict(api_key=GOOGLE_API_KEY,
                token=SLACK_API_TOKEN,
                channel=channel)
    # レース傾向まとめ
    trends = gp.ask_model(f"""\
    {race_info}について過去のレース傾向をまとめます。
    また、{dt.year}との差異など留意すべき点があれば指摘します。
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
    • *その他*  
     上記以外の補足事項
    """)
    # 有力馬・危険な馬・穴馬まとめ
    contenders = gp.ask_model(f"""\
    枠や血統、過去の傾向などをもとに{today}時点での{today} {race_info}の有力馬を過去データをもとにあげます。
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
    """)
    # レース傾向予測
    forcasts = gp.ask_model(f"""\
    これまでの情報をもとにレース展開を予想します。
    ただし、以下のフォーマットとします。
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
    """)
    # 馬券
    recommendation = gp.ask_model(f"""\
    これまでを踏まえて、{today} {race_info}において軸となる馬とその馬を軸にした期待値の高い馬券をあげます。
    穴馬がいる場合はしっかりと抑えてリターンが大きくなるようにします。
    ただし、以下のフォーマットとします。
    *🐎 結論馬券*
    • *馬券種類1*  
     単勝や三連複などの馬券種類名と買い目、点数
    • *馬券種類2*  
     単勝や三連複などの馬券種類名と買い目、点数
    • *その他*  
     上記以外の補足事項
    """)
    return {
        "trends": trends,
        "contenders": contenders,
        "forcasts": forcasts,
        "recommendation": recommendation
    }

@app.get("/win5")
async def predict():
    dt = datetime.datetime.today() 
    today = f"{dt.year}年{dt.month}月{dt.day}日(JST)"
    channel = slack_dict["win5"]
    gp = GeminiPredict(api_key=GOOGLE_API_KEY,
                token=SLACK_API_TOKEN,
                channel=channel)
    # 馬券
    recommendation = gp.ask_model(f"""\
    まず、{today}に開催されるWIN5の対象となる5つのレースに関する情報を取得します。
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