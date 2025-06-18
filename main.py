# %%
import os
import certifi
from google import genai
from google.genai.types import GoogleSearch, GenerateContentConfig, Tool, Content, Part, GenerateContentResponse
from dotenv import load_dotenv
from slack_sdk import WebClient

# omajinai
os.environ["SSL_CERT_FILE"] = certifi.where()

# .env読み込み
load_dotenv("./.env")
# API Key
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SLACK_API_TOKEN = os.getenv("SLACK_API_TOKEN")
SLACK_CHANNEL_ID = os.getenv("SLACK_CHANNEL_ID")
# Google検索
search_tool = Tool(google_search = GoogleSearch())
# Client
client = genai.Client(api_key = GOOGLE_API_KEY)
# 会話履歴
history: list[Content] = []


def ask_model(user_prompt: str) -> str:
    """
    Args:
        user_prompt (str): User's prompt
    Returns:
        response.text (str): Gen AI's answer
    """
    history.append(Content(role="user", parts=[Part(text=user_prompt)]))
    response = client.models.generate_content(model="gemini-2.0-flash", 
                                              contents=history,
                                              config=GenerateContentConfig(
                                                tools=[search_tool],
                                                response_modalities=["TEXT"],
                                                )
                                            )
    history.append(Content(role="model", parts=[Part(text=response.text)]))
    return f"{user_prompt}\n\n{response.text}"


def send_slack_message(text: str) -> str:
    """
    Args:
        text (str): text which you want to send Slack
    Returns:
        str
    """
    client = WebClient(token=SLACK_API_TOKEN)
    response = client.chat_postMessage(
        channel=SLACK_CHANNEL_ID,
        text=text
    )
    return response

if __name__ == "__main__":
    print(send_slack_message(ask_model("府中牝馬ステークスについて過去のレース傾向をまとめます。")))
    print(send_slack_message(ask_model("これを踏まえて現時点での2025年の府中牝馬ステークスの有力馬をあげます。")))
