# %%
import os
from google import genai
from google.genai.types import GoogleSearch, GenerateContentConfig, Tool, Content, Part, GenerateContentResponse
from dotenv import load_dotenv

# .env読み込み
load_dotenv("./.env")
# API Key
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
# Google検索
search_tool = Tool(google_search=GoogleSearch())
# Client
client = genai.Client(api_key=GOOGLE_API_KEY)
# 会話履歴
history: list[Content] = []


def ask_model(user_input: str) -> GenerateContentResponse:
    history.append(Content(role="user", parts=[Part(text=user_input)]))
    response = client.models.generate_content(model="gemini-2.0-flash", 
                                              contents=history,
                                              config=GenerateContentConfig(
                                                tools=[search_tool],
                                                response_modalities=["TEXT"],
                                                )
                                            )
    history.append(Content(role="model", parts=[Part(text=response.text)]))
    return response.text


if __name__ == "__main__":
    print(ask_model("2025年の宝塚記念の結果を教えてください"))
    print(ask_model("では、優勝馬の特徴と考えられる勝因について教えてください"))
